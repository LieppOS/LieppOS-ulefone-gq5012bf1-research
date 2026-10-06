# YFT / Ulefone deltas — 8-003c ("FM78100") path

No public donor source exists for `yft_tiny2c_usb` (bounded identifier searches in
NothingOSS/ALPS/kernel-research/public code: `NO_PUBLIC_DONOR_FOUND`, see
`kernel/phase4-yft-tiny2c-usb-source-candidates.md`). Provenance is therefore binary
reconstruction from the stock oracle; parity in `parity/`.

| # | donor / reference behaviour | GQ5012BF1 behaviour | evidence | delta | confidence |
|---|---|---|---|---|---|
| 1 | ODM base: `fm78100-sensor` I2C driver for an FM78100/78102 IR thermometer (chip_power/chip_enable/chip_exist/mems_temp/ntc_temp/objs_temp) | not built; node name `fm78100@0x3c` kept, compatible changed to `mediatek,tiny2c_usb` | init.yft.rc 41-52, FactoryMode `ThermometerTestActivity`, `libthermometerTemp78102.so`; no `.ko`/Image hit | DT reuse of the old node | PROVEN |
| 2 | — | new `yft_tiny2c_usb.ko` (author `yft-drv`): rails 149/191/192 + optional 5 V slot, boot ID read, `tiny2c_usb_mode`, `sensor_id` | stock module | ODM-only driver | PROVEN (11/12 byte-identical) |
| 3 | MT6375 charger | exports `int yft_usb_flag` used to skip BC1.2/Type-C handling while thermal owns USB | `power-charging/yft-power-deltas.md` #17 | provider ABI | PROVEN |
| 4 | ALPS extcon-mtk-usb | `yft_extcon/tiny2c_mode` → host role; `yft_usb_flag` gates TCPC/ID role events | `usb/yft-usb-deltas.md` | consumer | PROVEN |
| 5 | MTK HAL | `TINY2C_MIPI_RAW` static metadata for a MIPI Tiny2-C variant | libcam.halsensor.so etc.; no kernel imgsensor driver, empty tuning dir | unused on this SKU | PROVEN unused |
| 6 | InfiRay SDK | MIPI/I2C variant constants (`I2C_ADDRESS=72`, `/dev/i2c-8`, `/dev/video0`) left in M170infisens `Const` | decompiled APK; no references | dead constants | PROVEN |
| 7 | — | DT omits `tiny2c_usb_vdd_5v`; module VDD50 not software-switched | DT | board config | PROVEN (absence) |
| 8 | — | stock bugs kept: `tiny2c_mode` show always 0; no unwind on probe errors; I2C remove calls `i2c_unregister_device(client)`; sysfs nodes chmod 0666 | binaries | quirks | PROVEN |
