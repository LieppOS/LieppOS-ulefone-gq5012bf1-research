# imx989_mipi_raw (stock) vs imx989_mipi_raw (donor)

* sensor id: stock 0x989 / donor 0x989
* pw_seq: stock [('HW_ID_MCLK', 19, 0), ('HW_ID_PDN', 0, 0), ('HW_ID_RST', 0, 0), ('HW_ID_MCLK_DRIVING_CURRENT', 4, 1), ('HW_ID_AVDD', 2800000, 0), ('HW_ID_AVDD2', 1800000, 0), ('HW_ID_AFVDD', 2800000, 0), ('HW_ID_DOVDD', 1800000, 0), ('HW_ID_DVDD', 1100000, 1), ('HW_ID_PDN', 1, 1), ('HW_ID_RST', 1, 2)]
* pw_seq: donor [('11', 19, 0), ('10', 0, 0), ('12', 4, 1), ('0', 2900000, 0), ('6', 1800000, 0), ('3', 3100000, 0), ('4', 1800000, 0), ('2', 1800000, 0), ('1', 1100000, 1), ('16', 3100000, 1), ('10', 1, 2)]

## static_ctx field deltas

| field | stock | donor |
|---|---|---|
| eeprom_info | `eeprom_info@750` | `eeprom_info` |
| saturation_info | `imgsensor_saturation_info_10bit@1780` | `imgsensor_saturation_info_10bit` |
| start_exposure_offset | `7600000` | `5500000` |
| pdaf_type | `CAMSV_QPD` | `CAMSV_DUALPD` |
| hdr_type | `0` | `416` |
| mode | `mode_struct@1c28` | `mode_struct` |
| list | `feature_control_list@54e0` | `feature_control_list` |
| list_len | `5` | `4` |

79 static_ctx fields identical.

## Mode table

stock modes: 33, donor modes: 33

