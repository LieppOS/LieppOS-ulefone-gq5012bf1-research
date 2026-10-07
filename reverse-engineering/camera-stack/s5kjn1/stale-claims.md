# CAMERA-S5KJN1 — stale / wrong claims corrected (2026-10-07)

| # | claim (where) | verdict | correction / evidence |
|---|---|---|---|
| 1 | "Still required: C source for the stock TU (data complete)" (workspace README, status row) | **RESOLVED** | All three slot TUs are byte-identical to the **shipped** `imgsensor.ko`: s5kjn1 32/32, s5kjn1cts 28/28, ov32b40 24/24. B1==B2 (`parity/`). |
| 2 | "Still required: hs/slim modes are IMX989 placeholders" (workspace README) | **RECLASSIFIED** | This is a stock data fact, now reproduced and documented, not an open question. The HAL never selects these modes, and the `corrected` build fixes the descriptors. |
| 3 | "tuning proprietary" as a blocker | **RECLASSIFIED** | External boundary (`CAMERA-HAL-ISP`). |
| 4 | "no AF/PDAF/**EEPROM hook**" (workspace README "Proven so far"); "EEPROM QSC hook: none" for camera 1 (`notes/s5kjn1-family.md`) | **WRONG (EEPROM part)** | `s5kjn1` reads 9490 B of 4-cell calibration from `4-0050` via `GET_4CELL_DATA`, and it carries the same user-sized-buffer overflow as `s5kjn1main2`. No AF and no PDAF are correct. |
| 5 | "stream reg 0 → `custom_streaming_control` (s5kjn1 only)" (`notes/s5kjn1-family.md`) | **INCOMPLETE** | `s5kjn1cts` has the same custom stream control. In both, `common_close` still writes 0 to register 0x0000 because `reg_addr_stream` is unset. |
| 6 | "slot alternates ov32b40 / s5kjn1cts" (workspace README) | **CLARIFIED** | On this unit only `s5kjn1` can bind. `s5kjn1cts` needs `is_yft_cts_board()==1` (it is 0 here). `ov32b40` is never probed (DT order, first match wins), is absent from the HAL imgsensor.core sensor list, and has stub mode tables, so it is a dormant BOM option. |
| 7 | 2026-10-02 "byte-for-byte … 618/619 functions, 394/394 data objects" (workspace README) | **SUPERSEDED** | 620/621 and 416/416 against the shipped module (70-byte file delta). The 2026-10-03 "our build vs our build" relabel is wrong (`../ov64b/stale-claims.md` #2). |
| 8 | JN1 "4K@60, 1080p@240" (qwen `cameras.md` capability table) | **CLARIFIED** | That is a silicon capability. Stock kernel modes stop at 4080×3072@30 and 8160×6144@10; the 120/240 fps slots are IMX989 placeholders. |
