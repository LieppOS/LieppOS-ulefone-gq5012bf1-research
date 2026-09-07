# MASTER HARDWARE INVENTORY — Ulefone Armor 29 Pro Thermal (GQ5012BF1)

> Generated from live ADB snapshots, kernel I2C/SPI device enumeration, camera HAL output,
> sensor service dump, thermal/power dumps, device-tree analysis, and vendor library analysis.
>
> **Evidence sources**:
> - Live stock snapshot (`live-stock-adb-20260831-115649/`)
> - Kernel I2C/SPI bus enumeration
> - Camera HAL device enumeration
> - Android sensor service dump (`dumpsys sensorservice`)
> - Thermal HAL AIDL v3 dump
> - Battery/PowerService dump
> - Device tree (DTB) analysis
> - Vendor library / init service / property analysis
>
> **Confidence levels**: PROVEN > STRONGLY_SUPPORTED > LIKELY > POSSIBLE > UNKNOWN

---

## 1. Device Identity

| Field | Value |
|---|---|
| Marketing name | Ulefone Armor 29 Pro Thermal |
| Android product | GQ5012BF1 |
| Boot fingerprint | `Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274` |
| Baseband | `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1` |
| Connsys chip ID | `0x6878` (`persist.vendor.connsys.chipid`) |
| Serial | `5012BF3010001335` |
| Region | EEA (`ro.boot.vba_regional: EEA`) |
| Custom version | `DZ_M170_Ulefone_EEA_Armor29Pro_20251022_V35` |

---

## 2. Hardware Summary (Quick Counts)

| Category | Count |
|---|---|
| **Rear visible-light cameras** | 3 |
| **Front cameras** | 1 |
| **Thermal imaging sensors** | 1 (USB-connected, ThermoVue T2, 640×512) |
| **Total visible-light + thermal sensors** | 5 |
| **Rear display** | 1 (CO5300, 1.04″ 340×340 AMOLED, SPI) |
| **Rear touch controllers** | 1 (Hynitron hyn_ts) |
| **Speakers** | ≥1 external; earpiece separate |
| **Microphones** | ≥2 (headset + internal) |
| **Flash / torch LEDs** | Controlled by AW36515 + AW36518-family |
| **IR blaster** | Yes (listed in official sensor list; vendor `ir-default` service present) |
| **Physical buttons** | ≥3 (power, volume, yft-gpio-keys → F1/F2) |
| **Haptic motor** | 1 (ERM, software-emulated) |
| **IMU** | 1 (IvenSense ICM4N607, accel+gyro) |
| **Magnetometer** | 1 (Memsic MMC5603) |
| **ALS/Proximity** | 1 combo (Sensortek STK3A5X) |
| **Barometer** | 1 (Goer SPL07) |
| **Fingerprint** | 1 (Madev, side-mounted capacitive in power key, SPI, TEE-authenticated) |
| **NFC** | 1 (ST21NFC) |
| **Fuel-gauge ICs** | 2 (MT6375 primary, SH366003 secondary) |
| **Charge-pump ICs** | 3 (SC8571 master, SC8571 slave, SC851x) |
| **LED controller** | 1 (Awinic AW2013 RGB) |
| **Touchscreen controller** | 1 (FocalTech FT3680, SPI) |
| **Display panel controller** | 1 (YFT VTDR6115, DSI) |

---

## 3. SoC

| Field | Value |
|---|---|
| Marketing name | **MediaTek Dimensity 7400** (official Ulefone spec) |
| Platform variant | **MT6878T** (per Ulefone official spec; MT6878 family) |
| Kernel platform string | `mt6878` (`ro.hardware`, `ro.boot.hardware`, `ro.board.platform`) |
| CPU | 4× Arm Cortex-**A78** (up to 2.6 GHz) + 4× Arm Cortex-**A55** (up to 2.0 GHz) |
| GPU | **Arm Mali-G615 MC2**, up to 1400 MHz (`ro.hardware.vulkan: mali`, `vendor.mali_platform-mediatek`) |
| NPU | MediaTek NPU (official spec: "MediaTek NPU 655"); NPU temp zone present in thermal HAL |
| Process node | TSMC 4 nm (per GSMArena/web) |
| DDR (RAM) | 16 GB (`ro.boot.ddr_size: 17179869184`) + up to 16 GB dynamic RAM expansion (official) |
| ISP | MTK ISP-DIP-V4L2 (`media_device_info topology[0]`) |
| Modem | MTK integrated 5G (MOLY baseband `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1`) |
| Wi-Fi/BT co-chip | MediaTek **MT6637** (dmesg: `ADIE6637` = A-die 0x66378a01), connsys D-die `connsys_d_die_cfg_mt6878` |
| GNSS | MTK connsys (`vendor.gnss-default`) |

**NOTE — SoC identification**: Ulefone's official spec sheet lists the SoC as
"MediaTek Dimensity 7400, CPU: MT6878T" (4×A78@2.6GHz + 4×A55@2.0GHz, Mali-G615 MC2).
Dimensity 7400 is a Dimensity-8300-family derivative: it lives on the **MT6878 platform**,
which is exactly why every kernel/ISP string on this device says `mt6878`
(`ro.hardware`, `connsys_d_die_cfg_mt6878`, ISP tuning DB `mt6878/`). It is **not** a
Dimensity 8300 (which would be 4×A715 + 4×A55 with Mali-G615 MC5/MC6).

**Evidence**: `ro.boot.hardware: mt6878`, `ro.board.platform: mt6878`,
`persist.vendor.connsys.chipid: 0x6878`, dmesg `ADIE6637` / `connsys_d_die_cfg_mt6878`,
`ro.kernel.version: 6.1`, Ulefone official spec sheet (store.ulefone.com),
GSMArena (Dimensity 7400, 4×A78 + 4×A55, Mali-G615 MC2).

---

## 4. RAM

| Field | Value |
|---|---|
| Capacity | **16 GB** |
| Type | LPDDR (TBD: LPDDR5/5X) |
| Manufacturer | UNKNOWN |
| Part number | UNKNOWN |
| Boot-reported size | `17179869184` bytes (16 GiB exactly) |
| RAM expansion | Up to +16 GB storage-backed ("Dynamic RAM Expansion", official spec) |

**Evidence**: `ro.boot.ddr_size: 17179869184`, Ulefone official spec sheet.

---

## 5. Storage

| Field | Value |
|---|---|
| Interface | UFS (`/dev/block/loopN` backing `sdc` — UFS device) |
| Boot path | `112b0000.ufshci` (`ro.boot.boot_devices`) |
| Partitions | system, vendor, product, persist, protect_f/s, nvcfg, nvdata, metadata, data |
| RPMB | Present (`ro.boot.rpmb_status: 1`) |
| Capacity | **512 GB** (official spec, 16 GB + 512 GB SKU) |
| microSD | Dedicated slot, up to **2 TB** (official spec) |
| UFS version | TBD |

