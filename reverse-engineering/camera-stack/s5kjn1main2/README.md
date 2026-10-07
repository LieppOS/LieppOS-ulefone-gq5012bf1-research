# CAMERA-S5KJN1MAIN2 — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/CAMERA-S5KJN1MAIN2` → **DONE**.
Earlier material: `../notes/s5kjn1-family.md`, `../stock-imgsensor-oracle/`,
`../reconstruction/imgsensor/` (`tools/mk_s5kjn1.py`), `../donor-comparisons/`.

## Selection log

SELECTED TARGET: `CAMERA-S5KJN1MAIN2`. VERIFIED: present in `Reverse Engineer - PARTIAL/`,
and `REVERSE-ENGINEERING-STATUS.md` lists it as PARTIAL.

WHY: one sub-driver TU in the same imgsensor rebuild tree that closed `CAMERA-OV64B`.
The whole-module comparison against the shipped module already exists. Its EEPROM
item belongs to `CAMERA-EEPROMS` (DONE 2026-10-06), and its AF item belongs to
`CAMERA-VCMS` (DONE).

CURRENT BLOCKERS (as recorded): (1) "C source for the TU (data complete)";
(2) "tuning proprietary"; (3) "EEPROM layout in CAMERA-EEPROMS".

## Scope

The `s5kjn1main2_mipi_raw` sub-driver (TU `common/s5kjn1main2_mipi_raw/s5kjn1main2mipiraw_Sensor.c`)
inside the stock `imgsensor.ko`. This covers identity probe, static context,
mode table, register payload, power sequence, frame descriptors, PDAF block
info, the 4-cell EEPROM read and the CTS gate. It also covers DT/bus/power
binding and the HAL exposure of camera 2.

Outside scope:
* ISP tuning and 3A (`s5kjn1main2_mipi_raw_tuning.so`, `_IdxMgr.so`, tuning DB) and the HAL 4-cell remosaic → `CAMERA-HAL-ISP`.
* EEPROM `2-0050` layout and the cam_cal driver → `CAMERA-EEPROMS`.
* `main4_vcm` → `CAMERA-VCMS`.
* `is_yft_cts_board()` → `YFT-DEVINFO`.

## Result

| item | result |
|---|---|
| lineage | **BINARY-EQUIVALENT RECONSTRUCTION**. No public `s5kjn1main2` source exists (GitHub code search: 0 hits). The C was reconstructed from the stock binary on the MTK `static_ctx` sub-driver skeleton. Its stock data is regenerated verbatim (`s5kjn1main2_stock_data.h`). The nearest public JN1 donors are Xiaomi zircon `bailus5kjn1` (preview: same address sequence, 5 values differ) and NothingOSS mt6886 `s5kjn1` (all 30 init pairs are inside the 37-write stock init). |
| B1 == B2 | stripped `.ko`, unstripped `.ko` and `s5kjn1main2mipiraw_Sensor.o` byte-identical (`parity/b1-b2-build.txt`) |
| A (shipped `imgsensor.ko` `9243061c…`) vs B1 | same size; 70 differing bytes = 20 build-id + 50 in `yft_ctrl_nightled_by_idx`. That function is idx-4 only and mechanically proven equivalent (`../ov64b/evidence/nightled-equivalence.txt`). None of the 70 bytes is in this TU. |
| S5KJN1MAIN2 TU | **32/32 symbols identical in the shipped module**: 11 functions (incl. `read_4cell_from_eeprom`, `s5kjn1main2_seamless_switch`, `set_sensor_cali`) and 21 data objects (`static_ctx`, `mode_struct` 2 200 B, `imgsensor_pd_info` 932 B, `eeprom_info`, 481-entry gain table, 5 register tables, 5 frame descriptors, `pw_seq`, `.bss` 4-cell cache). Same-named statics shared with other JN1 TUs are pinned by the relocations of this TU's uniquely matched functions (`parity/s5kjn1main2-tu-parity.tsv`). |
| module-wide | functions 620/621, data 416/416, KCFI 621/621, `__versions`, `.modinfo`/vermagic, imports 131/131, exports, 65 section headers, 2 857 ordered symbols: identical |

