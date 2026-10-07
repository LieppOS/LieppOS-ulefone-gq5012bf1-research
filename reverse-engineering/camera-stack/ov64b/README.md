# CAMERA-OV64B — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/CAMERA-OV64B` → **DONE**.
Earlier material: `../notes/ov64b.md`, `../stock-imgsensor-oracle/`,
`../reconstruction/imgsensor/`, workspace pack `notes/source-donor-analysis.md`.

## Selection log

SELECTED TARGET: `CAMERA-OV64B`. VERIFIED: present in `Reverse Engineer - PARTIAL/`,
and `REVERSE-ENGINEERING-STATUS.md` lists it as PARTIAL.

WHY: it is one sub-driver TU inside one module. The stock binary, the donor
lineage and a reconstruction tree that builds were all already local. The
recorded blockers ("source for stock register revision; tuning") turned out to
be stale labels, not open RE questions (see "Original blockers").

CURRENT BLOCKERS (as recorded): (1) "no source for the stock register revision
(data complete)"; (2) "dropped seamless/QSC behaviour documented"; (3) "tuning
proprietary". Implicit: (4) a 2026-10-03 note in camera-stack `STATUS.md`
re-labelled every module-wide imgsensor result as "our build vs our build" and
said shipped-module parity was proven only for IMX989.

## Scope

The OV64B sub-driver (`ov64b_mipi_raw`, TU `common/ov64b_mipi_raw/ov64bmipiraw_Sensor.c`)
inside the stock `imgsensor.ko`. This covers identity probe, static context,
mode table, register payload, power sequence, frame descriptors and
CTS gating. It also covers the framework behaviour the shipped module applies
only to this sensor slot: the sensor4 night-LED hook in `adaptor-ctrls.c`.
Plus DT/bus/power binding and HAL exposure. Outside: ISP tuning and the 3A
userspace (`CAMERA-HAL-ISP`); the flashlight core and the AW36518 LED drivers
(`flashlight.ko` / `AW36518*-FLASH`); the module EEPROM (`CAMERA-EEPROMS`); the
VCM (`CAMERA-VCMS`); OIS (`DW9781C-OIS`).

## Result

