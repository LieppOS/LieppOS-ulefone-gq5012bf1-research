# OV64B (camera 3, rear) — donor analysis, modes, kernel contract

> **Closed 2026-10-07 (`../ov64b/`):** the TU is byte-identical to the SHIPPED
> `imgsensor.ko` (27/27 symbols, B1==B2). The night-vision IR LEDs
> (`aw36518` 8-0063 and `aw36518_v2` 12-0063) follow sensor4 init/power-off
> through `yft_ctrl_nightled_by_idx`. The "Unknowns" section below is resolved;
> tuning is an external boundary.

## Identity (PROVEN)

* Runtime HAL `[03] BACK SENSOR_DRVNAME_OV64B_MIPI_RAW`, hasFlashUnit 1.
* Kernel: `ov64b_mipi_raw` (id 0x566442, regs 0x300A/0x300B/0x300C),
  write-IDs **0x20, 0x44** (7-bit 0x10, 0x22) — stock added 0x20 in front of
  the donor's single 0x44. `get_imgsensor_id` is CTS-gated (calls
  `is_yft_cts_board`; no ov64b CTS variant exists, so a CTS board would
  get no camera 3).
* DT `i2c@11c23000` (i2c-4) `sensor4`, reg 0x20; endpoint →
  `seninf-csi-port-0`; MCLK `CAMTG2_SEL` (shared selector with sensor1).

## Donor

NothingOSS MT6878 `src-v4l2/common/ov64b_mipi_raw` = **same driver
lineage, older/different tuning revision** (`donor-comparisons/ov64b-*`):

* 79/87 static_ctx identical; stock removed EEPROM QSC (`eeprom_num 1→0`,
  `s_cali` NULL), changed output format 37→3, cut modes 12→5.
* `ov64b_set_test_pattern` and `ov64b_set_max_framerate_by_scenario`
  byte-size-identical; `ov64b_seamless_switch` **dropped** in stock;
  `init_ctx` 92→160 (stock adds logging).
* Init table: 2806 vs 2802 pairs, 2805/2801 unique addresses, **847
  addresses with different values** (analog 0x36xx/0x37xx, 0x3820 flip,
  0x5Bxx DPC/BLC…) + stock-only 0x0103 (SW reset), 0x0303, 0x0343, 0x3624.
* Mode tables: none byte-identical; preview/capture/video 146/160 pairs
  shared with donor preview; hs/slim 80/160 with donor custom3.

## Stock modes (5)

| idx | scenario | out | fps | pclk | LL | FL | MIPI rate |
|---|---|---|---|---|---|---|---|
| 0 | preview | 4624×3472 | 30 | 115.2 M | 1056 | 3636 | 600.8 M |
| 1 | capture | 4624×3472 | 30 | " | " | " | " |
| 2 | normal_video | 4624×3472 | 30 | " | " | " | " |
| 3 | hs_video | 1920×1080 | 120 | 115.2 M | 600 | 1600 | 1.2 G |
| 4 | slim_video | 1920×1080 | 120 | " | " | " | " |

No full-array 9248×6944 mode is compiled in → the 64 MP remosaic capture
is not reachable from the stock kernel. hs/slim carry donor frame
descriptors 4624×2604 (window/VC mismatch, same ODM pattern as IMX989).
PDAF type CAMSV but no mode has `pdaf_cap`. Temperature 0x4D13 enabled.

## Kernel contract

exposure 0x3500-02, gain 0x3508/09, FL 0x380E/0F (+0x3840 MSB),
stream 0x0100; pw_seq MCLK24, PDN0, RST0, AVDD 2.8, AFVDD 2.8, DVDD 1.1,
DOVDD 1.8, MCLK 8 mA, PDN1, RST1 (donor additionally had OISVDD/OISEN 3.1 V
steps — removed). custom-LDO avdd=4, afvdd=5, dvdd=1, dovdd=7.

## imgsensor reconstruction (2026-10-02)

Rebuilt byte-identically from the older NothingOSS revision + stock data:
3-byte ID probe with CTS gate, `open` without QSC, seamless switch and QSC
calibration removed (stock has neither). hs/slim VC 4624×2604 vs programmed
1920×1080 fixed only in the CORRECTED header.

## Unknowns

Source text for the stock register revision (data is fully recovered in
`stock-imgsensor-oracle/settings/ov64b_*.tsv`); tuning blobs proprietary
(`ov64b_mipi_raw_tuning.so`, `ISP_param.db` TreeBuildStamp 20250224).