## Interface (stock)

* DT `i2c@11c22000` (i2c-2) `sensor2@10`, `reg = <0x10>` → bus client `2-0010`
  (bound to `imgsensor`, `of:Nsensor2`). `sensor-names = "s5kjn1main2_mipi_raw"`;
  no `reindex-to`, so `ctx->idx = 2`. Endpoint → seninf csi-port-1, D-PHY 4-lane.
  MCLK `CAMTG4` 24 MHz, 4 mA drive. `#thermal-sensor-cells` (sensor temperature).
* Sub-driver I2C: write-ID **0x5A** (7-bit 0x2D). 16-bit registers,
  burst-write. Chip-ID regs 0x0000/0x0001.
* **Probe:** reads both bytes in both orders per retry and adds **1 to the
  low byte**, so a JN1 die reporting 0x38E1 matches **0x38E2**. It binds only
  if `!is_yft_cts_board()`. The pseudo-ID is a driver convention that gives
  two identical JN1 dies distinct HAL identities (tuning, lens table
  0x38E2 → `main4_vcm`, cam_cal config 0x38E2). It is not silicon.
* **Power (`pw_seq`, 10 steps):** PDN0 → DOVDD 1.8 (+3 ms) → DVDD 1.2 (+1) →
  AVDD 2.8 → AVDD1 1.8 (+2; `avdd1-supply`, GPIO76 `camera2-common-avdd1`) →
  RST1 (+2) → AFVDD 2.8 (+1) → MCLK 4 mA → MCLK 24 MHz (+2) → PDN1 (+1).
  The custom-LDO channels are dvdd 1, avdd 4, afvdd 6, dovdd 7 (WL2864C).
* `static_ctx`: output format 35 = `RAW_4CELL_BAYER_Gr` (Tetra-cell), 4 lanes,
  OB 64. Analog gain 1×–16× in 481 steps (`ana_gain_type 2`). Exposure 3–65532
  (margin 3). FL max 65535. Registers: stream 0x0100, mirror/flip 0x0101,
  exposure 0x0202/03, gain 0x0204/05, FL 0x0340/41, group hold 0x0104, test
  pattern 0x0600–0x0608. `pdaf_type CAMSV`.
* **Modes (5):**
  * preview and normal_video 4080×3072@30 (pclk 560 MHz, LL 5894, FL 3168). Preview carries the PD VC (DT 0x30, 640×3056) with `pdaf_cap = 1`.
  * capture 8160×6144@10 (full remosaic, LL 8688, FL 6400).
  * hs_video and slim_video carry IMX989 timings (pclk 4.39/4.35 GHz, 120/240 fps) with a 74-pair table. These are ODM placeholders the HAL never selects. The stock frame descriptors say 1920×1080 / 640×480 while the TG is 4080×3072. The `corrected` build fixes this (data only).
* **Feature list (4):** test pattern, test-pattern data, seamless switch,
  `GET_4CELL_DATA`.

## GQ5012BF1 behaviour (`evidence/integration-checks.txt`, 23/23 PASS)

* **ACTIVE.** `2-0010` is bound, and the HAL exposes
  `[02] BACK SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW`, so the +1 chip-ID match
  succeeded (the die answered 0x38E1 at 0x2D) and `is_yft_cts_board()` = 0.
  The HAL treats it as the 16 mm ultrawide: 4080×3072 RAW, 8192×6144 BLOB.
* **4-cell calibration is live.** `read_4cell_from_eeprom` is reached via
  `VIDIOC_MTK_G_4CELL_DATA` → `SENSOR_FEATURE_GET_4CELL_DATA`. On the first
  call it reads the module EEPROM through the sensor's own adapter (i2c-2,
  0x50 = `2-0050`, the same chip `camera_eeprom_v4l2` binds) and caches
  9490 B plus a 2-byte length:
  * XTC 0x0D4F (3502 B);
  * sensor XTC 0x1AFD (768 B);
  * PDXTC 0x1DFD (4000 B);
  * SW-GGC 0x2D9D (626 B).

  The regions end exactly at the QSC base 0x300F, inside the 0x4000 EEPROM.
  HAL consumers are present: `libmtkcam_hwutils.so`
  `FOUR_CELL_CAL_TYPE_{GAIN_TBL,DPC,FD_DPC}`, the capture featurepipe
  "remosaic to bayer by 3rdParty", and `PipelineModelSession4Cell`.
