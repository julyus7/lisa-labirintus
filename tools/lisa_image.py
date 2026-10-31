"""Read tagged Lisa DC42 images; preserve native page-chain tags when writing."""
from pathlib import Path
import hashlib
import re
import struct


def checksum(data):
    value = 0
    for i in range(0, len(data), 2):
        value = (value + int.from_bytes(data[i:i+2], 'big')) & 0xffffffff
        value = (value >> 1) | ((value & 1) << 31)
    return value


class LisaImage:
    def __init__(self, path):
        self.path = Path(path)
        self.b = bytearray(self.path.read_bytes())
        self.ds, self.ts = struct.unpack_from('>II', self.b, 64)
        if self.ds % 512 or len(self.b) != 84 + self.ds + self.ts:
            raise ValueError('Invalid DC42 lengths')
        self.count = self.ds // 512
        self.tl = self.ts // self.count
        if self.tl not in (12, 20) or self.ts != self.count*self.tl:
            raise ValueError('Expected native Lisa tags')
        self.tags = [struct.unpack_from('>H', self.b, 84+self.ds+s*self.tl+4)[0]
                     for s in range(self.count)]
        self.base = self.tags.index(1)
        self.files = {}
        for s, tag in enumerate(self.tags):
            if not 32768 < tag < 65535:
                continue
            inode = self.b[84+s*512:84+(s+1)*512]
            if 0 < inode[0] <= 32:
                name = inode[1:1+inode[0]].decode('mac_roman')
                self.files[name] = ((-tag)&65535, s)
        self.catalog_sectors = [s for s, tag in enumerate(self.tags) if tag == 4]
        self.catalog_sectors.sort(key=lambda s: struct.unpack_from(
            '>H', self.b, 84+self.ds+s*self.tl+6)[0])
        self.catalog = bytearray(b''.join(self.sector(s) for s in self.catalog_sectors))
        self.records = {}
        for off in range(len(self.catalog)-59):
            if self.catalog[off] != 36:
                continue
            name = self.catalog[off+3:off+35].split(b'\0', 1)[0].decode('mac_roman')
            fid = struct.unpack_from('>H', self.catalog, off+38)[0]
            if name in self.files and self.files[name][0] == fid:
                self.records[name] = off

    def sector(self, s):
        return self.b[84+s*512:84+(s+1)*512]

    def sectors(self, name):
        fid, s = self.files[name]
        inode = self.sector(s)
        sectors = []
        for i in range(struct.unpack_from('>H', inode, 0x86)[0]):
            start = self.base + struct.unpack_from('>I', inode, 0x88+6*i)[0]
            length = struct.unpack_from('>H', inode, 0x8c+6*i)[0]
            sectors.extend(range(start, start+length))
        if any(s >= self.count or self.tags[s] != fid for s in sectors):
            raise ValueError('File extent does not match native tags: '+name)
        return sectors

    def read(self, name):
        size = struct.unpack_from('>I', self.catalog, self.records[name]+48)[0]
        return bytes(b''.join(self.sector(s) for s in self.sectors(name))[:size])

    def replace(self, name, payload):
        fid, _ = self.files[name]
        sectors = self.sectors(name)
        if len(payload) > len(sectors)*512:
            raise ValueError('New file exceeds existing allocation: '+name)
        padded = payload.ljust(len(sectors)*512, b'\0')
        for i, s in enumerate(sectors):
            self.b[84+s*512:84+(s+1)*512] = padded[i*512:(i+1)*512]
        struct.pack_into('>I', self.catalog, self.records[name]+48, len(payload))
        for i, s in enumerate(self.catalog_sectors):
            self.b[84+s*512:84+(s+1)*512] = self.catalog[i*512:(i+1)*512]
        slist = [s for s, tag in enumerate(self.tags) if tag == 3]
        struct.pack_into('>I', self.b, 84+slist[fid//36]*512+(fid%36)*14+8, len(payload))

    def verify_checksums(self):
        actual = (checksum(self.b[84:84+self.ds]),
                  checksum(self.b[84+self.ds+self.tl:]))
        if actual != struct.unpack_from('>II', self.b, 72):
            raise ValueError('DC42 checksum mismatch')

    def save(self, path):
        struct.pack_into('>II', self.b, 72, checksum(self.b[84:84+self.ds]),
                         checksum(self.b[84+self.ds+self.tl:]))
        Path(path).write_bytes(self.b)

    def tools(self):
        return {int(m[1]): name for name in self.files
                if (m := re.fullmatch(r'\{T(\d+)\}(?i:obj)', name))}
