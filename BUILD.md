# Building Labirintus3D

The release was compiled with **Lisa Pascal V3.26 (10-Jul-84)**,
**MC68000 Code Generator V3.16** and **M68000 Object Code Linker 3.0**
in Workshop 3 running in LisaEm. Python prepares source and disk images;
the Pascal compiler itself runs on the Lisa.

## Requirements

- Apple Lisa 2 or LisaEm, your own ROM and Workshop 3/LOS 3 environment.
- LOS interface objects referenced by the source, `IOSPASLIB.OBJ`,
  `SYS1LIB.OBJ` and `PRLIB.OBJ`.
- Python 3.10+ for the included tools; standard library only.

ROMs, OS images, SDK libraries and the private development VM are not included.
Use a separate copy of your development disk.

## Source

`src/M.TEXT` is the exact final source compiled for this release. Supporting
units are `G.TEXT`, `J.TEXT`, `D.TEXT` and `I.TEXT`. These TEXT files retain
classic CR line endings. `src/game.pas` contains the Labirintus3D logic and renderer.
Optional regeneration uses the included previous-game application shell:

```sh
python tools/generate_source.py
python tests/test_rules.py
```

The generator does not require a sibling project checkout. Rule tests create `tests/model-validation.json` and legal replay traces.
The original levels are in `src/levels.json`; the model uses its identical `tests/levels.json` copy.

## Compile and link

Transfer the TEXT files into Workshop as Lisa TEXT files, not ordinary raw
files on a floppy. The receiver and serial transfer utility in
[LOS Minesweeper](https://github.com/alexthecat123/los_minesweeper) provide one
transfer method. Set your Workshop prefix to the source folder and make the
LOS interface objects available.

Compile G, J, D, I and then M with Workshop P. Enter the source name, accept
the default listing and object output. The release reused the four verified
support objects and freshly compiled M. Final code generation: **12924 bytes**.

Start **Run (R), LINKER**. Enter these inputs individually:

```text
M.OBJ
G.OBJ
J.OBJ
D.OBJ
I.OBJ
IOSPASLIB.OBJ
SYS1LIB.OBJ
PRLIB.OBJ
```

End inputs with Return, use V.TEXT as the listing and enter **W.OBJ** as
output. Require zero errors and an executable program file. The release
W.OBJ is **15872 bytes**, in the packaged file. `C.TEXT` includes the compiler macro. Enter the linker inputs above explicitly;
the inherited L.TEXT macro is retained as source provenance, not the recommended command.
The release used the corrected `LL.TEXT` via Run: `<LL`.

Quit Workshop with Q, confirm Y and use P (Power_off) in the text system menu.
Wait for shutdown and close LisaEm before inspecting its disk image.

## Package the executable

The included released floppy serves as the template. The packager preserves
tool ID 249, icons, phrase resources and all native Sony sector tags:

```sh
python tools/package.py /path/to/closed-workshop.dc42 Labirintus3D-new.dc42
python tools/inspect_image.py Labirintus3D-new.dc42
```

The Workshop disk must contain `W.OBJ`. The new executable must fit the
template’s allocation; this utility does not allocate larger files or change
resources. Keep all output images separate from the inputs.

## Native validation provenance

The recorded native tests ran LisaEm locally in an Alpine Linux VM under
Windows QEMU. They sent normal COPS keyboard and mouse events and read game
state from emulated RAM without writing board state. The VM, debugger setup,
private disk images and SSH credentials are not redistributed. The included
Python rule model and test suite can be run without this VM. Native reports
and screenshots document the release test, rather than offering a portable
one-command native test environment.
