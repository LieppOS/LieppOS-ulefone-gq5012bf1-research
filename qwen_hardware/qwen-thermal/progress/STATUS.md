# Status

Static/offline investigation complete for the available corpus. Completed: artifact inventory/hashes, all three APK decompilations, native exports/strings, yft/extcon kernel RE, power/ID path, UVC/vdcmd architecture, radiometric representation, FFC/NUC/ISP/palettes, calibration paths/status, donor comparison, reconstructed API and LieppOS design.

Highest-confidence new facts: expected sensor/front-end ID `0x4c59`; two-node power+USB routing; FactoryMode 256x384@25 YUYV+temp test mode; uint16 LE 1/64 K radiometry; >=192-byte per-unit calibration status record with byte-0 flag.

Remaining work requires a powered device, passive descriptors/frame capture, native decompiler or controlled reference-temperature testing. See `findings/unresolved.md`.

Parent (module-family) finding, separate from the FLIR/AC020 path: `aw36518.ko` and
`aw36518_v2.ko` are the same source with one config difference — identical function
sets, one structurally differing function (`parse_dt`, 364→296 B, the removed
`is_yft_cts_board()` CTS-board branch and the `yft_devinfo` dependency), so the v1
reconstruction covers both; `aw36515.ko` is an alternate two-channel topology with a
shared `set_ctrl` helper and its own V4L2 subdev registration and needs its own pass.
All three stay unloadable (`flashlight`, `yft_devinfo` absent), so none of them is the
camera thermal-sensor path. Every number is re-measurable with
`python3 tools/ko-family-delta.py --self-test` (from `qwen_hardware/qwen-thermal/`),
which prints `SELF_TEST: PASS` after 10 golden invariants over the three frozen stock
modules — function sets, import delta, `.data`/`.rodata` byte comparison, the
`parse_dt` call multiset and the `modinfo depends` delta. Full write-up:
`findings/aw36518-family-structural-delta.md`.