* **QSC is NOT applied (dead in stock).** `eeprom_info` sets no `*_support`
  flag, so `preload_eeprom_data` → `read_sensor_Cali` only matches the header
  0x77006901 and preloads nothing. `set_sensor_cali` (the `s_cali` hook) is
  called only from `common_open`, and this TU installs its own `open()`, so it
  never runs. It would be a no-op anyway (`qsc_support = 0`).
* **Seamless switch is inert.** No mode has a `seamless_switch_group`, so
  `s5kjn1main2_seamless_switch` always logs "not supported" and returns
  before any I2C write.
* No slot-specific framework hook. The only idx-specific code is the idx-4
  night-LED (OV64B). Framework-wide YFT hooks apply as they do to every camera:
  HV charging suspended on subdev open, and `yft_camera_device_add` at probe.

## Stock defects (reproduced by the parity build; LieppOS decision)

1. **Kernel heap overflow (userspace-sized buffer).** `g_4cell_data` allocates
   `info->size` bytes chosen by the caller. `read_4cell_from_eeprom` then
   always `memcpy`s 9492 bytes into that buffer. Any caller with access to the
   subdev node that passes `size < 9492` overflows the kernel heap. In stock,
   access is limited to the camera HAL by node permissions and SELinux.
   Suggested hardening (behaviour change, breaks parity): clamp the copy to the
   work-buffer size, or reject a smaller `size`.
2. EEPROM read return values are ignored, and `Is_Read_4Cell` is latched
   anyway. A transient I2C failure therefore caches partial or zeroed 4-cell
   data until reboot.
3. `*data` is dereferenced before its NULL check. This is harmless on the
   ioctl path, because the work buffer is non-NULL.
4. hs/slim placeholder modes (see above).

## Boundaries (external)

* Tuning, 3A, the 4-cell remosaic (third party) and the BLOB upscale:
  proprietary userspace (`CAMERA-HAL-ISP`).
* EEPROM layout and cam_cal parsing (`CAMERA-EEPROMS`, DONE): header
  0x77006901, AWB/LSC/AF/PDAF offsets, config sensor 0x38E2.
* AF actuator `main4_vcm`: DT `2-000d` is a placeholder; the wire address is
  0x0C (`CAMERA-VCMS`, DONE).
* `is_yft_cts_board()` implementation (`YFT-DEVINFO`). The import CRC is
  identical.

## LieppOS contract

Build `imgsensor.ko` with `../reconstruction/imgsensor/build/build.sh … parity`
(or `scripts/build_b1_b2.sh`). The result is a drop-in for stock. Keep `2-0050`
readable by both `camera_eeprom_v4l2` and imgsensor. The cam_cal driver
preloads 0x4000 bytes, and imgsensor re-reads the 4-cell windows itself.
Do not "fix" the +1 pseudo-ID: the HAL tuning, lens and cam_cal tables are keyed
on 0x38E2. Consider defect 1 (hardening) for any build that does not need
byte parity.

## Runtime-only validation (not performed)

Streaming camera 2, checking the full-size remosaic capture with the 4-cell
data, and verifying PDAF. These validate the contract above.

## Files

* `scripts/build_b1_b2.sh`, `scripts/s5kjn1main2_parity.py` (adds NOBITS
  zero-fill and relocation-pinned disambiguation of same-named statics),
  `scripts/s5kjn1main2_integration.py`.
* `parity/{b1-b2-build.txt, s5kjn1main2-parity.txt, s5kjn1main2-parity.tsv, s5kjn1main2-tu-parity.tsv}`.
* `evidence/{integration-checks.txt, stock-module-identity.txt}`; `stale-claims.md`.
