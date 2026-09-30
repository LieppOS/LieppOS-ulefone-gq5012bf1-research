> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.

# Sensors

## Physical sensors proven by live HAL + bus/driver evidence

| Function | Exact/working name | Bus / address | Stock HAL |
|---|---|---|---|
| Accelerometer | IvenSense `icm4n607_acc` | I2C `1-0068` | 12.5–400 Hz class |
| Gyroscope | IvenSense `icm4n607_gyro` | same IMU | 12.5–400 Hz class |
| Magnetometer | Memsic `mmc5603` / MMC5603NJ | `1-0030` | 5–50 Hz, FIFO 4500/600 |
| Ambient light | Sensortek `stk3a5x_als` | on sensor bus (exact address in live buses) | on-change |
| Proximity | Sensortek `stk3a5x_ps` | same family | on-change, wake-up |
| Barometer | Goermicro `spl07` / SPL07-003 | `1-0077` | 1–10 Hz, FIFO 4500/300 |

The snapshot exposes 22 Android sensors. The remaining entries (gravity, linear acceleration, rotation vector, step counter/detector, tilt, orientation, wake gesture, etc.) are MTK/AOSP/vendor fusion outputs, not additional physical ICs.

## Capability layer

* ICM-4N607 exact datasheet is unavailable. ICM-426xx-family inference: accel ±2/4/8/16 g, gyro up to ±2000 dps, FIFO, self-test, high-rate ODR and APEX-class step/tap/wake engines. Do not treat family figures as confirmed exact-die limits.
* MMC5603NJ: 3-axis ±30 G, 20-bit, 0.0625 mG/LSB, up to 1000 Hz ODR, approximately 2 mG noise, self-test and heading/orientation support.
* SPL07-003: 300–1100 hPa, −40…85 °C, I2C/SPI, oversampling and low-power modes; live Android layer uses only 10/20/50 Hz-class rates.
* STK3A5X exact ALS/PS sub-variant, optical range, IR LED current and crosstalk calibration are UNKNOWN.

## Board configuration / stock use

* ICM driver defaults visible to HAL are ±2 g, ±2000 dps and 500 Hz maximum rate; high-g/game-VR virtual sensors are exposed.
* MMC5603 HAL reports a driver-scaled 32768 µT max range and 100 Hz rate cap despite the die's higher possible ODR.
* SPL07 HAL exports 300–1100 hPa and 10/20/50 Hz settings.
* Android sensor-service batching and fusion are enabled; step persistence, calibration values and full wake/suspend behavior require raw sensorservice output over time.

## Hidden / unused

1. IMU APEX step/tap/no-activity/wrist-off engines may be available in the driver but are not proven exposed as all independent Android features.
2. MMC5603 1000-Hz ODR, self-test and precise 20-bit output are hidden behind a 100-Hz HAL cap.
3. SPL07 SPI and high-oversampling modes are not used by the stock sensor HAL.
4. STK3A5X proximity/ALS calibration and gesture/wake thresholds are vendor data, not public chip limits.

## Verification

Dump each IIO/input sysfs node and sensorservice dynamic metadata; run FIFO/ODR tests; read ICM and MMC5603 chip IDs; capture STK3A5X address and calibration EEPROM; test step/tap/tilt while suspended.

Sources: S01–S03, S16/S17; `evidence/local/sensors-live.txt`; findings L12.
