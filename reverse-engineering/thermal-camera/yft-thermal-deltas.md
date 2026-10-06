# YFT / Ulefone thermal deltas (summary)

| area | delta | evidence | confidence |
|---|---|---|---|
| DT | `fm78100@0x3c` node name kept from the thermometer variant, compatible `mediatek,tiny2c_usb`; `/yft_tiny2c_usb` with 149/191/192, no 5 V property | stock DT | PROVEN |
| kernel | ODM-only `yft_tiny2c_usb.ko` (no public donor) | `fm78100/parity` | PROVEN |
| kernel | `mt6375-charger` exports `yft_usb_flag`; `extcon-mtk-usb` adds `tiny2c_mode` and honours `yft_usb_flag` | power/usb closures | PROVEN |
| kernel | no thermal UVC driver; GKI `uvcvideo` built in | boot Image | PROVEN |
| HAL | `TINY2C_MIPI_RAW` static metadata only (MIPI variant unused) | vendor libs | PROVEN |
| apps | InfiRay RS300/AC020 SDK in M170infisens/M170infDlp/FactoryMode; Tiny2-C firmware package in M170infDlp; MNN_SR_TINY2C super-resolution | APKs | PROVEN |
| init/SELinux | 0666/0777 on thermal/uSmart nodes; dead `fm78100-sensor` chmods | init.yft.rc | PROVEN |
| marketing | "640×512" = upscaled output; native 256×192 | APK + firmware json + descriptor | STRONGLY SUPPORTED → native 640×512 RETRACTED |

Per-component tables: `fm78100/yft-fm78100-deltas.md`.