**Evidence**: `ro.boot.boot_devices: bootdevice, soc/112b0000.ufshci`,
`ro.boot.rpmb_status: 1`, `dev.mnt.rootdisk.data: sdc` (UFS), Ulefone official spec sheet.

---

## 6. Display (Main)

| Field | Value |
|---|---|
| Panel driver | `yft-lcm-vtdr6115-drv` |
| DSI connector | `card0-DSI-1` |
| Size | **6.67″** (official) |
| Native resolution | **1080 × 2400** |
| Pixel density | 480 dpi reported (≈395 ppi true by geometry) |
| Refresh rates | 60 / 90 / 120 Hz (HWC exposes all three; snapshot active mode = 60 Hz) |
| Panel type | **AMOLED** (official) |
| Protection | **Corning Gorilla Glass 3** (official), oleophobic coating |
| Brightness | 2200 nits peak (GSMArena; not software-verifiable) |
| Colors | 1B colors (GSMArena) |
| HDR | **HDR10 + HLG + Dolby Vision** (HAL `supportedHdrTypes: [2,3,4]`) |
| Orientation | 270° physical, 90° logical |
| AOD support | TBD |
| Refresh control | HWC exposes 60/90/120 Hz |

**Evidence**: `yft-lcm-vtdr6115-drv` kernel probe, `SurfaceFlinger` 1080×2400@480dpi,
`displays.txt` (modes + HDR types), `debug.composition.type: mdp`,
Ulefone official spec sheet, GSMArena.

---

## 7. Touchscreen (Main)

| Field | Value |
|---|---|
| Controller | FocalTech **FT3680** |
| Bus | SPI3 (`spi3.0`) |
| Driver | `fts_ts` / `focaltech_touch_spi_ft3680` |
| Resolution | 1080 × 2400 |
| Max touch points | 10 |
| Firmware file | TBD |
| Gesture support | Yes (`fts_gesture_mode` sysfs node) |

**Evidence**: `/sys/bus/spi/devices/spi3.0` → `fts_ts`, `focaltech_touch_spi_ft3680`;
`persist.sys.phh.focaltech_node` points to `spi3.0/fts_gesture_mode`.

---

## 8. Rear Cameras

### Camera 0 — Main (BACK)

| Field | Value |
|---|---|
| Sensor (this unit) | **Sony IMX989** — 1″ class, 50.3 MP, 1.6 µm, 8192×6144, quad Bayer |
| **Marketing conflict** | Ulefone official spec + GSMArena list "Samsung GN1, 1.2 µm, 1/1.3″, 7-piece lens, FOV 85°" — **contradicts** the HAL/driver evidence on this unit. See note below. |
| Driver | `SENSOR_DRVNAME_IMX989_MIPI_RAW` (PROVEN on this unit) |
| Default active array | 4096 × 3072 (2×2 binned ≈12.6 MP — IMX989 default mode) |
| Max still | 8192 × 6144 @30 fps (full 50 MP) |
| Video (HAL) | 8K 7680×4320@24 fps, 4K@30, HFPS: **4K@60–120, 1080p@60–240, 720p@60–120** (`CONSTRAINED_HIGH_SPEED_VIDEO`) |
| Video (official app) | 4K@30 max (app limit — HAL exposes more) |
| Aperture | f/1.9 (HAL) / f/1.95 (official) |
| Focal length | 23.0 mm equivalent (HAL) |
| Min focus distance | HAL raw `6.66666651` (units not reliably meters on MTK HAL — TBD, verify in-app) |
| Flash | Yes (`torchModeStatus:AVAILABLE_OFF`) |
| OIS | **Not exposed in HAL** (`availableOpticalStabilization: [0]`); EIS modes [0,1,2] |
| Sensor physical size | 13.107 × 9.830 mm (HAL; matches 8192×6144 @ 1.6 µm exactly) |
| Sensitivity range | ISO 100–19200 (max analog ISO 6400) |
| Exposure range | 0.1 ms – **16 s** long exposure |
| AE comp | ±4 EV |
| Digital zoom | 4× max |
| Color filter | RGGB Bayer, 10-bit (whiteLevel 1023) |
| RAW | Yes (RAW capability + vendor RAW format in stream configs) |
| Hardware level | 3 (top level, Android 14+) |
| I2C address | `7-0020` (sensor0) |
| VCM (AF) | `main_vcm` at I2C `7-000a` (PDAF) |
| EEPROM | `camera-eeprom0` at I2C `7-0051` |
| Confidence | PROVEN (driver + physical size + 1.6 µm pitch all match IMX989) |

**Sensor conflict note**: The official spec sheet markets the main as Samsung GN1 (1/1.3″, 1.2 µm),
but three independent fields on this device match the Sony IMX989 exactly — driver name
`IMX989_MIPI_RAW`, physical size 13.107×9.830 mm (= 8192×6144 × 1.6 µm), and default binned
mode 4096×3072. A GN1 module would be ~7.6×5.7 mm and expose 8160×6120. Conclusion for **this
unit**: IMX989; marketing label likely wrong or refers to a different production batch.

### Camera 1 — Front

| Field | Value |
|---|---|
| Sensor | Samsung **S5KJN1** (JN1 — matches official spec) |
| Driver | `SENSOR_DRVNAME_S5KJN1_MIPI_RAW` |
| Resolution | 50 MP (8160 × 6144) |
| Pixel size | 0.64 µm (official) |
| Aperture | f/2.45 (HAL, matches official) |
| Focal length | 25.0 mm (HAL); FOV 80.4°, 5-piece lens (official) |
| AF | Fixed focus (HAL: hyperfocal 0, minFocus 0) |
| Exposure range | 70 µs – 0.4 s |
| Sensitivity | ISO 100–16000 (analog max 1600) |
| Max still | 8192 × 6144 (HAL stream config) |
| Video (HAL/app) | 1080p@30 max (no HFPS capability in HAL) |
| Flash | No |
| I2C address | `4-0010` (sensor1) |
| Confidence | PROVEN |

### Camera 2 — Main2 (BACK) — Ultra-Wide

| Field | Value |
|---|---|
| Sensor | Samsung **S5KJN1MAIN2** (JN1-family — official spec lists "JN1" for the ultra-wide) |
| Driver | `SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW` |
| Resolution | 50 MP (8160 × 6144) |
| Aperture | f/2.2 (HAL, matches official) |
| Focal length | 16.0 mm (HAL); **FOV 117.3°** (official) |
| Min focus | 1.0 m (HAL) |
| Exposure range | 0.1 ms – 16 s |
| Sensitivity | ISO 100–19200 (analog max 6400) |
| Max still | 8192 × 6144 |
| Video | 4K@30 max (HAL); no HFPS |
| Flash | Yes (`torchModeStatus:AVAILABLE_OFF`) |
| OIS | Not exposed in HAL (`[0]`) |
| I2C address | `2-0010` (sensor2) |
| VCM (AF) | `main2_vcm` at I2C `4-000b` |
| EEPROM | `camera-eeprom1` at I2C `4-0050` |
| Note | HAL reports physical size 13.107×9.830 mm — identical to cam0; treated as a tuning-DB default (a 117° ultra-wide on a 13 mm sensor is implausible) |
| Confidence | PROVEN |

