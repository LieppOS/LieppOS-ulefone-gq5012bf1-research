# CAMERA-S5KJN1 — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/CAMERA-S5KJN1` → **DONE**.
Earlier material: `../notes/s5kjn1-family.md`, `../stock-imgsensor-oracle/`,
`../reconstruction/imgsensor/` (`tools/mk_s5kjn1.py`), `../donor-comparisons/`.

## Selection log

SELECTED TARGET: `CAMERA-S5KJN1`. VERIFIED: present in `Reverse Engineer - PARTIAL/`,
and `REVERSE-ENGINEERING-STATUS.md` lists it as PARTIAL.

WHY: this is the last sensor slot in the imgsensor rebuild tree. The build, the
shipped-module comparison and the night-LED proof are all reusable. The added
scope is the slot's two alternate sub-drivers.

CURRENT BLOCKERS (as recorded): (1) "C source for the stock TU (data complete)";
(2) "hs/slim modes are IMX989 placeholders"; (3) "tuning proprietary".

## Scope

The camera-1 slot: DT `sensor1` with `sensor-names = s5kjn1, ov32b40, s5kjn1cts`.
It covers the three sub-driver TUs compiled into the stock `imgsensor.ko`:

* `s5kjn1_mipi_raw` (the populated die);
* `ov32b40_mipi_raw` (alternate-BOM die);
* `s5kjn1cts_mipi_raw` (CTS-board variant).

Covered for each: probe and selection, static context, modes, register payload,
power sequence, frame descriptors, stream control and the 4-cell EEPROM read.
Also covered: DT/bus/power binding and the HAL exposure of camera 1.

Outside scope:
* Tuning and 3A (`s5kjn1*_mipi_raw_tuning.so`, `_IdxMgr.so`, tuning DB) and
  the HAL remosaic → `CAMERA-HAL-ISP`.
* EEPROM `4-0050` layout → `CAMERA-EEPROMS`.
* `is_yft_cts_board()` → `YFT-DEVINFO`.

## Result

| item | result |
|---|---|
| lineage | **BINARY-EQUIVALENT RECONSTRUCTION** for all three. No public `s5kjn1`/`s5kjn1cts` source matches. The C was rebuilt on the MTK `static_ctx` skeleton with stock data regenerated verbatim. The nearest JN1 donors are Xiaomi zircon `bailus5kjn1` (preview: same address sequence, 5 values differ) and NothingOSS mt6886 `s5kjn1` (its 30 init pairs are inside the 37-write stock init). `ov32b40` is an MTK template driver (`set_ctrl_locker` from `s5k3p9sp`). |
| B1 == B2 | stripped `.ko`, unstripped `.ko` and all three TU objects byte-identical (`parity/b1-b2-build.txt`) |
| A (shipped `imgsensor.ko` `9243061c…`) vs B1 | same size. 70 differing bytes = 20 build-id + 50 in `yft_ctrl_nightled_by_idx` (idx 4 only, proven equivalent: `../ov64b/evidence/nightled-equivalence.txt`). None is in these TUs. |
| TU parity vs shipped | **s5kjn1 32/32** (13 fn, 19 data), **s5kjn1cts 28/28** (11 fn, 17 data), **ov32b40 24/24** (5 fn, 19 data incl. the 10 580 B init table) (`parity/jn1-slot-tu-parity.tsv`) |
| module-wide | functions 620/621, data 416/416, KCFI 621/621, `__versions`, `.modinfo`/vermagic, imports 131/131, exports, section headers, 2 857 ordered symbols: identical |

## Interface (stock)

* **DT:** `i2c@11c23000` (i2c-4) `sensor1@10` → bus client `4-0010`; no
  `reindex-to`, so idx 1. Endpoint → csi-port-2, D-PHY 4-lane. MCLK `CAMTG2`
  24 MHz (shared selector with sensor4). LDO dvdd 1 / avdd 4 / dovdd 7 plus
  `avdd1-supply` (GPIO76). No afvdd: fixed focus. `#thermal-sensor-cells`.
* **Selection:** `search_sensor()` tries the names in DT order and returns at
  the first `get_id` success.
  * `s5kjn1`: write-ID 0x7A (7-bit 0x3D), chip-ID 0x0000/0x0001 = 0x38E1 (both
    byte orders), bind only if `!is_yft_cts_board()`.
  * `ov32b40`: write-ID 0x6C, 0x300A-C = 0x563242 via `common_get_imgsensor_id`
    (no CTS gate).
  * `s5kjn1cts`: write-ID 0x7A, reads die ID − 1 = 0x38E0, bind only if
    `is_yft_cts_board() == 1`.
* **s5kjn1 power (9 steps):** PDN0 → DOVDD 1.8 (+3 ms) → DVDD 1.2 (+1) →
  AVDD 2.8 → AVDD1 1.8 (+2) → RST1 (+2) → MCLK 4 mA → MCLK 24 (+2) → PDN1 (+1).
  `s5kjn1cts` is identical.
