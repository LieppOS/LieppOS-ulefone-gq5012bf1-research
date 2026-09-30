# Thermal calibration

Corrected classic-path pixels are LE uint16 at 1/64 kelvin; Celsius is `raw/64-273.15`. Gain-specific KT/BT, NUC-T, B/OOC, DPC and RMVC data feed environmental correction for emissivity, transmission, ambient/reflected temperature, humidity and distance. The module exposes default and second-calibration file trees.

FactoryMode validates `secd_cali_data/manufacturer_temporary_data.bin`: length >=192 and byte 0==1. Treat all module-resident files as per-unit and irreplaceable. APK assets are generic multi-product seeds and must never overwrite production calibration. See `../re/calibration-format.md`, `../re/radiometry.md` and `../re/ffc-nuc.md`.