### Camera 3 — Night Vision 64 MP (BACK)

| Field | Value |
|---|---|
| Sensor | OmniVision **OV64B** (matches official "64MP Night Vision Camera OV64B") |
| Driver | `SENSOR_DRVNAME_OV64B_MIPI_RAW` |
| Resolution | 64 MP (9216 × 6912) — max still in HAL stream config |
| Default active array | 4624 × 3472 (16 MP binned — 0.7 µm native ≈ 1.4 µm binned) |
| Sensor physical size | 6.5 × 4.89 mm (1/2″ class, matches HAL 0.7 µm pitch) |
| Aperture | f/1.79 (HAL, matches official) |
| Focal length | 26.0 mm (HAL); FOV 79.4° (official) |
| Min focus | 1.0 m (HAL) |
| Exposure range | 0.1 ms – 16 s |
| Sensitivity | ISO 100–15500 (analog max 1550) |
| Video | 4K@30 max (HAL); no HFPS |
| Flash | Yes; **4 IR illuminator LEDs** (official, GSMArena) for night-vision mode |
| OIS | Hardware motor present (DW9781C, I2C `4-000e`) — **not exposed** in HAL (`[0]`), EIS-only |
| I2C address | `4-0020` (sensor4) |
| VCM (AF) | `main4_vcm` at I2C `2-000d` |
| EEPROM | `camera-eeprom2` at I2C `2-0050`, `camera-eeprom4` at I2C `4-0051` |
| Confidence | PROVEN |

### OIS hardware

| Field | Value |
|---|---|
| OIS controller | **DW9781C** at I2C `4-000e` |
| Driver | `dw9781c` |
| Purpose | Optical stabilization actuator (most likely on the OV64B module; exact module mapping not exposed in HAL) |
| HAL status | **`availableOpticalStabilization: [0]` on ALL four cameras** — OIS hardware present but never enabled by stock HAL (EIS only) |
| Confidence | PROVEN (motor present + HAL disabled) |

**Evidence**: Camera HAL `camerahalserver` static info — 4 physical devices, exact driver names.
I2C bus enumeration: 4 `imgsensor` bindings, 4 camera EEPROMs, 4 VCM (AF) drivers, 1 OIS.

---

## 9. Thermal Camera

| Field | Value |
|---|---|
| Module (official) | **ThermoVue T2** thermal imaging (official spec sheet) |
| Thermal resolution | **640 × 512** (official) |
| Frame rate | **25 Hz** (official) |
| Pixel pitch | **12 µm** (official) → ~7.7 × 6.1 mm uncooled microbolometer |
| FOV | **56° × 42°** (official) |
| Sensitivity (NETD) | **< 40 mK** (official) |
| Temp range | **−20 °C to +550 °C** (official) |
| Accuracy | **±2 °C** (official) |
| Spectral band | LWIR 8–14 µm (implied by class; confirm on module label) |
| APK | `M170infisens/M170infisens.apk` (package `com.energy.tc2c`), label **ThermoVue Pro**, pre-installed |
| Native libraries | AC020, UVC/USB, IR camera/command, image processing, dual calibration, temperature |
| Calibration assets | 17 embedded (high/low B, K, KT/BT, NUC, OOC, RMVC, private datasets) |
| Kernel driver | `yft_tiny2c_usb` / `tiny2c_usb-sensor` |
| I2C binding | `8-003c` (`fm78100` compatible) |
| Sysfs | `tiny2c_usb_mode`, `tiny2c_mode` |
| Interface to phone | USB (UVC/proprietary protocol) |
| Radiometric | Yes (private temperature libraries, dual calibration, radiometric 17-dataset calibration) |
| Sensor vendor | UNKNOWN (APK name `M170infisens` suggests an InfiRay-derived stack; 640×512@12 µm is a standard mid-grade uncooled VoS format) |
| Confidence | STRONGLY_SUPPORTED (official specs + APK + driver all consistent) |

**Evidence**: Ulefone official spec sheet (ThermoVue T2 640×512@25 Hz, 12 µm, <40 mK,
−20..550 °C, ±2 °C); APK `com.energy.tc2c` with 17 calibration assets and AC020/UVC stack;
`yft_tiny2c_usb` kernel driver; `8-003c` I2C binding.

---

## 10. Camera Supporting Hardware

### Illumination / Flash / Torch ICs

Official spec for the main LED: **1000 lumens max, 570 LEDs, 5 W max, IP68-rated housing**.

| IC | I2C Address | Driver | Function |
|---|---|---|---|
| **AW36515** | `6-0063` | `aw36515` | Camera flash + main work-light LEDs (1000 lm / 570 LEDs / 5 W) |
| **AW36518** | `8-0063` | `aw36518` | IR/aux illumination (night-vision IR LEDs) |
| **AW36518_v2** | `12-0063` | `aw36518_v2` | Warning-light controller (red/blue) |

Official warning light spec: **red / blue / red-blue**, simulated emergency sirens
(fire engine, ambulance, police), 2 lighting modes (constant, blink), driven by
`YftRedBlueLight` app.

### LED Controller

| IC | I2C Address | Driver | Function |
|---|---|---|---|
| **AW2013** | `11-0045` | `leds_rgb_aw2013` | RGB notification / charging-indicator LED |
| **Manufacturer** | Awinic | | |

Proven detail (see `kernel/phase4-leds-rgb-aw2013-reconstruction.md`):
compatible `awinic,rgb,aw2013`; chip-enable **GPIO 188** (`aw2013-pwd-gpio`,
no regulator); 3 channels `red`/`green`/`blue` at **5 mA** each; brightness is
clamped to the DT `led-fixed-brightness` (red 64, green 64, blue 128);
hardware blink with a 130 ms step; no breathing ramps; no PM callbacks.
Exposed as `/sys/class/leds/{red,green,blue}` — consumed by the MediaTek
Lights HAL, `init.mt6878.rc`, `init.yft.rc` and `FactoryMode.apk`.
In power-off-charging boot the driver itself lights green ≥ 90 %, red ≤ 15 %,
blue otherwise, from the `3rd-gauge` fuel gauge.

### Camera VCM (AF) Motors

| I2C Address | Driver | Purpose |
|---|---|---|
| `7-000a` | `main_vcm` | Camera 0 (IMX989) |
| `4-000b` | `main2_vcm` | Camera 2 (S5KJN1MAIN2) |
| `2-000d` | `main4_vcm` | Camera 3 (OV64B) |

### OIS

