# FM78100-COMPANION (8-003c) — resolved

**What it is:** the I2C-slave control port of the thermal module's own ASIC
(Raytron/InfiRay Tiny2-C / TC2-C, LY-series ASIC), on I2C8 at 0x3c. It is **not** an
FM78100. "fm78100" is an inherited DT node name from an ODM variant that carried an
FM78100/78102 single-point IR thermometer (`fm78100-sensor`); that driver does not ship
and the FactoryMode thermometer test is hidden on GQ5012BF1.

**What stock does with it:** one boot-time chip-ID read — 16-bit register addresses
0x0000 (=0x59) and 0x0001 (=0x4c), composed `0x4c59` ("LY") — cached and exposed as
`/sys/devices/platform/yft_tiny2c_usb/sensor_id`. FactoryMode's SMT test passes iff it reads
`0x4c59`. Nothing else ever goes over this bus: no writes, no shutter, no calibration, no
firmware, no reset.

**What controls the camera:** `yft_tiny2c_usb.ko` raw GPIOs 149 (VDDIO), 191 (VDD33),
192 (VDD18) via `tiny2c_usb_mode`, plus `yft_usb_flag`; `extcon-mtk-usb` host role via
`tiny2c_mode`; imaging/control over USB `3474:4321` (AC020-UVC). GPIO 55/152 are uSmart,
not thermal.

| file | content |
|---|---|
| `register-map.tsv` | complete I2C transaction map |
| `../hardware/role-map.tsv` | every candidate role, proven/absent |
| `../hardware/topology.md` | DT/board contract, identity classification, GPIO55/152 correction |
| `power-sequence.md` | boot ID read, thermal start/stop ordering and delays |
| `firmware-boundary.md`, `calibration-boundary.md` | none on I2C; module flash/USB ownership |
| `kernel/module-inventory.tsv`, `kernel/stock-search.tsv` | stock inventory |
| `source/yft_tiny2c_usb.c`, `scripts/build.sh` | reconstruction + isolated build |
| `parity/` | A/B parity (11/12 functions byte-identical, data/ABI/strings exact) |
| `yft-fm78100-deltas.md` | ODM deltas / provenance |
