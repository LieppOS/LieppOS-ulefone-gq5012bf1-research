# Thermal hardware

The thermal subsystem is a separately powered InfiRay/InfiSense module on an internal USB2 host path. `yft_tiny2c_usb.ko` controls 1.8/3.3/5/IO-3.3 V enables and probes an I2C 0x3c front-end; FactoryMode expects ID `0x4c59`. `extcon-mtk-usb.ko` routes the USB path. The DT name `fm78100` is legacy power/presence glue, not the detector data interface.

Product evidence identifies a Mini640-class 640x512/12 um/25 Hz radiometric module branded ThermoVue T2; the static multi-product SDK also contains 160x120 and 256x192 factory paths, so physical geometry awaits passive live confirmation. See `../re/hardware-map.md` and `../re/power-sequencing.md`.