| item | result |
|---|---|
| lineage | **BINARY-EQUIVALENT RECONSTRUCTION**: NothingOSS MT6878 `ov64b_mipi_raw` (older register revision) + ODM code edits (3-byte ID probe with `is_yft_cts_board()` gate, write-IDs 0x20/0x44, QSC/seamless removed, `init_ctx` logging) + stock register/mode data regenerated verbatim (`ov64b_stock_data.h`) |
| B1 == B2 | stripped `.ko`, unstripped `.ko` and `ov64bmipiraw_Sensor.o` byte-identical (`scripts/build_b1_b2.sh`) |
| A (shipped `imgsensor.ko` `9243061c…`, 1 140 880 B) vs B1 | same size; **70 differing bytes** = 20 build-id + 49 `.text` and 1 `.rela.text` byte(s), all inside `yft_ctrl_nightled_by_idx` (`parity/ov64b-parity.txt`) |
| OV64B TU | **27/27 symbols identical in the shipped module** (9 functions, 18 data objects: `static_ctx`, `mode_struct` 2 200 B, `pw_seq`, 6 register tables incl. 11 224 B init, 5 frame descriptors, gain table, ops, feature list, entry) (`parity/ov64b-tu-parity.tsv`) |
| module-wide | functions 620/621 (size, bytes, symbolic relocs, KCFI); data 416/416; KCFI 621/621; `__versions` 8 448 B, `.modinfo`, `__ksymtab*`, `.rodata.str1.1`, `.llvm_addrsig`, 65 section headers, 2 857 ordered symbols identical; imports 131/131; exports `fs_sync_frame`; relocations 15 486/15 487 |
| vermagic / srcversion | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` / absent on both |
| only differing function | `yft_ctrl_nightled_by_idx` (static, address never taken, 2 callers passing constant 0 and 1): **mechanically equivalent**. Both binaries were interpreted over every input; traces (calls, arguments, final LED state) are identical for state ∈ {0,1}. They differ only for state ∉ {0,1}, which no caller passes (`evidence/nightled-equivalence.txt`). Cause: register allocation and value-range narrowing in clang. |

So the shipped OV64B code and data are reproduced exactly. The single
framework residual that touches this sensor slot has no behavioural effect.

## Interface (stock)

* DT `i2c@11c23000` (i2c-4) `sensor4@10`, `reg = <0x20>` → bus client
  `4-0020` (bound to `imgsensor`, capture `buses.txt`); `sensor-names =
  "ov64b_mipi_raw"`; endpoint → `seninf-csi-port-0` (D-PHY 4-lane); MCLK
  `CAMTG2` (shared selector with sensor1) 24 MHz, 8 mA drive.
* Sub-driver I2C: write-IDs **0x20 → 0x44** (7-bit 0x10, 0x22); chip ID
  regs 0x300A/0x300B/0x300C = **0x566442**; probe gated by `is_yft_cts_board()`
  (yft_devinfo; returns 0 on this unit, otherwise no camera 3).
* Power (`pw_seq`, custom-LDO WL2864C channels avdd 4, afvdd 5, dvdd 1,
  dovdd 7): MCLK 24 → PDN0 → RST0 → AVDD 2.8 → AFVDD 2.8 → DVDD 1.1 →
  DOVDD 1.8 → MCLK 8 mA → PDN1 → RST1. No OIS step. The `oisen` pinctrl
  (GPIO3) is never selected.
* 5 modes: preview/capture/normal_video 4624×3472@30, pclk 115.2 MHz, LL 1056,
  FL 3636; hs/slim 1920×1080@120, LL 600, FL 1600. Control registers:
  exposure 0x3500-02, gain 0x3508/09, FL 0x380E/0F (+0x3840), stream 0x0100,
  temperature 0x4D13. PDAF type CAMSV but no mode has `pdaf_cap`. EEPROM QSC
  disabled (`eeprom_num 0`).
* Known stock defect (reproduced, not fixed by the parity build): hs/slim
  frame descriptors say 4624×2604 while the tables program 1920×1080. The
  `corrected` build fixes this as a data-only change.

## GQ5012BF1 behaviour

* **ACTIVE / physically present.** `search_sensor()` powers the slot, runs
  `init_ctx` and the I2C chip-ID read, and binds only on a match. `4-0020` is
  bound and the HAL exposes `[03] BACK SENSOR_DRVNAME_OV64B_MIPI_RAW`
  (`hasFlashUnit 1`), so 0x566442 answered on i2c-4.
* **Night-vision IR LEDs follow this camera.** `ctx->idx` is the DT index of
  `sensor4` (no `reindex-to`). On `V4L2_CID_MTK_SENSOR_INIT` val≠0,
  `yft_ctrl_nightled_by_idx(ctx,1)` calls `flashlight_drvctrl(1)` and `(11)`.
  On `V4L2_CID_MTK_SENSOR_POWER` val=0 it calls `(0)` and `(10)`; a static
  `nightled_is_open` suppresses repeats. In stock `flashlight.ko`, cmd 1/0
  selects the flashlight device {type 0, ct 0, part 1} = `aw36518@63`
  (`8-0063`), and cmd 11/10 selects {type 0, ct 1, part 1} = `aw36518_v2`
  (`12-0063`). "On" is `open` → `set_driver(1)` → `fl_enable(1)`; "off" is
  `fl_enable(0)` → `set_driver(0)` → `release`. The normal rear flash is
  `aw36515` (part 0, `6-0063`).
  So every stock stream on camera 3 lights the IR array. There is no
  separate user control in the kernel path.
* HAL: camera 3 publishes 4624×3472 RAW and a 9216×6912 BLOB size, but no
  full-array 9248×6944 kernel mode exists, so that BLOB is produced in the
  HAL. `availableOisModes = 6` (no provider; see DW9781C-OIS).
  `availableOpticalStabilization = [0]`. Tuning: `ov64b_mipi_raw_tuning.so`,
  `ISP_param.db`.

## Board / ODM deltas versus donor

Stock vs NothingOSS MT6878 `ov64b_mipi_raw`: 79/87 `static_ctx` fields equal.
Output format 37→3; modes 12→5; EEPROM QSC removed; `ov64b_seamless_switch`
dropped; `init_ctx` 92→160 B. Init table 2806 vs 2802 pairs, 847 differing
values plus stock-only 0x0103/0x0303/0x0343/0x3624. All mode tables are new.
Write-ID 0x20 is added before 0x44, the CTS gate is added, and the donor
OISVDD/OISEN pw_seq steps are removed. Framework side: the YFT night-LED hook
for idx 4.

## Boundaries (external)

* ISP tuning, 3A, MFNR/remosaic and the BLOB upscale path: proprietary
  userspace (`CAMERA-HAL-ISP`).
* LED current, duty and AW36518 register behaviour: `flashlight.ko` core and
  the DONE `AW36518-FLASH` / `AW36518-V2-FLASH`. This component closes only
  the trigger contract.
* `is_yft_cts_board()` / `yft_camera_device_add()` implementation
  (`YFT-DEVINFO`). The import CRCs are identical, and the call contract is used
  as-is.
* Module EEPROM `4-0051` (`CAMERA-EEPROMS`), VCM `main2_vcm` (`CAMERA-VCMS`),
  OIS (`DW9781C-OIS`).

## LieppOS contract

Build `imgsensor.ko` with `../reconstruction/imgsensor/build/build.sh … parity`
(or `scripts/build_b1_b2.sh`). The result is a drop-in for stock. Load
dependencies are unchanged (`imgsensor-glue`, `custom-ldo(-wl2868)`,
`yft_devinfo`, `flashlight`, `mtk_ccuv`, power-budget modules). Expect the IR
LEDs to come on whenever camera 3 is initialised. If LieppOS wants a
visible-light-only mode for this camera, it must change
`yft_ctrl_nightled_by_idx` (a new feature, not a stock behaviour). The
`corrected` build fixes the hs/slim frame-descriptor defect, at the cost of
stock parity.

## Runtime-only validation (not performed)

Streaming camera 3 and observing the IR array, and per-mode image
verification. Both are validation of the contract above.

## Files

`scripts/build_b1_b2.sh`, `scripts/ov64b_parity.py`, `scripts/nightled_equivalence.py`;
`parity/{b1-b2-build.txt, ov64b-parity.txt, ov64b-parity.tsv, ov64b-tu-parity.tsv}`;
`evidence/{nightled-equivalence.txt, stock-module-identity.txt}`; `stale-claims.md`.
