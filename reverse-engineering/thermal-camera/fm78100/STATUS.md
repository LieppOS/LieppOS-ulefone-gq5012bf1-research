# FM78100-COMPANION — STATUS: DONE (static)

| item | result |
|---|---|
| identity | 8-003c = I2C slave of the Tiny2-C/TC2-C module ASIC (STRONGLY SUPPORTED); module = Tiny2-C (PROVEN at firmware/software level); FM78100 fitted: **RETRACTED** |
| bus / address | I2C8 `/soc/i2c@11e03000`, 0x3c, SCL/SDA GPIO 141/142; no IRQ/reset/regulator/clock/pinctrl |
| protocol | 16-bit BE register address, 8-bit data; reads only: 0x0000 (0x59), 0x0001 (0x4c); ID `0x4c59`; retry 3×(5×) with 400 ms + 10 ms delays; no writes anywhere in stock |
| role | boot-time presence/ID only; feeds `sensor_id` (FactoryMode SMT pass, VernoInfo, YftSystemUI) |
| power/reset | rails GPIO 149 → [5v absent] → 191 → 192 (raw, no delay) via `tiny2c_usb_mode`; probe powers on for the ID read and off afterwards; no reset line |
| USB relationship | same module, separate interface; not required for enumeration (thermal start never touches I2C); host role = extcon `tiny2c_mode`; GPIO 55/152 are uSmart |
| kernel driver | `yft_tiny2c_usb.ko` (ODM-only, no public donor); rebuild 11/12 functions byte-identical, probe residual = rolled-vs-peeled sysfs error-unwind loop (behaviour identical); data 27/27, imports 23/23 CRC, modinfo 9/9, strings exact, B1==B2 |
| firmware | none on I2C; module firmware is in module flash, updated over USB (Tiny2-C package hashed in `firmware-boundary.md`) |
| calibration | none on I2C |
| userspace | sysfs only; no `/dev/i2c` use, no ioctl, no daemon |
| stale claims corrected | FM78100 identity; "GPIO55 = thermal D+/D- mux, GPIO152 = camera power"; "640×512 native"; "5 V rail phandle not recovered" (property absent); "sensor_id not captured" (0x4c59 known) |
| open | physical D+/D- wiring (board); ASCII "LY" interpretation (inference); none affect Linux/control behaviour |