| idx | scenario | stock out | donor out | identical fields | differing fields | reg table |
|---|---|---|---|---|---|---|
| 0 | preview | 4096x3072 | 4096x3072 | 34 | pclk: 4390400000→4070400000, linelength: 44672→11168, framelength: 3272→12144, mipi_pixel_rate: 585530000→2445531428, fine_integ_line: 0→-982 | SAME_ADDR_SEQ, 22/279 values differ: 0x0342:0x002b->0x00ae, 0x0343:0x00a0->0x0080, 0x0340:0x002f->0x000c, 0x0341:0x0070->0x00c8, 0x0307:0x003e->0x0057, 0x030b:0x0001->0x0004, 0x030d:0x0004->0x0013, 0x030e:0x0002->0x000d |
| 1 | capture | 4096x3072 | 4096x3072 | 34 | pclk: 4390400000→4070400000, linelength: 44672→11168, framelength: 3272→12144, mipi_pixel_rate: 585530000→2445531428, fine_integ_line: 0→-982 | SAME_ADDR_SEQ, 22/279 values differ: 0x0342:0x002b->0x00ae, 0x0343:0x00a0->0x0080, 0x0340:0x002f->0x000c, 0x0341:0x0070->0x00c8, 0x0307:0x003e->0x0057, 0x030b:0x0001->0x0004, 0x030d:0x0004->0x0013, 0x030e:0x0002->0x000d |
| 2 | normal_video | 4096x2304 | 4096x2304 | 34 | pclk: 3328000000→3225600000, linelength: 44672→11168, framelength: 2480→9624, mipi_pixel_rate: 442260000→2445531428, fine_integ_line: 0→-982 | SAME_ADDR_SEQ, 23/279 values differ: 0x0342:0x002b->0x00ae, 0x0343:0x00a0->0x0080, 0x0340:0x0025->0x0009, 0x0341:0x0098->0x00b0, 0x0306:0x0000->0x0001, 0x0307:0x00fc->0x0004, 0x030b:0x0001->0x0004, 0x030d:0x0004->0x0013 |
| 3 | hs_video | 1920x1080 | 4096x2304 | 32 | pclk: 2252800000→4390400000, linelength: 14336→11168, framelength: 1304→3272, mipi_pixel_rate: 411430000→3085714286, coarse_integ_step: 8→4, winsize, fine_integ_line: 0→-982 | SAME_ADDR_SEQ, 43/279 values differ: 0x0342:0x002b->0x0038, 0x0343:0x00a0->0x0000, 0x0340:0x000c->0x0005, 0x0341:0x00c8->0x0018, 0x0345:0x0000->0x00c0, 0x0347:0x0000->0x0080, 0x0349:0x00ff->0x003f, 0x034b:0x00ff->0x007f |
| 4 | slim_video | 1280x720 | 1920x1080 | 33 | pclk: 3340800000→4352000000, linelength: 14336→7168, framelength: 968→2528, mipi_pixel_rate: 451100000→2445531428, winsize, fine_integ_line: 0→-1486 | SAME_ADDR_SEQ, 33/279 values differ: 0x0342:0x001c->0x0038, 0x0340:0x0009->0x0003, 0x0341:0x00e0->0x00c8, 0x0346:0x0003->0x0006, 0x0347:0x0080->0x0060, 0x034a:0x0014->0x0011, 0x034b:0x007f->0x009f, 0x0408:0x0000->0x0001 |
| 5 | custom1 | 3840x2160 | 1280x720 | 29 | setting_len: 558→562, pclk: 3174400000→2982400000, linelength: 44672→3584, framelength: 2368→864, max_framerate: 300→9600, mipi_pixel_rate: 854390000→3085714286, coarse_integ_step: 4→8, winsize, pdaf_cap: 1→0, fine_integ_line: 0→-2973 | DIFFERENT (stock 279 pairs, donor 281 pairs; 230 common pairs, 1 addr not shared) |
| 6 | custom2 | 1920x1080 | 1920x1080 | 38 | fine_integ_line: 0→-2973 | IDENTICAL (281 pairs) |
| 7 | custom3 | 1280x720 | 1280x720 | 39 | — | IDENTICAL (279 pairs) |
| 8 | custom4 | 3296x2460 | 4096x2304 | 24 | seamless_group: 0→2, seamless_len: 0→174, hdr_mode: NONE→RAW_DCG_COMPOSE, exp_cnt: 1→2, pclk: 3558400000→3225600000, linelength: 44672→42400, framelength: 2648→2528, mipi_pixel_rate: 1398680000→2037942857, coarse_integ_step: 4→2, winsize, fine_integ_line: 0→-436, vc, dcg_mode: 0→1, dcg_gain_mode: 0→1, sensor_output_dataformat: 40→19 | SAME_ADDR_SEQ, 46/279 values differ: 0x0112:0x000c->0x000a, 0x0113:0x000c->0x000a, 0x0342:0x00a5->0x00ae, 0x0343:0x00a0->0x0080, 0x0340:0x0009->0x000a, 0x0341:0x00e0->0x0058, 0x0346:0x0003->0x0002, 0x0347:0x0000->0x0060 |
| 9 | custom5 | 4096x2304 | 4096x2304 | 39 | — | IDENTICAL (279 pairs) |
| 10 | custom6 | 4096x2304 | 4096x2304 | 39 | — | IDENTICAL (279 pairs) |
| 11 | custom7 | 4096x2304 | 4096x2304 | 25 | setting_len: 538→558, hdr_mode: NONE→RAW_STAGGER, raw_cnt: 1→2, exp_cnt: 1→2, pclk: 2112000000→3225600000, linelength: 13632→11168, framelength: 2580→9616, max_framerate: 600→300, mipi_pixel_rate: 932230000→2445531428, readout_length: 0→4848, framelength_step: 8→16, coarse_integ_step: 4→16, num_entries: 2→4, vc | DIFFERENT (stock 269 pairs, donor 279 pairs; 239 common pairs, 18 addr not shared) |
| 12 | custom8 | 2048x1152 | 4096x2304 | 28 | setting_len: 538→558, seamless_group: 0→2, seamless_len: 0→174, pclk: 2112000000→3225600000, linelength: 10880→11168, framelength: 3232→4808, mipi_pixel_rate: 589170000→2445531428, coarse_integ_step: 2→4, winsize, fine_integ_line: 0→-982, vc | DIFFERENT (stock 269 pairs, donor 279 pairs; 230 common pairs, 18 addr not shared) |
| 13 | custom9 | 4096x3072 | 4096x2304 | 29 | seamless_len: 0→174, pclk: 4070400000→3225600000, linelength: 11168→21536, framelength: 12144→2496, max_framerate: 300→600, coarse_integ_step: 4→2, winsize, fine_integ_line: -982→-484, vc, sensor_output_dataformat: 0→32 | SAME_ADDR_SEQ, 30/279 values differ: 0x0342:0x0054->0x002b, 0x0343:0x0020->0x00a0, 0x0340:0x0009->0x002f, 0x0341:0x00c0->0x0070, 0x0346:0x0007->0x0000, 0x0347:0x0080->0x0000, 0x034a:0x0010->0x0017, 0x034b:0x007f->0x00ff |
| 14 | custom10 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 15 | custom11 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 16 | custom12 | 8192x6144 | 8192x6144 | 34 | setting_len: 538→558, pclk: 2112000000→4070400000, framelength: 6536→7872, max_framerate: 150→240, mipi_pixel_rate: 987430000→2445531428 | DIFFERENT (stock 269 pairs, donor 279 pairs; 253 common pairs, 18 addr not shared) |
| 17 | custom13 | 8192x6144 | 8192x6144 | 39 | — | IDENTICAL (279 pairs) |
| 18 | custom14 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 19 | custom15 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 20 | custom16 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 21 | custom17 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 22 | custom18 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 23 | custom19 | 2048x1152 | 4096x3072 | 31 | pclk: 3200000000→4070400000, linelength: 21760→11168, framelength: 2448→6072, mipi_pixel_rate: 499080000→2445531428, coarse_integ_step: 8→4, winsize, fine_integ_line: 0→-982, vc | SAME_ADDR_SEQ, 39/279 values differ: 0x0342:0x002b->0x0055, 0x0343:0x00a0->0x0000, 0x0340:0x0017->0x0009, 0x0341:0x00b8->0x0090, 0x0346:0x0000->0x0003, 0x034a:0x0017->0x0014, 0x0901:0x0022->0x0044, 0x31d0:0x0041->0x0043 |
| 24 | custom20 | 7680x4320 | 7680x4320 | 34 | setting_len: 536→558, pclk: 2999100000→4339200000, framelength: 4642→6712, mipi_pixel_rate: 1959000000→2445531428, sensor_output_dataformat: 3→32 | DIFFERENT (stock 268 pairs, donor 279 pairs; 251 common pairs, 19 addr not shared) |
| 25 | custom21 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 26 | custom22 | 4096x2304 | 4096x2304 | 39 | — | IDENTICAL (279 pairs) |
| 27 | custom23 | 2048x1152 | 4096x2304 | 31 | pclk: 3200000000→3328000000, linelength: 21760→22336, framelength: 2448→2480, mipi_pixel_rate: 499080000→2445531428, coarse_integ_step: 8→4, winsize, fine_integ_line: 0→-491, vc | SAME_ADDR_SEQ, 36/279 values differ: 0x0342:0x0057->0x0055, 0x0343:0x0040->0x0000, 0x0341:0x00b0->0x0090, 0x0901:0x0022->0x0044, 0x31d0:0x0041->0x0043, 0x31d1:0x0041->0x0043, 0x040c:0x0010->0x0008, 0x040e:0x0009->0x0004 |
| 28 | custom24 | 4096x2304 | 4096x2304 | 39 | — | IDENTICAL (279 pairs) |
| 29 | custom25 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |
| 30 | custom26 | 1920x1080 | 1920x1080 | 39 | — | IDENTICAL (279 pairs) |
| 31 | custom27 | 2048x1152 | 4096x2304 | 31 | pclk: 3200000000→4390400000, linelength: 21760→11168, framelength: 2448→6552, mipi_pixel_rate: 499080000→3085714286, coarse_integ_step: 8→4, winsize, fine_integ_line: 0→-982, vc | SAME_ADDR_SEQ, 37/279 values differ: 0x0342:0x002b->0x0055, 0x0343:0x00a0->0x0000, 0x0340:0x0019->0x0009, 0x0341:0x0098->0x0090, 0x0901:0x0022->0x0044, 0x31d0:0x0041->0x0043, 0x31d1:0x0041->0x0043, 0x040c:0x0010->0x0008 |
| 32 | custom28 | 4096x3072 | 4096x3072 | 39 | — | IDENTICAL (279 pairs) |

