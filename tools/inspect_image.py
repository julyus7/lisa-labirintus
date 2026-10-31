"""Inspect the release's DC42 checksums, identity, executable and icon payloads."""
import argparse
import hashlib
from pathlib import Path
from lisa_image import LisaImage

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('image', nargs='?', type=Path,
               default=Path(__file__).resolve().parent.parent/'dist'/'Labirintus3D.dc42')
a = p.parse_args()
im = LisaImage(a.image)
im.verify_checksums()
if set(im.tools()) != {249}:
    raise ValueError('Unexpected LOS tool identity')
icons = [im.read(n) for n in ('{T249}ICON', '{T249}ICON.BACKUP', '{t249}icon2')]
if len(icons[0]) != 814 or not all(x == icons[0] for x in icons):
    raise ValueError('Missing or mismatched native icons')
code = im.read(im.tools()[249])
print('DC42 checksums: valid; LOS tool:', 249)
print('Executable bytes:', len(code), 'SHA256:', hashlib.sha256(code).hexdigest())
print('Image SHA256:', hashlib.sha256(im.b).hexdigest())
print('All three native icon files agree.')