* **s5kjn1 `static_ctx`:** output 35 `RAW_4CELL_BAYER_Gr`, 4 lanes, no PDAF,
  no `eeprom_info`, and **no `reg_addr_stream`**. Streaming runs through the
  feature list instead: `SET_STREAMING_RESUME/SUSPEND` → `0x0100 = 1/0` plus
  10 ms.
* **Modes (5):**
  * preview and normal_video 4080×3072@30 (pclk 560 MHz, LL 5894, FL 3168).
  * capture 8160×6144@10.
  * hs/slim are IMX989 placeholders (pclk 4.39/4.35 GHz, 120/240 fps, 74-pair
    table also used by `ov32b40`) with frame descriptors 1920×1080 / 640×480
    against a 4080×3072 TG. The HAL never selects them. The `corrected` build
    fixes the descriptors.
* **Feature list (s5kjn1, 6):** test pattern, test-pattern data, seamless
  switch, `GET_4CELL_DATA`, streaming suspend/resume.

## GQ5012BF1 behaviour (`evidence/integration-checks.txt`, 24/24 PASS)

* **`s5kjn1` ACTIVE.** `4-0010` is bound (`of:Nsensor1`), and the HAL exposes
  `[01] FRONT SENSOR_DRVNAME_S5KJN1_MIPI_RAW`.
* **`s5kjn1cts` UNREACHABLE on this unit.** `is_yft_cts_board()` is 0 here
  (both `s5kjn1` and `s5kjn1main2` bound, and both need `!cts`), so its gate
  can never pass. It is the CTS-board build of the same die (plain Bayer
  output, no 4-cell or seamless handlers).
* **`ov32b40` NEVER PROBED on this unit.** `s5kjn1` precedes it in the DT list
  and binds. On an OV32B40-populated board it would bind, but its per-mode
  tables are 10-pair PLL stubs that never program an output size. In the HAL,
  the `libcameracustom.imgsensor.core.so` sensor list has no `ov32b40` entry
  (only its IdxMgr .so), and its tuning DB is the MTK default template. It is a
  dormant BOM option.
* **4-cell calibration read is live.** `GET_4CELL_DATA` reads XTC, sensor-XTC,
  PDXTC and SW-GGC (9490 B) from the module EEPROM over the sensor's own
  adapter (i2c-4 0x50 = `4-0050`). That is the chip `camera_eeprom_v4l2` binds
  (layout sensor 0x38E1, header 0x77006901, `CAMERA-EEPROMS`).
* Seamless switch is inert: no mode has a `seamless_switch_group`.
* No slot-specific framework hook (only idx 4 has one). Framework-wide YFT
  hooks apply: HV-charging suspend on open, `yft_camera_device_add` at probe.

## Stock defects / quirks (reproduced by the parity build)

1. **Heap overflow, shared with `s5kjn1main2`.** `VIDIOC_MTK_G_4CELL_DATA`
   allocates `info->size` bytes as the caller asks, and `read_4cell_from_eeprom`
   always copies 9492 B into it. EEPROM read errors are ignored and the cache
   is latched. LieppOS hardening: clamp the copy to the buffer size, or reject
   a short buffer.
2. **Stream-off on close goes to the wrong register.** `ops.close =
   common_close` → `streaming_control(FALSE)` → `wr_u8(reg_addr_stream, 0)`,
   and `reg_addr_stream` is 0. The write lands on chip-ID register 0x0000, not
   0x0100. The real stop happens only through `SET_STREAMING_SUSPEND`, and
   power-off follows close in any case. Same in `s5kjn1cts`.
3. hs/slim placeholder modes (see above). `ov32b40` per-mode stubs (dormant).

## Boundaries (external)

* Tuning, 3A and the 4-cell remosaic: proprietary userspace (`CAMERA-HAL-ISP`).
* EEPROM layout and cam_cal parsing (`CAMERA-EEPROMS`, DONE).
* `is_yft_cts_board()` implementation (`YFT-DEVINFO`; import CRC identical).

## LieppOS contract

Build `imgsensor.ko` with `../reconstruction/imgsensor/build/build.sh … parity`
(or `scripts/build_b1_b2.sh`). The result is a drop-in for stock. Keep the DT
name order (s5kjn1 first). On this board only `s5kjn1` can bind. Keep `4-0050`
readable by both drivers. Hardening options that break parity: defect 1, and
setting `reg_addr_stream = 0x0100` for defect 2.

## Runtime-only validation (not performed)

Streaming camera 1, checking the 4-cell remosaic capture, and per-mode checks.

## Files

* `scripts/build_b1_b2.sh`, `scripts/jn1_slot_parity.py` (all TUs of the slot;
  NOBITS zero-fill; relocation-pinned statics), `scripts/jn1_slot_integration.py`.
* `parity/{b1-b2-build.txt, jn1-slot-parity.txt, jn1-slot-parity.tsv, jn1-slot-tu-parity.tsv}`.
* `evidence/{integration-checks.txt, stock-module-identity.txt}`; `stale-claims.md`.