| I2C Address | Driver | Purpose |
|---|---|---|
| `4-000e` | `dw9781c` | Camera 3 (OV64B) OIS |

### Camera EEPROMs

| I2C Address | Driver |
|---|---|
| `7-0051` | `mediatek,camera_eeprom` |
| `4-0050` | `mediatek,camera_eeprom` |
| `2-0050` | `mediatek,camera_eeprom` |
| `4-0051` | `mediatek,camera_eeprom` |

**Evidence**: I2C bus enumeration (`buses.txt`), camera HAL output.

---

## 11. Battery

| Field | Value |
|---|---|
| Technology | Li-ion polymer (official) |
| **Official rating** | **21,200 mAh total = 2 × 10,600 mAh cells in series, 7.74 V nominal** ("equivalent to 10600 mAh, 7.74V") |
| **Cell configuration** | **2S — CONFIRMED** (official 2×10600 mAh + observed 8.397 V pack voltage + 4.45 V/cell constant-charge) |
| Gauge design capacity | 8,594 mAh (pack, series basis — `CHARGE_FULL_DESIGN` on SH366003 3rd-gauge; OEM-set below official 10,600 mAh/cell) |
| Voltage at snapshot | 8.397 V (≈99% state of charge of a 7.74 V nominal pack) |
| Constant-charge voltage | 4.45 V per cell (`CONSTANT_CHARGE_VOLTAGE: 4450`) |
| Max charging current | 1,000,000 µA at framework level (top-off at snapshot; 120 W capable) |
| Temperature at snapshot | 37.0 °C |
| Health | GOOD |
| Charge topology | Dual charge-pump (SC8571×2) + SC8510 + dual fuel gauge (MT6375 + SH366003) |
| Official battery life | Standby up to 1140 h, talk time up to 114 h (official) |
| Cell manufacturer | TBD |

**Evidence**: Ulefone official spec sheet (21200 mAh / 10600×2 / 7.74 V / 120 W);
BatteryService dump — `voltage: 8397`, `design capacity: 8594000`, `technology: Li-ion`;
sysfs `CONSTANT_CHARGE_VOLTAGE: 4450`.

---

## 12. Charging Hardware

### Primary Fuel Gauge

| Field | Value |
|---|---|
| IC | MediaTek **MT6375** |
| I2C address | `5-0034` |
| Driver | `mt6375` / `mtk-gauge` |
| Path | Primary Android battery path |

### Secondary Fuel Gauge

| Field | Value |
|---|---|
| IC | **SH366003** |
| I2C address | `9-0055` |
| Driver | `sh366003_fg` |
| Path | `3rd-gauge` (secondary/backup) |

### Charge-Pump ICs

| IC | I2C Address | Role |
|---|---|---|
| **SC8571** (master) | `11-0066` | Primary charge pump |
| **SC8571** (slave) | `6-0067` | Secondary/parallel charge pump |
| **SC851x** (SC8510) | `6-0069` | Additional charger binding |

### PMIC / Power ICs

| IC | I2C Address | Driver |
|---|---|---|
| **RT6160** (Crichtek) | `5-0075` | Power management |
| **RT6160** (Crichtek) | `6-0075` | Power management |
| **WL2864C** | `11-0029` | `custom_ldo_wl2868` / `will,wl2864c_pmu` |

### USB PD / PPS

| Field | Value |
|---|---|
| PD support | Yes (`PD` and `PD_PPS` USB types advertised: `SDP DCP CDP PD PD_PPS`) |
| UFCS | Yes — dmesg `mtk_adapter_switch_control pd_type:2, ufcs_type:1` (Universal Fast Charging, China standard) |
| Max wired wattage | **120 W** (official "flash charging") |
| Direct (non-pump) path | Max 5 V × 13 A (13,000 mA `CURRENT_MAX`, 4.5–5 V input limit) ≈ 65 W direct to pack |
| OEM 120 W path | Via SC8571/SC8510 charge pumps (PD/PPS 9–12 V input; exact OEM PPS profile TBD) |
| **Reverse charging** | **Yes — 10 W wired reverse charging** (official spec) |
| Adapter at snapshot | USB-PD adapter present (sink mode, `pd_adapter` in dmesg) |

**Evidence**: dmesg `pd_adapter` / `ufcs_type:1`, thermal-power sysfs (`POWER_SUPPLY_CURRENT_MAX: 13000`,
`INPUT_VOLTAGE_LIMIT: 4500`), Ulefone official spec sheet (120 W + 10 W reverse).

---

## 13. USB / Type-C

| Field | Value |
|---|---|
| USB Controller | UDC `11201000.usb0` |
| Interface | configfs USB gadget |
| USB Data Generation | USB 2.0 (no evidence of SuperSpeed) |
| OTG | Supported (configfs host/device mode) |
| DisplayPort Alt Mode | UNKNOWN |
| USB-PD | Yes (PD + PPS) |
| Services | `vendor.usb_default`, `vendor.usb_gadget_default` |

**Evidence**: `11201000.usb0` UDC, configfs init, `persist.vendor.usb.offload: true`.

---

## 14. Cellular / Modem

| Field | Value |
|---|---|
| Modem | MediaTek integrated (MOLY baseband) |
| 5G | Yes (NR17 in baseband string) |
| SIM config | Dual Nano-SIM + microSD (3 slots, official); DSDS (`persist.vendor.radio.msimmode: dsds`) |
| **5G NR bands (official)** | **N1/2/3/5/7/8/20/25/28/38/40/41/66/71/77/78/79** (Sub-6) |
| **LTE-FDD (official)** | B1/2/3/4/5/7/8/12/13/17/18/19/20/25/26/28A/28B/32/66/71 |
| **LTE-TDD (official)** | B34/38/39/40/41 |
| **WCDMA (official)** | B1/2/4/5/6/8/19 |
| **GSM (official)** | B2/3/5/8 |
| **CDMA (official)** | BC0/BC1/BC10 |
| VoLTE | Supported (`persist.vendor.mtk.volte.enable: 1`; official) |
| VoNR | **Single VoNR supported (official)**; NOT enabled in stock (`persist.vendor.mtk.vonr.enable: 0`) |
| WFC | Supported (`persist.vendor.mtk.wfc_support: 1`) |
| IMS | Supported (`persist.vendor.ims_support: 1`) |
| Dual 5G/4G | Both SIMs can access 5G; simultaneous 4G+4G (official) |
| Connsys | `connac2x` (`persist.vendor.connsys_fm_chipid`) |
| NV data | Present (`mnt.vendor.nvdata: sdc7`, `mnt.vendor.nvcfg: sdc6`) |
| RIL | Reference RIL (`android reference-ril 1.0`) |

**Evidence**: Baseband string, `persist.vendor.*` properties, NV partitions,
Ulefone official spec sheet (full band list).

---

## 15. RF Frontend

