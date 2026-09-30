> **Pass-2 pointer (2026-09-08).** First-pass working material. Where anything here conflicts with `../../final/` or `../../verification/findings/`, the verification pass wins. Two blanket corrections apply: the 2026-08-31 capture ran a **LieppOS GSI**, so its framework-level observations are not stock Ulefone behaviour; and `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this board's bill of materials.

# Frozen live-device snapshot summary

Source: `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/`, captured 2026-08-31 11:56 on the GQ5012BF1 EEA build. This is not a current live re-check; `adb devices` had no device during the audit continuation.

## Identity / services

* Android 15, `Ulefone/GQ5012BF1_EEA/GQ5012BF1`, build `AP3A.240905.015.A2/1761131274`.
* Vendor GNSS, Wi-Fi, NFC, USB and thermal services are running. Bluetooth was never enabled in the capture.
* `vendor.connsys.wifi.adie.chipid=0x6637`, `vendor.connsys.gps.adie.chipid=0x6637`; `vendor.debug.gps.support.l5=1`; DSDS and VoLTE/VoWiFi properties are enabled.

## Camera enumeration

```text
[00] BACK  SENSOR_DRVNAME_IMX989_MIPI_RAW       hasFlashUnit:1
[01] FRONT SENSOR_DRVNAME_S5KJN1_MIPI_RAW       hasFlashUnit:0
[02] BACK  SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW   hasFlashUnit:1
[03] BACK  SENSOR_DRVNAME_OV64B_MIPI_RAW         hasFlashUnit:1
```

HAL contains stream-configuration metadata and optical/video-stabilization keys; OIS metadata is `[0]`. Detailed decoded stream arrays are not in the snapshot summary.

## Buses / support silicon

* `speaker_amp` AW88394 at `6-0034`; AW2013 at `11-0045`; AW36515/18 at `6-0063`, `8-0063`, `12-0063`.
* FT3680 touch on SPI3; Madev fingerprint on SPI1; Hynitron rear touch `0-0015`; ST21NFC `6-0008`.
* RT5133 `5-0018`; MT6375 `5-0034`; SC8571 `11-0066`/`6-0067`; SC851x `6-0069`; SH366003 `9-0055`; RT6160 rails `5-0075`/`6-0075`.
* Thermal `fm78100`/`tiny2c_usb` `8-003c`; OCP2131 `6-003e`; WL2864C `11-0029`; camera EEPROM/VCM/OIS nodes are preserved in `../local/buses-live.txt`.

## Display / sensor / thermal observations

* Primary display framework: 1080×2400, 60/90/120 Hz, HDR types `[2,3,4]`, 500-nit framework max; active snapshot mode 60 Hz.
* 22 Android sensor entries map to four physical groups: ICM IMU, MMC5603 magnetometer, STK3A5X ALS/PS and SPL07 barometer; remaining entries are fusion/virtual sensors.
* Thermal HAL current values: CPU/GPU/NPU/TPU/SOC ~46.8 °C, skin ~39.2 °C, battery 37 °C, USB 43 °C, PA ~39.7 °C. Cooling devices include Mali devfreq, charger, LCD, Wi-Fi and flashlight.

## Battery / haptics

* Battery: USB powered, wireless false, 79%, 8.400 V, Li-ion, charge counter 2,327,340 µAh; observed max current 1 A and max voltage 5 V. Gauge fields report design capacity 8,594,000 µAh and maximum capacity 2,946,000 (units/semantics unresolved).
* One vibrator ID with effect support but no primitives/frequency/acceleration characteristics.

Raw/filtered evidence: `../local/buses-live.txt`, `../local/sensors-live.txt`, `camera-hal-live.txt`, and original snapshot files.
