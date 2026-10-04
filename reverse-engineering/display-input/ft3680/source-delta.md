# FT3680 source lineage and GQ5012BF1 deltas

## Closest donor

The closest proven public source remains:

- repository: `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`
- commit: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- subject: `Merge codes for CMF by Nothing Phone 1 Nothing OS 2.6(Tetris-U2.6-241204-2338)`
- path: `drivers/input/touchscreen/FT3519/`
- donor tree: `f074a8ccb6d1785721946ee71c3e2a0ef149a9ee`
- banner: FocalTech V4.1 20230424

The shipped module is V4.2 20240407. Searches of local BSPs, NothingOSS history, public FocalTech repositories, Sourcegraph/GitHub candidates and other MT6878 trees found no exact V4.2/FT3680 source. Full search notes are in `workspace/phase4-focaltech-ft3680/source-candidates.md`.

## Recovered stock configuration

The source under `Reverse Engineer - PARTIAL/FT3680-TOUCH/source/` removes donor-only production-test, proximity, panel-event export, FOD, game/pocket and unrelated flash-backend code and enables the stock SPI, gesture, point-report-check, ESD, FHP, firmware-debug and upgrade paths.

Major GQ5012BF1/V4.2 deltas recovered from the binary include:

- FT3680 type/ID tuple and 18-record upgrade-setting table.
- SPI-v2 framing, CRC-16/Kermit checking, retry/timing constants and direct-transfer ABI.
- YFT registration/version/gesture-provider calls with all stock modversion CRCs.
- MediaTek display notifier label `Touch_fts`, asynchronous resume work, AOD gate and `tpgesture_status` policy.
- `vddi-gpio` + optional `iovcc` naming, 3.3 V VDD control and Ulefone power strings.
- FHP `fhp_ft`/`fhp_input` ABI and firmware-debug proc protocol.
- Embedded non-const `fw_file`, request-firmware fallback and FT3680 PRAM/DRAM download engine.
- Exact sysfs object names `fts_earphone_mode`, `fts_edgepalm_mode` and `fts_esdcheck_group`.

## Recovered `fts_ts_data` layout

Binary offset correlation plus rebuilt parity established the stock-visible layout. Important anchors are:

| member | stock offset |
|---|---:|
| extra 8-byte slot after `spi` | `0x10` |
| `dev` / `input_dev` / `pdata` | `0x18` / `0x20` / `0x30` |
| `ts_workqueue` | `0x58` |
| `resume_work` | `0x60` |
| `ts_waitqueue` | `0x228` |
| `irq` / `suspended` | `0x2f8` / `0x308` |
| ESD support flag | `0x315` |
| gesture flag/mode | `0x31a` / `0x31b` |
| `touch_size` | `0x478` |
| VDD / optional IOVCC | `0x4e0` / `0x4e8` |
| display notifier | `0x4f0` |
| structure end | `0x508` |

The donor's unused per-device `fwupg_work` occupied the stock `resume_work` slot. Donor-only `fod_info`, FOD paths, game mode and pocket mode were removed. This change alone moved raw byte-identical functions from 23 to 65 before later fixes.

## Additional behavior corrections in this pass

- Corrected display suspend/resume, IRQ-wake, reset and normal-firmware recovery order.
- Reconstructed the gesture D0 gate, appended-buffer validity checks and D3 fallback.
- Reconstructed firmware-reset detection (`EF` markers), state recovery and IRQ event dispatch.
- Recovered V4.2 readiness polling and HID-to-standard-I2C helper behavior.
- Restored mutex-protected ex-mode sysfs semantics.
- Restored complete probe failure unwinding and stock-visible data sections/names.
- Corrected `fts_read()` so a NULL/zero-length command is legal while data/datalen remain mandatory.

## Known deliberate boundary

The proprietary 118,972-byte firmware include is present only in the private parity harness. It is not copied into the research repository or publishable source bundle. The private harness compiles the stock programming branches for static comparison; no module was loaded and no controller command was executed.

## Residual source uncertainty

The function set is exact (166/166) and the static interfaces are reconstructed, but 40 functions still differ in compiled size and 68 functions are not classified as normalized-identical/order-only. Residuals cluster in compiler/inlining shape, FHP/FWDBG queue code, flash helper call boundaries, IRQ dispatcher source shape and cleanup ordering. There is no surviving V4.2 source to distinguish every source spelling that produces equivalent control flow.

Therefore this source is behaviorally advanced and buildable but is not claimed byte-exact or uniquely source-exact.
