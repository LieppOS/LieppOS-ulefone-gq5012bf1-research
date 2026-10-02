# S5KJN1 family — camera 1 (front, `s5kjn1`) and camera 2 (rear, `s5kjn1main2`)

## Identity (PROVEN)

| | camera 1 | camera 2 |
|---|---|---|
| HAL DRVNAME | S5KJN1_MIPI_RAW, FRONT 270 | S5KJN1MAIN2_MIPI_RAW, BACK |
| DT | i2c-4 `sensor1` reg 0x10, names s5kjn1 / ov32b40 / s5kjn1cts, → csi-port-2 | i2c-2 `sensor2` reg 0x10, name s5kjn1main2, → csi-port-1 |
| write-ID (7-bit) | 0x7A (0x3D) | 0x5A (0x2D) |
| chip-ID read 0x0000/0x0001 | must equal 0x38E1 | **value + 1 must equal 0x38E2** (pseudo-ID; the die is still a JN1 reporting 0x38E1) |
| MCLK | CAMTG2_SEL, 24 MHz | CAMTG4_SEL, 24 MHz |
| custom-LDO | dvdd=1 (1.2 V), avdd=4, dovdd=7 | dvdd=1, avdd=4, dovdd=7, **afvdd=6** |
| AVDD1 1.8 V | `camera-common-avdd1` GPIO76 | `camera2-common-avdd1` (also GPIO76) |
| AF | none | `main4_vcm` (lens table: sensor 0x38E2) |
| PDAF | none | CAMSV, `imgsensor_pd_info`, PD VC 0x30 640×3056 on preview |
| EEPROM QSC hook | none | `set_sensor_cali` + `read_4cell_from_eeprom` |
| stream reg | 0 → `custom_streaming_control` (s5kjn1 only) | 0x0100 |

The `+1` trick (disassembly of `s5kjn1main2 get_imgsensor_id`: `add w8,w8,#1`
before `orr`/`cmp w26=0x38e2`) is how two identical JN1 dies get distinct
sensor IDs and therefore distinct HAL tuning/metadata.

## Donor search

* No public `src-v4l2` driver named `s5kjn1main2`, `s5kjn1cts`, nor this
  exact `s5kjn1`. GitHub code search (authenticated) for `s5kjn1main2`,
  `S5KJN1MAIN2_SENSOR_ID`, `s5kjn1cts`: **0 hits**.
* Closest public sources (fetched, hashes in
  `donor-comparisons/public-donor-file-hashes.txt`):
  * NothingOSS `android_kernel_5.15_nothing_mt6886@mt6886/Pacman/t`
    `src-v4l2/common/s5kjn1_mipi_raw` (legacy-style v4l2 driver);
  * AdarshGrewal `android_kernel_xiaomi_zircon@zircon-t-oss`
    `src-v4l2/common/bailus5kjn1_mipi_raw` (static_ctx style).
* Match (`donor-comparisons/s5kjn1*-table-crossmatch.tsv`): stock
  preview/normal_video (277 pairs, shared by all three JN1 drivers) has the
  **same address sequence as Xiaomi zircon `preview_setting_array` with 5
  values different** (`0x6F12` ×2, 0x0310 PLL, 0x0340 FL 0x0C60 vs 0x0C54,
  0x0342 LL 0x1706 vs 0x1716). Capture (241 pairs) is only 149/241 similar
  to any donor. The open() inline init (37 writes, identical in all three
  JN1 drivers, `stock-imgsensor-oracle/inline/`) contains **all 30 pairs**
  of the Nothing-mt6886 JN1 init plus 7 more.

## Stock modes (5 each)

preview/normal_video 4080×3072@30 (pclk 560 M, LL 5894, FL 3168),
capture 8160×6144@10 (LL 8688, FL 6400), hs_video/slim_video:
**IMX989 timings pasted in** (pclk 4.3904/4.352 GHz, LL 11168/7168,
1200/2400 fps) with a 74-pair Samsung table also used by `ov32b40` and
the CTS drivers, and frame descriptors 1920×1080 / 640×480 that do not
match the 4080×3072 window. These are ODM placeholders (PROVEN at
data level); the HAL stream tables for cams 1/2 do not offer 120/240 fps.

## Variants compiled into the same imgsensor.ko

`s5kjn1cts` (id 0x38E0, CTS boards), `ov32b40` (alternate front die,
0x563242 @0x6C, default MTK tuning DB template), `s5kgn1sp`/`s5kgm2sp`
(alternate main dies). All recovered by the oracle.

## Remaining

C source for the three JN1 TUs (data + inline init fully recovered;
logic is framework `common_*`); tuning proprietary
(`s5kjn1_mipi_raw_tuning.so`, `s5kjn1main2_mipi_raw_tuning.so`,
ISP_param.db 2.5 MB / 5.4 MB).