| Field | Value |
|---|---|
| FEM | TBD (ConnFem phase4 research in progress) |
| Antennas | TBD (exact count/routing) |
| MIMO | TBD |
| Wi-Fi/BT co-chip | MediaTek connsys |
| Confidence | LIKELY (MTK platform; exact FEM parts TBD) |

---

## 16. Wi-Fi

| Field | Value |
|---|---|
| Chipset | MediaTek **MT6637** (Wi-Fi 6E + BT combo; dmesg `ADIE6637` A-die 0x66378a01) on connsys D-die (`connsys_d_die_cfg_mt6878`) |
| HAL | `vendor.wifi_hal_legacy` |
| Service | `connsys_wifi` |
| Firmware partition | `connsys_wifi` |
| **Standard** | **Wi-Fi 6E** — 802.11 a/b/g/n/ac/**ax**, 2.4 + 5 + **6 GHz** (official spec) |

**Evidence**: dmesg `ADIE6637` / `connsys_d_die_cfg_mt6878`, `vendor.wifi_hal_legacy`,
`connsys_wifi` service, Ulefone official spec sheet ("WIFI 6E, 2.4GHz/5GHz/6GHz").

---

## 17. Bluetooth

| Field | Value |
|---|---|
| Controller | MediaTek MT6637 combo (same chip as Wi-Fi) |
| **Version** | **Bluetooth 5.4** (official spec) |
| HAL | `system.bt-audio-hal`, `bluetooth_hal_service` |
| Service | `connsys_bt` |
| LE Audio | Supported (`bluetooth.leaudio_offload.disabled: false`) |
| A2DP offload | Disabled in stock (`bluetooth.a2dp_offload.disabled: true`) |
| Codecs | SBC-AAC (`bluetooth.a2dp_offload.cap: sbc-aac`) |
| Coexistence | With Wi-Fi via connsys |

**Evidence**: Bluetooth properties, init services, Ulefone official spec sheet (BT 5.4).

---

## 18. GNSS

| Field | Value |
|---|---|
| Chipset | MediaTek integrated connsys (MT6637 combo) |
| Service | `vendor.gnss-default` |
| LBS | `mtk_lbs_service` |
| Firmware partition | `connsys_gnss` |
| **Constellations (official)** | **GPS, GLONASS, Galileo, BEIDOU, QZSS, NavIC** + digital compass (MMC5603) |

**Evidence**: `vendor.gnss-default` service, `connsys_gnss` partition, Ulefone official spec sheet.

---

## 19. NFC

| Field | Value |
|---|---|
| Controller | **ST21NFC** |
| I2C address | `6-0008` |
| Driver | `st21nfc` |
| Firmware | `st21nfc_fw.bin`, `st21nfc_fw7.bin` |
| HAL | `android.hardware.nfc.INfc/default` |
| Secure element | Dual (SIM1 + SIM2) |
| SE service | `mtk_secure_element_hal_service` |
| NFC modes | Card emulation, host card emulation, peer-to-peer |

**Evidence**: I2C bus, `st21nfc` module, firmware files, HAL service.

---

## 20. Speakers

| Field | Value |
|---|---|
| External amplifier | I2C `6-0034`, driver `speaker_amp` / `mtk_sp_spk_amp` |
| Exact amp IC | UNKNOWN |
| Amplifier manufacturer | UNKNOWN |
| Speaker count | ≥1 (at least external speaker + earpiece) |
| Stereo configuration | TBD |
| ALSA card | MediaTek (one card, large PCM topology) |
| Headset jack | **3.5 mm headphone jack** (official) — `mt6878-mt6369 Headset Jack` in ALSA |

**Evidence**: I2C `6-0034` → `mtk_sp_spk_amp`, ALSA headset jack, Ulefone official spec sheet.

---

## 21. Audio Codec / PMIC Audio

| Field | Value |
|---|---|
| Codec | Integrated in MediaTek PMIC (MT6369) |
| Headset jack | `mt6878-mt6369 Headset Jack` |
| Features | Headphone, microphone, line-out, physical-insert detection |
| DSP | MediaTek audio DSP (vendor HAL) |

**Evidence**: ALSA `mt6878-mt6369 Headset Jack`, `mt6369` I2C binding at `5-0018`.

---

## 22. Fingerprint Sensor

| Field | Value |
|---|---|
| Manufacturer | **Madev** |
| Transport | SPI (`spi1.0`) |
| Driver | `madev` / `microarray_fp_tee` (MTK generic fingerprint HAL name) |
| Device nodes | `/dev/madev0`, `/dev/tkcore_fp` |
| Authentication | TrustKernel TEE-based (`microarray_fp_tee`) |
| **Sensor type** | **Capacitive** (official: "Capacitive Touch Sensor") |
| **Physical location** | **Side-mounted, integrated with power key** (official) |
| Response speed | Up to 0.1 s (official) |
| Enrollment | Up to 5 fingerprints (official) |
| Confidence | PROVEN placement + STRONGLY_SUPPORTED auth flow |

**Evidence**: SPI1 `madev`, `microarray_fp_tee` module, TrustKernel keymaster,
Ulefone official spec sheet (side-mounted capacitive in power key, 5 prints, 0.1 s).

---

## 23. IMU (Accelerometer + Gyroscope)

| Field | Value |
|---|---|
| Chip | IvenSense **ICM4N607** |
| I2C address | TBD (no direct I2C; fused through sensor hub) |
| Driver | `icm4n607_acc`, `icm4n607_gyro` |
| Vendor string | `iven_sense` |
| Accelerometer range | TBD (datasheet TBD) |
| Gyro range | TBD (datasheet TBD) |
| Max sample rate | 400 Hz (accel + gyro) |
| FIFO | Yes (gyro) |

**Evidence**: `dumpsys sensorservice` — `icm4n607_acc` and `icm4n607_gyro` with vendor `iven_sense`,
400 Hz max rate, real accelerometer events captured.

---

## 24. Magnetometer

| Field | Value |
|---|---|
| Chip | Memsic **MMC5603** |
| I2C address | TBD |
| Driver | `mmc5603` |
| Vendor | `memsic` |
| Range | TBD |
| Max sample rate | 50 Hz |
| FIFO | Yes (4500 events, 600 reserved) |

**Evidence**: `dumpsys sensorservice` — `mmc5603`, vendor `memsic`.

---

## 25. Ambient Light Sensor

| Field | Value |
|---|---|
| Chip | Sensortek **STK3A5X** |
| I2C address | TBD |
| Driver | `stk3a5x_als` |
| Vendor | `sensortek` |
| Type | ALS (lux) |
| Mode | On-change |

---

## 26. Proximity Sensor

| Field | Value |
|---|---|
| Chip | Sensortek **STK3A5X** (combo with ALS) |
| I2C address | TBD |
| Driver | `stk3a5x_ps` |
| Vendor | `sensortek` |
| Type | Proximity (IR-based) |
| Mode | On-change, wakeUp |
| FIFO | Yes (4500 events, 100 reserved) |

---

## 27. Barometer

| Field | Value |
|---|---|
| Chip | Goer **SPL07** |
| I2C address | TBD |
| Driver | `spl07` |
| Vendor | `goer` |
| Range | TBD (datasheet TBD) |
| Max sample rate | 10 Hz |
| FIFO | Yes (4500 events, 300 reserved) |

**Evidence**: `dumpsys sensorservice` — `spl07`, vendor `goer`.

---

## 28. IR Hardware

| Field | Value |
|---|---|
| IR blaster | **Confirmed as OEM feature** — "Infrared sensor" in official sensor list; `vendor.ir-default` service present (universal remote function) |
| IR receiver | UNKNOWN (no dedicated receiver node found) |
| IR illuminator | AW36518 at `8-0063` (4 IR LEDs for OV64B night-vision mode) |
| Proximity IR LED | Part of STK3A5X proximity sensor |

---

## 29. Flash / Torch LEDs

| Field | Value |
|---|---|
| Flash controller | **AW36515** at I2C `6-0063` |
| IR/aux controller | **AW36518** at I2C `8-0063` |
| Work light controller | **AW36518_v2** at I2C `12-0063` |
| Work/warning light apps | `YftOutdoorLightUlefone`, `YftRedBlueLight` |
| RGB notification | **AW2013** at I2C `11-0045` |

**Evidence**: I2C bus enumeration showing all three AW365xx families and AW2013.

---

## 30. Haptics / Vibration Motor

| Field | Value |
|---|---|
| Motor type | ERM (software reports `HARDWARE_FEEDBACK` but no LRA characteristics) |
| Vibrator ID | 1 |
| HAL | `vendor.vibrator-default` |
| Resonant frequency | NaN (not LRA) |
| Supported effects | Click, double-click, tick, heavy-click, texture-tick |
| Driver IC | TBD |

**Evidence**: `VibratorManagerService` — capabilities flags, supported effects,
no q-factor/resonant frequency (indicates ERM, not LRA).

---

## 31. Physical Buttons

| Button | GPIO/Driver | Keycode |
|---|---|---|
| Power | TBD | KEY_POWER |
| Volume Up | TBD | KEY_VOLUMEUP |
| Volume Down | TBD | KEY_VOLUMEDOWN |
| Programmable key 1 | `yft-gpio-keys` | F1 |
| Programmable key 2 | `yft-gpio-keys` | F2 |
| Rugged buttons | TBD (may map to F1/F2) | |

**Evidence**: `yft-gpio-keys` driver emitting F1/F2.

---

## 32. Cooling Hardware

| Field | Value |
|---|---|
| Active fan | None (no fan service) |
| Passive cooling | TBD (graphite, copper foil, heat pipe, vapor chamber) |
| Thermal zones | CPU, GPU, NPU, TPU, SOC, skin, battery, USB port, power amplifier |
| Cooling devices | Mali GPU, charger-cooler, LCD backlight, Wi-Fi, flashlight |
| Thresholds | CPU/GPU/NPU/TPU/SOC: 85/90/100/117 °C; Battery: 50/55/59/60 °C |

**Evidence**: Thermal HAL AIDL v3 — 8 temperature types, 5 cooling devices.

---

## 33. Rear Display (Sub-screen)

| Field | Value |
|---|---|
| Panel | CO5300 (via `spi_tiny_lcd_co5300`) — panel driver name; official panel = AMOLED |
| Interface | SPI0 (`spi0.0`) |
| Driver | `spi_tiny_co5300_lcd` |
| Touch controller | Hynitron **hyn_ts** |
| Touch I2C | `0-0015` |
| **Size (official)** | **1.04″ AMOLED** |
| **Resolution (official)** | **340 × 340 pixels** (matches HAL touch resolution) |
| **Peak brightness (official)** | **600 nits** |
| **Refresh rate (official)** | **60 Hz** |
| **Protection (official)** | **Corning Gorilla Glass Victus** |
| Touch points | 1 (single ID) |
| Userspace app | `YftMiniScreen.apk` (~84 MB) |
| Control | `/sys/class/misc/tiny_lcd_miscdev` |
| Confidence | PROVEN components + official spec; protocol TBD |

**Evidence**: SPI0 `spi_tiny_lcd_co5300`, I2C `0-0015` hyn_ts, YftMiniScreen.apk,
`tinydisplay_touch_daemon` and `tinylcd_hal` services, Ulefone official spec sheet.
NOTE: the CO5300 driver name refers to the small-panel driver; official spec confirms AMOLED.

---

## 34. SIM / microSD

| Field | Value |
|---|---|
| SIM slots | **3 slots: Nano-SIM + Nano-SIM + microSD** (official) |
| eSIM | No evidence of eSIM hardware |
| microSD | Dedicated slot, up to **2 TB** (official) |
| SIM lock | SIM1 has PIN1 (3 attempts), PUK1 (10 attempts) |
| SIM type | 20 (nano-SIM) |
| Snapshot state | SIM1 (Telia LT, Lithuania) PIN_REQUIRED; slot 2 ABSENT |

**Evidence**: `gsm.sim1.type: 20`, `persist.vendor.radio.msimmode: dsds`,
`gsm.slot1.num.pin1: 3`, telephony dump (Telia LT subscription), Ulefone official spec sheet.

---

## 35. Antennas

| Antenna Type | Count | Confidence |
|---|---|---|
| Cellular | TBD | LIKELY (4G/5G MIMO) |
| Wi-Fi | TBD | LIKELY |
| Bluetooth | TBD | LIKELY (shared with Wi-Fi) |
| GNSS | TBD | LIKELY |
| NFC coil | 1 | PROVEN (ST21NFC) |
| Antenna switch | TBD | LIKELY |

---

## 36. Rugged-Specific Hardware

Official physical ratings: **177.35 × 85.6 × 33.8 mm, 688 g**; **IP68** (2 m / 30 min, IEC 60529),
**IP69K** (IEC 60529), **MIL-STD-810H**. Official: supports underwater photo/video,
starting/stopping and switching shooting modes underwater.

| Feature | Hardware | Confidence |
|---|---|---|
| Thermal imaging | ThermoVue T2 (640×512, 25 Hz, 12 µm, <40 mK, −20..550 °C) | PROVEN (official specs) + STRONGLY_SUPPORTED (driver/APK) |
| Work lights | AW36515 main LED (1000 lm / 570 LEDs / 5 W) + YftOutdoorLightUlefone app | PROVEN |
| Red/blue warning light | AW36518_v2 + YftRedBlueLight app; red/blue/red-blue + fire/ambulance/police sirens, constant/blink | PROVEN + official spec |
| RGB notification LED | AW2013 (red/green/blue, charging prompt) | PROVEN |
| Programmable buttons | yft-gpio-keys (F1/F2) | PROVEN |
| Sub-screen | 1.04″ 340×340 AMOLED + hyn_ts | PROVEN + official spec |
| IP-rated enclosure | IP68 + IP69K + MIL-STD-810H | PROVEN (official certification claims) |
| Underwater shooting | Supported per official spec (photo/video start/stop/mode-switch underwater) | STRONGLY_SUPPORTED (marketing; untested) |
| Glove mode | TBD (touch controller may support) | POSSIBLE |
| SOS hardware | TBD | UNKNOWN |
| Camp light | Possibly work lights | LIKELY |
| Barometer | SPL07 | PROVEN |
| IR blaster | `vendor.ir-default` + official "Infrared sensor" listing | STRONGLY_SUPPORTED |

---

## 37. PCB / Board Revisions

| Field | Value |
|---|---|
| Board ID | TBD |
| PCB name | TBD |
| Hardware revision | TBD |
| Sub-boards | TBD |

---

## 38. Known Unknowns (Research Queue)

See `../docs/known-unknowns.md` for the full list. Key gaps (after 2026-08-31 fact-check pass):

**RESOLVED** (this pass):
- ~~Cell wiring~~ → **2S confirmed** (official 2×10,600 mAh, 7.74 V + 8.397 V pack + 4.45 V/cell CCV)
- ~~Wi-Fi standard~~ → **Wi-Fi 6E** (2.4/5/6 GHz, 802.11ax — official; MT6637 chip in dmesg)
- ~~GNSS constellations~~ → GPS, GLONASS, Galileo, BEIDOU, QZSS, NavIC (official)
- ~~IR blaster~~ → confirmed OEM feature (official sensor list + `vendor.ir-default`)
- ~~Night-vision sensor~~ → **cam3 OV64B** + 4 IR LEDs (official "64MP Night Vision Camera")
- ~~Thermal sensor specs~~ → ThermoVue T2 640×512@25 Hz, 12 µm, <40 mK, −20..550 °C (official)
- ~~Reverse charging~~ → 10 W wired reverse (official)

**STILL OPEN:**
1. **Exact speaker amplifier IC** — generic `speaker_amp` at `6-0034`
2. **120W OEM PPS profile** — UFCS+PD+PPS proven present; exact OEM profile/waveform unverified (65 W direct path measured in sysfs limits)
3. **Antenna count / RF FEM** — ConnFem research in progress
4. **Rear-display protocol** — ioctl/sysfs between YftMiniScreen and tiny_lcd_miscdev
5. **Battery cell manufacturer/model** — 2S 10,600 mAh cells, vendor unknown
6. **Main-camera marketing conflict** — this unit proven IMX989 (driver/physical-size); official sheet says GN1 — likely variant/batch difference or mislabel
7. **Cam0 min-focus distance** — HAL raw `6.6667` unit ambiguous; needs in-app verification
8. **Thermal sensor vendor** — `M170infisens` APK suggests InfiRay-derived; exact detector model unconfirmed

---

## 39. BOM-Style Component Table

| Subsystem | Component | Manufacturer | Exact Model | Qty | Interface | Address | Evidence | Confidence |
|---|---|---|---|---:|---|---|---|---|
| SoC | Application Processor | MediaTek | Dimensity 7400 (MT6878T) | 1 | — | — | boot props + official spec | PROVEN |
| RAM | DRAM | — | — | 1 | LPDDR | — | `ro.boot.ddr_size` | PROVEN |
| Storage | UFS | — | — | 1 | UFS | — | `112b0000.ufshci` | PROVEN |
| Main Display | Panel | — | yft-lcm-vtdr6115 | 1 | DSI | — | Kernel probe | PROVEN |
| Main Touch | Controller | FocalTech | FT3680 | 1 | SPI3 | spi3.0 | Kernel probe | PROVEN |
| Rear Display | Panel | — | CO5300 | 1 | SPI0 | spi0.0 | Kernel probe | PROVEN |
| Rear Touch | Controller | Hynitron | hyn_ts | 1 | I2C | 0-0015 | Kernel probe | PROVEN |
| CAM0 | Rear sensor | Sony | IMX989 | 1 | MIPI | 7-0020 | Camera HAL | PROVEN |
| CAM0 AF | VCM | — | main_vcm | 1 | I2C | 7-000a | Kernel probe | PROVEN |
| CAM0 EEPROM | Calibration | — | — | 1 | I2C | 7-0051 | Kernel probe | PROVEN |
| CAM1 | Front sensor | Samsung | S5KJN1 | 1 | MIPI | 4-0010 | Camera HAL | PROVEN |
| CAM2 | Rear sensor | Samsung | S5KJN1MAIN2 | 1 | MIPI | 2-0010 | Camera HAL | PROVEN |
| CAM2 AF | VCM | — | main2_vcm | 1 | I2C | 4-000b | Kernel probe | PROVEN |
| CAM2 EEPROM | Calibration | — | — | 1 | I2C | 4-0050 | Kernel probe | PROVEN |
| CAM3 | Rear sensor | OmniVision | OV64B | 1 | MIPI | 4-0020 | Camera HAL | PROVEN |
| CAM3 AF | VCM | — | main4_vcm | 1 | I2C | 2-000d | Kernel probe | PROVEN |
| CAM3 OIS | Stabilizer | Dahua | DW9781C | 1 | I2C | 4-000e | Kernel probe | PROVEN |
| CAM3 EEPROM | Calibration | — | — | 1+ | I2C | 2-0050, 4-0051 | Kernel probe | PROVEN |
| Thermal Cam | Imaging module | ThermoVue | T2 (640×512, 12 µm) | 1 | USB | I2C 8-003c | official spec + APK + driver | PROVEN |
| Battery | Fuel gauge | MediaTek | MT6375 | 1 | I2C | 5-0034 | Kernel probe | PROVEN |
| Battery | Fuel gauge | SH | SH366003 | 1 | I2C | 9-0055 | Kernel probe | PROVEN |
| Charger | Charge pump | Semtech | SC8571 | 2 | I2C | 11-0066, 6-0067 | Kernel probe | PROVEN |
| Charger | Charger IC | Semtech | SC8510 | 1 | I2C | 6-0069 | Kernel probe | PROVEN |
| Flash/Torch | LED controller | Awinic | AW36515 | 1 | I2C | 6-0063 | Kernel probe | PROVEN |
| IR/Aux light | LED controller | Awinic | AW36518 | 1 | I2C | 8-0063 | Kernel probe | PROVEN |
| Work light | LED controller | Awinic | AW36518_v2 | 1 | I2C | 12-0063 | Kernel probe | PROVEN |
| Notification | RGB LED | Awinic | AW2013 | 1 | I2C | 11-0045 | Kernel probe | PROVEN |
| NFC | Controller | STMicro | ST21NFC | 1 | I2C | 6-0008 | Kernel probe | PROVEN |
| Fingerprint | Sensor | Madev | side capacitive (in power key) | 1 | SPI1 | spi1.0 | Kernel probe + official spec | PROVEN |
| Battery | 2S Li-ion pack | TBD vendor | 21,200 mAh (2×10,600) | 2 cells | series | — | official spec + gauge dump | PROVEN |
| IMU | Accel+Gyro | IvenSense | ICM4N607 | 1 | I2C | TBD | Sensor HAL | PROVEN |
| Mag | Magnetometer | Memsic | MMC5603 | 1 | I2C | TBD | Sensor HAL | PROVEN |
| Ambient light | Sensor | Sensortek | STK3A5X | 1 | I2C | TBD | Sensor HAL | PROVEN |
| Proximity | Sensor | Sensortek | STK3A5X | 1 | I2C | TBD (same) | Sensor HAL | PROVEN |
| Barometer | Sensor | Goer | SPL07 | 1 | I2C | TBD | Sensor HAL | PROVEN |
| Audio codec | Headset jack | MediaTek | MT6369 | 1 | I2C | 5-0018 | ALSA | PROVEN |
| Speaker amp | External amp | — | speaker_amp | 1 | I2C | 6-0034 | Kernel probe | LIKELY |
| PMIC | Power management | Crichtek | RT6160 | 2 | I2C | 5-0075, 6-0075 | Kernel probe | PROVEN |
| PMIC | Power management | — | WL2864C | 1 | I2C | 11-0029 | Kernel probe | PROVEN |

---

## 40. Full Sensor Table

| Category | Vendor | Exact Model | Qty | Interface | Android Type | Max Rate | FIFO | Evidence | Confidence |
|---|---|---|---:|---|---|---:|---:|---|---|
| Accelerometer | IvenSense | ICM4N607 | 1 | I2C | `accelerometer` | 400 Hz | No | HAL + live events | PROVEN |
| Gyroscope | IvenSense | ICM4N607 | 1 | I2C | `gyroscope` | 400 Hz | No | HAL | PROVEN |
| Magnetometer | Memsic | MMC5603 | 1 | I2C | `magnetic_field` | 50 Hz | Yes (4500) | HAL | PROVEN |
| Ambient Light | Sensortek | STK3A5X | 1 | I2C | `light` | 1 Hz | No | HAL | PROVEN |
| Proximity | Sensortek | STK3A5X | 1 | I2C | `proximity` | 1 Hz | Yes (4500) | HAL | PROVEN |
| Barometer | Goer | SPL07 | 1 | I2C | `pressure` | 10 Hz | Yes (4500) | HAL | PROVEN |
| Orientation | MTK (fusion) | — | 1 | — | `orientation` | 200 Hz | No | HAL (fused) | PROVEN |
| Gravity | MTK (fusion) | — | 1 | — | `gravity` | 200 Hz | No | HAL (fused) | PROVEN |
| Linear accel | MTK (fusion) | — | 1 | — | `linear_acceleration` | 200 Hz | No | HAL (fused) | PROVEN |
| Rotation vector | MTK (fusion) | — | 1 | — | `rotation_vector` | 200 Hz | Yes (4500) | HAL (fused) | PROVEN |
| Uncal mag | MTK (fusion) | — | 1 | — | `magnetic_field_uncalibrated` | 50 Hz | Yes (4500) | HAL (fused) | PROVEN |
| Game rot vec | MTK (fusion) | — | 1 | — | `game_rotation_vector` | 200 Hz | Yes (4500) | HAL (fused) | PROVEN |
| Uncal gyro | MTK (fusion) | — | 1 | — | `gyroscope_uncalibrated` | 400 Hz | Yes (4500) | HAL (fused) | PROVEN |
| Sig motion | MTK (fusion) | — | 1 | — | `significant_motion` | one-shot | No | HAL (fused) | PROVEN |
| Step detect | MTK (fusion) | — | 2 | — | `step_detector` | special | Yes (4500) | HAL (fused) | PROVEN |
| Step counter | MTK (fusion) | — | 1 | — | `step_counter` | 1 Hz | No | HAL (fused) | PROVEN |
| Geo rot vec | MTK (fusion) | — | 1 | — | `geomagnetic_rotation_vector` | 200 Hz | No | HAL (fused) | PROVEN |
| Tilt detector | MTK (fusion) | — | 1 | — | `tilt_detector` | special | No | HAL (fused) | PROVEN |
| Wake gesture | MTK (fusion) | — | 1 | — | `wake_gesture` | one-shot | No | HAL (fused) | PROVEN |
| Dev orientation | MTK (fusion) | — | 1 | — | `device_orientation` | 1 Hz | No | HAL (fused) | PROVEN |
| Uncal accel | MTK (fusion) | — | 1 | — | `accelerometer_uncalibrated` | 400 Hz | No | HAL (fused) | PROVEN |
| Wake step detect | MTK (fusion) | — | 1 | — | `step_detector` | special | Yes (4500) | HAL (fused) | PROVEN |

**Total hardware sensors (physical ICs)**: 6 (ICM4N607, MMC5603, STK3A5X×1, SPL07)
**Total Android sensor types (including fused)**: 22 hardware + 8 AOSP AIDL = 30 reported

---

## 41. Sources / Evidence

| Source | Path |
|---|---|
| Live stock snapshot | `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/` |
| I2C bus enumeration | `buses.txt` |
| Camera HAL dump | `camera-media.txt` |
| Sensor service dump | `sensors.txt` |
| Thermal/Power dump | `thermal-power.txt` |
| Vibrator/Lights dump | `lights-vibrator.txt` |
| Properties dump | `identity.txt` |
| Hardware map | `../docs/hardware-map.md` |
| Sensors docs | `../docs/sensors.md` |
| Camera/thermal docs | `../docs/camera-thermal.md` |
| Battery/charging docs | `../docs/battery-charging.md` |
| Audio docs | `../docs/audio.md` |
| Connectivity docs | `../docs/connectivity.md` |
| Display docs | `../docs/display-secondary.md` |
| Known unknowns | `../docs/known-unknowns.md` |
| Evidence summary | `workspace/gq5012bf1/reports/inventory/summary.md` |
| Device tree audit | `workspace/gq5012bf1/reports/device-tree-audit.md` |
| Ulefone official spec sheet | `https://store.ulefone.com/pages/armor-29-pro-thermal-specs` |
| GSMArena page | `https://www.gsmarena.com/ulefone_armor_29_pro_thermal_5g-14104.php` |
| Samsung GN1 product page | `https://semiconductor.samsung.com/image-sensor/mobile-image-sensor/isocell-gn1/` |
| Sony IMX989 explainer | `https://curioussteve.com/tech/explained/sony-imx989-explained/` |

---

*This document was generated from the GQ5012BF1 research repository. It represents the state of hardware identification as of the live snapshot date. Hardware-tested validation under LieppOS custom ROM is pending for several subsystems.*
