# Thermal camera (GQ5012BF1, "ThermoVue T2")

| layer | what it is | where |
|---|---|---|
| module | Raytron/InfiRay **Tiny2-C (TC2-C)** LWIR, native 256×192, 12 µm, 25 Hz; one ASIC with USB2 UVC device `3474:4321` + I2C slave `8-003c` | `hardware/topology.md`, `ac020/README.md` |
| 8-003c ("FM78100-COMPANION") | the module ASIC's I2C slave; stock only reads chip ID `0x4c59` once at boot | `fm78100/` |
| power | `yft_tiny2c_usb.ko` raw GPIO 149/191/192 via `tiny2c_usb_mode` (+ `yft_usb_flag`) | `fm78100/power-sequence.md` |
| USB role | `extcon-mtk-usb` `tiny2c_mode` → HOST | `reverse-engineering/usb/` |
| stream/control | GKI uvcvideo binds, apps detach it and drive usbfs via bundled libusb; vendor vdcmd on EP0 | `ac020/` |
| apps | M170infisens `com.energy.tc2c`, M170infDlp `com.energy.tc2c.sop`, FactoryMode | `userspace/` |

GPIO 55/152/28 are the uSmart accessory path, not thermal. FM78100 is not fitted.