## Init / seamless tables

* init: IDENTICAL (295 pairs)
* mode 0 seamless `imx989_seamless_preview` vs `imx989_seamless_preview`: IDENTICAL (102 pairs)
* mode 1 seamless `imx989_seamless_capture` vs `imx989_seamless_capture`: IDENTICAL (102 pairs)
* mode 2 seamless `imx989_seamless_normal_video` vs `imx989_seamless_normal_video`: IDENTICAL (87 pairs)
* mode 8 seamless `` vs `imx989_seamless_custom4`: missing
* mode 9 seamless `imx989_seamless_custom5` vs `imx989_seamless_custom5`: IDENTICAL (87 pairs)
* mode 10 seamless `imx989_seamless_custom6` vs `imx989_seamless_custom6`: IDENTICAL (87 pairs)
* mode 11 seamless `imx989_seamless_custom7` vs `imx989_seamless_custom7`: SAME_ADDR_SEQ, 16/87 values differ: 0x381f:0x0001->0x0000, 0x3890:0x0001->0x0000, 0x3891:0x000c->0x00f8, 0x3894:0x0001->0x0000, 0x3895:0x001a->0x00f4, 0x3897:0x0088->0x00a0, 0x389b:0x008c->0x00a8, 0x38b8:0x0001->0x0000
* mode 12 seamless `` vs `imx989_seamless_custom8`: missing
* mode 13 seamless `` vs `imx989_seamless_custom9`: missing
* mode 14 seamless `imx989_seamless_custom10` vs `imx989_seamless_custom10`: IDENTICAL (102 pairs)
* mode 15 seamless `imx989_seamless_custom11` vs `imx989_seamless_custom11`: IDENTICAL (102 pairs)
* mode 16 seamless `imx989_seamless_custom12` vs `imx989_seamless_custom12`: IDENTICAL (102 pairs)
* mode 17 seamless `imx989_seamless_custom13` vs `imx989_seamless_custom13`: IDENTICAL (102 pairs)
* mode 18 seamless `imx989_seamless_custom14` vs `imx989_seamless_custom14`: IDENTICAL (102 pairs)
* mode 19 seamless `imx989_seamless_custom15` vs `imx989_seamless_custom15`: IDENTICAL (102 pairs)
* mode 20 seamless `imx989_seamless_custom16` vs `imx989_seamless_custom16`: IDENTICAL (102 pairs)
* mode 21 seamless `imx989_seamless_custom17` vs `imx989_seamless_custom17`: IDENTICAL (102 pairs)
* mode 22 seamless `imx989_seamless_custom18` vs `imx989_seamless_custom18`: IDENTICAL (102 pairs)
* mode 23 seamless `imx989_seamless_custom19` vs `imx989_seamless_custom19`: IDENTICAL (102 pairs)
* mode 24 seamless `imx989_seamless_custom20` vs `imx989_seamless_custom20`: IDENTICAL (102 pairs)
* mode 28 seamless `imx989_seamless_custom24` vs `imx989_seamless_custom24`: IDENTICAL (87 pairs)
* mode 29 seamless `imx989_seamless_custom25` vs `imx989_seamless_custom25`: IDENTICAL (102 pairs)
* mode 32 seamless `imx989_seamless_custom28` vs `imx989_seamless_custom28`: IDENTICAL (102 pairs)
