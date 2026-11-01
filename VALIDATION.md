# Validation

The reports in [validation/](validation/) record the released DC42, SHA-256
`d95b32c3e84ca054dbaab8714d7386cb5b6e20d247b7528b332506974ad1d8d1`.

- Lisa Pascal 3.26 / MC68000 Code Generator 3.16 / Linker 3.0: zero errors.
- Independent model: 69359 checks, three complete legal routes.
- Stock Linux LisaEm, LOS 3.1, 1 MB, 5 MHz target: 345 native checks in
  input, levels, map, render and video stages. All three levels completed.
- 80 idle and 80 turning frames; unchanged map pixels outside the player
  region stayed identical. Screenshots use normal X11 full refresh.
- Native LOS Duplicate/drag installation, floppy eject, hard-disk launch
  and actual Right key input: four observed checks. Closed-disk executable
  readback matched the release; 20 previous tool IDs / 77 payloads were preserved.
- Publication checks regenerate exact Pascal source, run the standalone
  model and compare the distributed floppy with the tested local/NAS release.

The native tests used real emulated COPS/X11 input and read-only game telemetry;
they did not write game state. The private VM/OS/debugger setup is not included,
so historical native reports are not a portable one-command test harness.
Physical Lisa 2, Windows LisaEm and separate LOS 3.0 tests were not performed.

[Hungarian detailed report](VALIDATION-HU.md).


## 1.0.1 keyboard-control update

The WASD input handler compiled with Lisa Pascal 3.26 and linked with zero errors using M68000 Linker 3.0. DC42 validation passed: 419,284 bytes, tool ID 249, volume suffix D60A, 800 native tags, and three matching icon resources. The updated key events were not separately exercised in a physical Lisa or in-game runtime session; this release does not claim that verification.
