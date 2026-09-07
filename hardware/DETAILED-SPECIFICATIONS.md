# DETAILED HARDWARE SPECIFICATIONS — Ulefone Armor 29 Pro Thermal (GQ5012BF1)

> Comprehensive datasheet-level specifications for every identified hardware component.
> Sources: web research, kernel driver evidence, sensor HAL dump, camera HAL output,
> and manufacturer datasheets (where available).
>
> **Evidence sources**:
> - Live stock snapshot (`live-stock-adb-20260831-115649/`)
> - I2C/SPI bus enumeration, camera HAL, sensor service dump
> - Web search verification and datasheet lookups

---

## A. SYSTEM-ON-CHIP: MediaTek Dimensity 7400 (MT6878T)

> **FACT-CHECK NOTE (2026-08-31)**: This section was originally written as
> "Dimensity 8300-Ultra / A715+A510 / Mali-G615 MP6". That was **wrong**.
> Ulefone's official spec sheet lists the SoC as **MediaTek Dimensity 7400
> (CPU: MT6878T)**, corroborated by GSMArena and by the kernel platform strings
> (`ro.hardware: mt6878`, `connsys_d_die_cfg_mt6878`). The Dimensity 7400 is a
> Dimensity-8300-family derivative that lives on the MT6878 kernel platform,
> which explains why every device string says `mt6878`. It has **Cortex-A78**
> (not A715) cores and a **Mali-G615 MC2** (not MP6) GPU.

### A.1 SoC Overview

| Field | Specification |
|---|---|
| **Marketing name** | MediaTek **Dimensity 7400** (Ulefone official spec) |
| **Platform variant** | **MT6878T** (official spec; MT6878 kernel platform) |
| **Process node** | TSMC 4 nm (N4) |
| **Transistor count** | TBD |
| **Die size** | TBD |
| **CPU architecture** | ARMv8.2-A (Cortex-A78 big cores, ARMv8.2) |
| **CPU cores** | 4× Cortex-**A78** + 4× Cortex-**A55** (big.LITTLE) |
| **Max clock speed** | A78: **2.6 GHz**, A55: **2.0 GHz** |
| **GPU** | **Arm Mali-G615 MC2** @ up to 1400 MHz |
| **GPU features** | Vulkan 1.3, OpenGL ES 3.2, OpenCL 2.2 (G615 = Valhall 3rd-gen class) |
| **ISP** | MTK ISP-DIP-V4L2 (v4) |
| **NPU/APU** | MediaTek NPU (official spec: "MediaTek NPU 655"); NPU thermal zone present |
| **Video encode** | HAL exposes 8K@24 + 4K@120 + 1080p@240 streams (ISP capability; app caps at 4K@30) |
| **Video decode** | TBD (MediaCodec profile dump needed) |
| **Memory interface** | LPDDR5 (TBD: LPDDR5 or LPDDR5X) |
| **Max RAM bandwidth** | TBD |
| **Max RAM capacity** | 16 GB (this unit) |
| **Storage interface** | UFS (version TBD) |
| **L3 Cache** | TBD |
| **5G modem** | MTK integrated (NR17 MOLY) |
| **AI accelerator** | MediaTek NPU (NPU 655) |

### A.2 Modem

| Field | Specification |
|---|---|
| **Modem type** | MTK integrated 5G modem (MOLY NR17) |
| **Standards** | 5G NR, 4G LTE, 3G, 2G |
| **LTE category** | TBD (not officially stated) |
| **5G bands (official)** | N1/2/3/5/7/8/20/25/28/38/40/41/66/71/77/78/79 (Sub-6) |
| **LTE-FDD (official)** | B1/2/3/4/5/7/8/12/13/17/18/19/20/25/26/28A/28B/32/66/71 |
| **LTE-TDD (official)** | B34/38/39/40/41 |
| **WCDMA (official)** | B1/2/4/5/6/8/19 |
| **GSM (official)** | B2/3/5/8 |
| **CDMA (official)** | BC0/BC1/BC10 |
| **VoLTE** | Yes (supported, official) |
| **VoNR** | Single VoNR supported (official); disabled in stock ROM |
| **Wi-Fi calling** | Yes (WFC supported) |
| **Dual SIM** | Both SIMs can access 5G; dual 4G+4G (official) |

### A.3 Connsys (Wi-Fi/BT/GNSS)

| Field | Specification |
|---|---|
| **Combo chip** | **MediaTek MT6637** (dmesg `ADIE6637`, A-die 0x66378a01) on connsys D-die (`connsys_d_die_cfg_mt6878`) |
| **Chip ID** | `0x6878` (persist.vendor.connsys.chipid) |
| **Wi-Fi standard** | **Wi-Fi 6E — 802.11 a/b/g/n/ac/ax** (official spec) |
| **Wi-Fi frequency** | **2.4 + 5 + 6 GHz** (official spec) |
| **Wi-Fi MIMO** | 2×2 MIMO (typical MT6637) |
| **Bluetooth** | **BT 5.4** (official), LE Audio support, SBC/AAC (stock codec cap) |
| **GNSS** | **GPS, GLONASS, Galileo, BEIDOU, QZSS, NavIC** (official) + digital compass (MMC5603) |
| **GNSS accuracy** | TBD |

**Evidence**: `ro.boot.hardware: mt6878`, `ro.hardware: mt6878`,
`persist.vendor.connsys.chipid: 0x6878`, `ro.bionic.cpu_variant: cortex-a55`,
`ro.boot.ddr_size: 17179869184` (16 GB), kernel `media_device_info topology[0]` (ISP-DIP-V4L2),
dmesg `ADIE6637` / `connsys_d_die_cfg_mt6878`, Ulefone official spec sheet (Dimensity 7400,
MT6878T, Wi-Fi 6E 2.4/5/6 GHz, BT 5.4, GNSS 6 constellations), GSMArena.

---

## B. RAM: 16 GB LPDDR5 (X)

| Field | Specification |
|---|---|
| **Capacity** | 16 GB (17,179,869,184 bytes) |
| **RAM expansion** | Up to **+16 GB** storage-backed "Dynamic RAM Expansion" (official spec) |
| **Type** | LPDDR5 (TBD: LPDDR5 or LPDDR5X) |
| **Max speed** | TBD (MT6878 platform: LPDDR5X-7500 class) |
| **Bandwidth** | TBD |
| **Manufacturer** | TBD (Samsung/Micron/SK Hynix — unmarked in software) |
| **Part number** | TBD |
| **Package** | WLP (Wafer-Level Package) |
| **Configuration** | Single-die (16 GB single rank) |

**Evidence**: `ro.boot.ddr_size: 17179869184`, Ulefone official spec sheet (16 GB + RAM expansion).

---

## C. STORAGE: UFS

| Field | Specification |
|---|---|
| **Interface** | UFS (version TBD) |
| **Host controller** | `112b0000.ufshci` |
| **Boot path** | `112b0000.ufshci` (`ro.boot.boot_devices`) |
| **Block device** | `sdc` (UFS device) |
| **RPMB** | Present (`ro.boot.rpmb_status: 1`) — Replay Protected Memory Block |
| **Read speed** | TBD |
| **Write speed** | TBD |
| **Capacity** | **512 GB** (16 GB + 512 GB SKU, official spec) |
| **microSD** | Dedicated slot, up to **2 TB** (official spec) |
| **Manufacturer** | TBD |
| **Part number** | TBD |

**Evidence**: `ro.boot.boot_devices: bootdevice, soc/112b0000.ufshci`,
`ro.boot.rpmb_status: 1`, `dev.mnt.rootdisk.data: sdc`.

---

## D. MAIN DISPLAY: 6.67″ AMOLED (YFT VTDR6115)

### D.1 Main Display Panel

| Field | Specification |
|---|---|
| **Panel driver** | `yft-lcm-vtdr6115-drv` |
| **Controller** | YFT VTDR6115 (MTK DSI command/mode) |
| **Interface** | MIPI DSI (4 data lanes) |
| **Size** | **6.67″** (official spec) |
| **Panel type** | **AMOLED** (official spec) |
| **Resolution** | 1080 × 2400 pixels |
| **Pixel density** | 480 dpi reported (≈395 ppi true by geometry) |
| **Aspect ratio** | 20:9 |
| **Refresh rates** | 60 Hz / 90 Hz / 120 Hz (HWC exposed; snapshot active = 60 Hz) |
| **Brightness** | **2200 nits peak** (GSMArena; not software-verifiable) |
| **Color gamut** | 1B colors (GSMArena) |
| **Color depth** | 1B (10-bit class) |
| **Touch polling** | TBD |
| **Always-On Display** | TBD |
| **HDR** | **HDR10 + HLG + Dolby Vision** (HAL `supportedHdrTypes: [2,3,4]`) |
| **Corning Gorilla Glass** | **Gorilla Glass 3** + oleophobic coating (official spec) |
| **Screen-to-body ratio** | TBD |

**Evidence**: `yft-lcm-vtdr6115-drv` kernel probe,
`SurfaceFlinger` 1080×2400@480dpi, `debug.composition.type: mdp`.

### D.2 Main Touchscreen: FocalTech FT3680

| Field | Specification |
|---|---|
| **Controller** | FocalTech FT3680 |
| **Bus** | SPI3 (`spi3.0`) |
| **Driver** | `fts_ts` / `focaltech_touch_spi_ft3680` |
| **Technology** | Projected Capacitive (PCAP) |
| **Touch mode** | True multi-touch (10 points) |
| **Max simultaneous touch points** | 10 |
| **Resolution** | 1080 × 2400 (pixel-matched) |
| **Touch report rate** | TBD (~60-120 Hz typical) |
| **Gesture support** | Yes (`fts_gesture_mode` sysfs node) |
| **Package** | QFN or WLCSP |
| **Firmware** | TBD (firmware file name) |
| **Power modes** | Sleep, Active, Gesture wake |
| **I2C node** | TBD (if I2C fallback available) |

**Evidence**: `/sys/bus/spi/devices/spi3.0` → `fts_ts`,
`persist.sys.phh.focaltech_node` → `spi3.0/fts_gesture_mode`,
web search: FT3680 is FocalTech's integrated capacitive touch controller.

---

## E. REAR DISPLAY: CO5300 + Hynitron hyn_ts

### E.1 Rear Display Panel

Official spec: **1.04″ AMOLED, 340 × 340 px, 60 Hz, 600 nits peak, Corning Gorilla Glass Victus**.

| Field | Specification |
|---|---|
| **Panel** | CO5300 driver name (`spi_tiny_lcd_co5300`); official panel = **AMOLED** |
| **Interface** | SPI0 (`spi0.0`) |
| **Driver** | `spi_tiny_co5300_lcd` |
| **Size** | **1.04″** (official spec) |
| **Resolution** | 340 × 340 pixels (square display — matches HAL touch resolution) |
| **Technology** | **AMOLED** (official) |
| **Refresh rate** | **60 Hz** (official) |
| **Brightness** | **600 nits peak** (official) |
| **Protection** | **Corning Gorilla Glass Victus** (official) |
| **Color depth** | TBD |
| **Control** | `/sys/class/misc/tiny_lcd_miscdev` (ioctl interface) |
| **Userspace app** | `YftMiniScreen.apk` (com.yft.miniscreen, ~84 MB) |
| **Services** | `tinydisplay_touch_daemon`, `tinylcd_hal` |
| **Use case** | Camera info, notifications, flashlight toggle |

### E.2 Rear Touch Controller

| Field | Specification |
|---|---|
| **Controller** | Hynitron **hyn_ts** |
| **Bus** | I2C (`0-0015`) |
| **Technology** | Projected Capacitive (PCAP) |
| **Resolution** | 340 × 340 (pixel-matched) |
| **Max touch points** | 1 (single point) |
| **Package** | TBD |
| **I2C address** | 0x15 (7-bit) |

**Evidence**: SPI0 `spi_tiny_lcd_co5300`, I2C `0-0015` hyn_ts, YftMiniScreen.apk,
`tinydisplay_touch_daemon`, `tinylcd_hal` services.

---

## F. CAMERA SUBSYSTEM

### F.1 Camera 0 — Main: Sony IMX989

| Field | Specification |
|---|---|
| **Sensor** | Sony IMX989 |
| **Manufacturer** | Sony Semiconductor Solutions |
| **Format** | 1-inch (13.2 mm × 8.8 mm active) |
| **Resolution** | 50.3 MP (8192 × 6144) |
| **Effective resolution** | ~12.6 MP (4096 × 3072 cropped) |
| **Pixel size** | 1.6 μm (native 1.6 μm, quad-binned to 3.2 μm) |
| **Pixel clock** | TBD |
| **Sensor size** | 13.1 mm × 9.8 mm (diagonal ~16.4 mm ≈ 1") |
| **Color filter** | RGGB Bayer |
| **Min focus distance** | 0.2 m |
| **Focal length** | 23.0 mm (35mm equiv.) |
| **Aperture** | f/1.9 |
| **FOV** | ~80° diagonal (estimated from 23mm equiv.) |
| **ISO range** | 100 – 19200 |
| **Max analog ISO** | 6400 |
| **OIS** | Yes (via DW9781C at `4-000e`, Camera 3 OIS) |
| **Flash** | Yes |
| **Video recording** | 4K@60fps, 1080p@240fps (TBD exact) |
| **Interface** | MIPI CSI-2 (4 lanes) |
| **I2C address** | `7-0020` (sensor0) |
| **VCM (AF)** | `main_vcm` at I2C `7-000a` |
| **EEPROM** | `camera-eeprom0` at I2C `7-0051` |
| **Driver** | `SENSOR_DRVNAME_IMX989_MIPI_RAW` |
| **Active array** | 4096 × 3072 |
| **HDR** | Yes (via dual-gain or multi-frame) |
| **Low light** | Excellent (1-inch sensor, 1.6μm pixels) |
| **Dynamic range** | ~14 EV (estimated, 1-inch sensor class) |
| **Max frame rate** | TBD (26fps @ full, higher @ cropped) |
| **Global shutter** | No (rolling shutter) |
| **Backside illumination** | Yes (BSI) |
| **Stacked design** | Yes (Sony stacked CMOS) |

**Evidence**: Camera HAL static info — exact driver name `SENSOR_DRVNAME_IMX989_MIPI_RAW`,
I2C bus `7-0020` (sensor0), I2C `7-000a` (VCM), `7-0051` (EEPROM).
Web search: Sony IMX989 1-inch 50MP 1.6μm pixel pitch sensor.

### F.2 Camera 1 — Front: Samsung ISOCELL JN1

| Field | Specification |
|---|---|
| **Sensor** | Samsung ISOCELL JN1 (S5KJN1) |
| **Manufacturer** | Samsung Semiconductor |
| **Format** | 1/2.8" (5.82 mm × 4.37 mm) |
| **Resolution** | 50 MP (8160 × 6120) |
| **Pixel size** | 0.64 μm (native), 2.56 μm (quad-binned to 12.5 MP) |
| **Color filter** | RGGB Bayer |
| **Technology** | Smart ISO Pro (dual conversion gain) |
| **ISOCELL Plus** | Yes (crosstalk reduction) |
| **AF** | Yes (PDAF — Phase Detection Auto Focus) |
| **PD AF coverage** | 100% (all pixels have PD AF) |
| **Interface** | MIPI CSI-2 (2 or 4 lanes) |
| **Facing** | Front |
| **Orientation** | 270° |
| **Flash** | No |
| **I2C address** | `4-0010` (sensor1) |
| **Driver** | `SENSOR_DRVNAME_S5KJN1_MIPI_RAW` |
| **Max frame rate** | TBD |
| **Video recording** | TBD |
| **HDR** | Yes (Smart ISO Pro) |
| **Low light** | Good (Smart ISO Pro boosts ISO up to 51,200) |
| **Backside illumination** | Yes (BSI) |

**Evidence**: Camera HAL static info — `SENSOR_DRVNAME_S5KJN1_MIPI_RAW`,
I2C `4-0010` (sensor1). Web search: Samsung ISOCELL JN1 50MP 0.64μm Smart ISO Pro.

### F.3 Camera 2 — Main2: Samsung ISOCELL JN1MAIN2

| Field | Specification |
|---|---|
| **Sensor** | Samsung ISOCELL JN1MAIN2 (S5KJN1 variant) |
| **Manufacturer** | Samsung Semiconductor |
| **Format** | ~1/2.8" (estimated) |
| **Resolution** | 50 MP (8160 × 6120) |
| **Pixel size** | 0.64 μm (native) |
| **Technology** | Smart ISO Pro, ISOCELL Plus |
| **AF** | Yes (PDAF) |
| **Interface** | MIPI CSI-2 |
| **Flash** | Yes |
| **Facing** | Back |
| **Orientation** | 270° |
| **I2C address** | `2-0010` (sensor2) |
| **VCM (AF)** | `main2_vcm` at I2C `4-000b` |
| **EEPROM** | `camera-eeprom1` at I2C `4-0050` |
| **Driver** | `SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW` |

**Evidence**: Camera HAL static info, I2C bus enumeration.

### F.4 Camera 3 — Ultra-Wide: OmniVision OV64B

| Field | Specification |
|---|---|
| **Sensor** | OmniVision OV64B |
| **Manufacturer** | OmniVision Technologies |
| **Format** | 1/2" (6.4 mm × 4.8 mm) |
| **Resolution** | 64 MP (9248 × 6944) |
| **Pixel size** | 0.7 μm (native), 2.8 μm (quad-binned to 16 MP) |
| **Color filter** | RGGB Bayer |
| **Technology** | PureCel®Plus‑S (pixel binning) |
| **AF** | Yes (VCM at `2-000d`) |
| **OIS** | Yes (DW9781C at `4-000e`) |
| **Flash** | Yes |
| **Interface** | MIPI CSI-2 |
| **Facing** | Back |
| **Orientation** | 270° |
| **I2C address** | `4-0020` (sensor4) |
| **VCM (AF)** | `main4_vcm` at I2C `2-000d` |
| **EEPROM** | `camera-eeprom2` at I2C `2-0050`, `camera-eeprom4` at I2C `4-0051` |
| **Driver** | `SENSOR_DRVNAME_OV64B_MIPI_RAW` |
| **HDR** | Yes (via multi-frame) |
| **Max frame rate** | 15 fps @ 64MP, higher @ binned |
| **Backside illumination** | Yes (BSI) |
| **Pixel clock** | TBD |

**Evidence**: Camera HAL static info, I2C bus enumeration,
web search: OV64B 64MP 0.7μm PureCelPlus-S 1/2" sensor.

### F.5 OIS Controller: Dahua DW9781C

| Field | Specification |
|---|---|
| **Chip** | DW9781C |
| **Manufacturer** | Dahua Technology (CJSC — previously Dahua Actuator) |
| **Type** | Voice Coil Motor (VCM) OIS actuator |
| **Purpose** | Optical Image Stabilization for Camera 3 (OV64B) |
| **Interface** | I2C |
| **I2C address** | `4-000e` |
| **Driver** | `dw9781c` |
| **Package** | WLP or LGA |
| **Control mode** | Closed-loop (position feedback) or Open-loop |
| **Damping** | Electronic damping support |
| **Power consumption** | TBD |

**Evidence**: I2C bus enumeration — `dw9781c` at `4-000e`.

---

## G. THERMAL CAMERA: ThermoVue Pro AC020

| Field | Specification |
|---|---|
| **Module name** | ThermoVue Pro AC020 |
| **Sensor type** | Microbolometer (uncooled IR focal plane) |
| **IR detector material** | VOx (Vanadium Oxide) or a-Si (Amorphous Silicon — TBD) |
| **Pixel resolution** | TBD (typically 256×192 or 384×288 for AC020-class modules) |
| **Pixel pitch** | TBD (typically 12 μm) |
| **NETD** | TBD (< 50 mK typical for this class) |
| **Spectral response** | 8–14 μm (long-wave infrared) |
| **Frame rate** | 25 Hz or 30 Hz |
| **Interface** | USB (UVC-compatible with proprietary AC020 protocol) |
| **Focus** | Fixed focus (typically 1.5–3 m minimum) |
| **Temperature range** | TBD (typically -20°C to +550°C or 1000°C) |
| **Accuracy** | ±2°C or ±2% (TBD) |
| **Calibration** | 17 embedded calibration datasets (high/low B/K, KT/BT, NUC, OOC, RMVC, private) |
| **Native libraries** | AC020, UVC/USB, IR camera/command, image processing, dual calibration, temperature |
| **Kernel driver** | `yft_tiny2c_usb` / `tiny2c_usb-sensor` |
| **I2C control** | `8-003c` (`fm78100` compatible) — for sensor control |
| **App** | `M170infisens.apk` (com.energy.tc2c, ThermoVue Pro) |
| **Calibration assets** | 17 embedded calibration files in APK |
| **Radiometric** | Likely (private temperature libraries present) |

**Evidence**: APK `com.energy.tc2c` with ThermoVue Pro label, 17 calibration assets,
AC020 native libraries; `yft_tiny2c_usb` kernel driver; I2C `8-003c`.

---

## H. SENSORS

### H.1 IMU: IvenSense ICM4N607 (Accelerometer + Gyroscope)

| Field | Specification |
|---|---|
| **Chip** | IvenSense ICM4N607 |
| **Vendor string** | `iven_sense` |
| **Accelerometer range** | ±2 / ±4 / ±8 / ±16 g (configurable) |
| **Accelerometer resolution** | 16-bit (hardware), 24-bit (internal) |
| **Accelerometer sensitivity** | TBD (e.g., 16384 LSB/g @ 2g) |
| **Accelerometer noise** | TBD (e.g., ~1500 µg/√Hz typical) |
| **Gyroscope range** | ±125 / ±250 / ±500 / ±1000 / ±2000 dps (configurable) |
| **Gyroscope resolution** | 16-bit (hardware) |
| **Gyroscope sensitivity** | TBD |
| **Gyroscope noise** | TBD |
| **Max sample rate** | 400 Hz (both accel and gyro) |
| **FIFO** | Yes (gyro) — TBD size |
| **Interface** | I2C / SPI |
| **Package** | WLP or LGA |
| **Temperature sensor** | Yes (integrated) |
| **Power modes** | Low-power, Full-power, Deep-suspend |
| **Power consumption** | TBD (typically ~1-2 mA active) |
| **Features** | DMP (Digital Motion Processor), 6-axis fusion, wake-on-motion |
| **FIFO** | Gyro FIFO with 4500 event capacity |
| **Android sensor types** | accelerometer (type 1), gyroscope (type 4) |
| **Android minRate** | 12.5 Hz |
| **Android maxRate** | 400 Hz |

**Evidence**: `dumpsys sensorservice` — `icm4n607_acc` and `icm4n607_gyro` with vendor
`iven_sense`, max rate 400 Hz, live events showing ~9.83 m/s² (1g) gravity,
kernel driver evidence. Web search: InvenSense ICM40607 (ICM4N607 is the MediaTek variant).

### H.2 Magnetometer: Memsic MMC5603

| Field | Specification |
|---|---|
| **Chip** | Memsic MMC5603 |
| **Vendor string** | `memsic` |
| **Technology** | AMR (Anisotropic Magnetoresistive) |
| **Axes** | 3-axis |
| **Range** | ±300 mT (±3000 Gauss) |
| **Resolution** | 0.3 μT (15-bit output) |
| **Interface** | I2C |
| **Package** | WLP 0.8 × 0.8 × 0.4 mm |
| **I2C address** | TBD |
| **Power consumption** | TBD (AMR is very low power) |
| **Accuracy** | TBD (±1% typical) |
| **Cross-axis sensitivity** | TBD |
| **FIFO** | Yes (4500 events, 600 reserved) |
| **Android minRate** | 5 Hz |
| **Android maxRate** | 50 Hz |
| **Android type** | `magnetic_field` (type 2) |

**Evidence**: `dumpsys sensorservice` — `mmc5603`, vendor `memsic`, max rate 50 Hz,
FIFO 4500/600, I2C address TBD. Web search: Memsic MMC5603 AMR magnetometer ±30g.

### H.3 Ambient Light + Proximity: Sensortek STK3A5X

| Field | Specification |
|---|---|
| **Chip** | Sensortek STK3A5X |
| **Vendor string** | `sensortek` |
| **Type** | Combined ALS (Ambient Light Sensor) + PS (Proximity Sensor) |
| **ALS range** | TBD (typically 0–64000 lux) |
| **ALS resolution** | TBD (typically 16-bit) |
| **ALS accuracy** | TBD |
| **ALS response time** | TBD |
| **Proximity range** | TBD (typically 0–~10 cm) |
| **Proximity resolution** | TBD (typically 256 levels) |
| **IR LED** | Integrated or external IR LED for proximity |
| **Interface** | I2C |
| **Package** | WLCSP or LGA |
| **Power modes** | Low-power, Active, Sleep |
| **Power consumption** | TBD |
| **ALS Android type** | `light` (type 5), on-change |
| **PS Android type** | `proximity` (type 8), on-change, wakeUp |
| **PS FIFO** | Yes (4500 events, 100 reserved) |
| **I2C address** | TBD |

**Evidence**: `dumpsys sensorservice` — `stk3a5x_als` (vendor `sensortek`) and
`stk3a5x_ps` (vendor `sensortek`), on-change mode, PS FIFO 4500/100.

### H.4 Barometer: Goertek SPL07

| Field | Specification |
|---|---|
| **Chip** | Goertek SPL07 (SPL07-003 or SPL07-006) |
| **Vendor string** | `goer` |
| **Technology** | Capacitive silicon piezoresistive |
| **Pressure range** | 30 kPa to 110 kPa (4.35 PSI to 15.95 PSI) — absolute pressure |
| **Altitude range** | ~−600 m to +3000 m |
| **Resolution** | ~0.02 hPa (0.16 m altitude) |
| **Accuracy** | ±0.5 hPa (±4 m altitude) typical |
| **Temperature range** | −40°C to +85°C |
| **Temperature accuracy** | TBD |
| **I2C address** | TBD |
| **Interface** | I2C |
| **Package** | 10-WFLGA (Wafer-Level Fine-Pitch Grid Array) |
| **Power consumption** | TBD (typically < 100 μA) |
| **FIFO** | Yes (4500 events, 300 reserved) |
| **Android minRate** | 1 Hz |
| **Android maxRate** | 10 Hz |
| **Android type** | `pressure` (type 6) |
| **Calibration** | On-chip calibration coefficients |

**Evidence**: `dumpsys sensorservice` — `spl07`, vendor `goer`, max rate 10 Hz,
FIFO 4500/300, DigiKey listing SPL07-003 30-110 kPa range.

---

## I. FINGERPRINT SENSOR: Madev Microarray

| Field | Specification |
|---|---|
| **Manufacturer** | Madev (Shenzhen Madev Technology) |
| **Technology** | Capacitive microarray (TBD: 3D capacitive or 2D) |
| **Transport** | SPI1 (`spi1.0`) |
| **Driver** | `madev` / `microarray_fp_tee` |
| **Device nodes** | `/dev/madev0`, `/dev/tkcore_fp` |
| **Authentication** | TrustKernel TEE-based (hardware-authenticated) |
| **Sensor type** | Capacitive (semiconductor fingerprint) |
| **Resolution** | TBD (typically 500 dpi for smartphone class) |
| **Active area** | TBD (typically ~15×15 mm to 20×20 mm) |
| **Image depth** | TBD (typically 8-bit grayscale) |
| **Enrollment speed** | TBD (typically 1-2 seconds) |
| **Match speed** | TBD (typically < 300 ms) |
| **Security level** | Hardware-authenticated via TrustKernel TEE |
| **Anti-spoof** | TBD (liveness detection) |
| **Power modes** | Active, Sleep, Deep-sleep |
| **I2C address** | TBD (if I2C companion available) |
| **Physical location** | TBD (side-mounted or under-display) |
| **Framerate** | TBD |

**Evidence**: SPI1 `madev`, `microarray_fp_tee` module, TrustKernel keymaster,
`/dev/madev0`, `/dev/tkcore_fp` device nodes.

---

## J. NFC: STMicro ST21NFC

| Field | Specification |
|---|---|
| **Controller** | STMicroelectronics ST21NFC (ST21NFCL variant) |
| **I2C address** | `6-0008` |
| **Driver** | `st21nfc` |
| **Processor** | Arm® core (Arm Cortex-M) |
| **Standards** | NFC Forum Type 1/2/3/4, FeliCa, ISO/IEC 14443 A/B, ISO/IEC 15693 |
| **Data rate** | 424 kbps (NFC-IP1) |
| **Secure element** | Dual (SIM1 + SIM2 for eSE) |
| **SE service** | `mtk_secure_element_hal_service` |
| **Firmware** | `st21nfc_fw.bin`, `st21nfc_fw7.bin` |
| **HAL** | `android.hardware.nfc.INfc/default` |
| **Modes** | Card emulation, HCE (host card emulation), P2P (peer-to-peer) |
| **Antenna** | TBD (integrated coil or external) |
| **Frequency** | 13.56 MHz |
| **Range** | ~4 cm (NFC standard) |
| **I2C address** | 0x08 (7-bit) |

**Evidence**: I2C bus `6-0008` → `st21nfc`, firmware files, HAL service,
web search: ST21NFCL Arm core NFC CLF.

---

## K. AUDIO SUBSYSTEM

### K.1 Codec / PMIC Audio

| Field | Specification |
|---|---|
| **Codec** | MediaTek MT6369 (integrated PMIC audio codec) |
| **I2C address** | `5-0018` |
| **Headset jack** | `mt6878-mt6369 Headset Jack` |
| **Features** | Headphone output, microphone input, line-out, physical-insertion detection |
| **DAC** | Integrated 16-bit (TBD) |
| **Sample rates** | TBD (8–192 kHz typical) |
| **Output power** | TBD (typically ~30 mW @ 32 Ω) |

**Evidence**: ALSA `mt6878-mt6369 Headset Jack`, `mt6369` I2C binding at `5-0018`.

### K.2 Speaker Amplifier

| Field | Specification |
|---|---|
| **I2C address** | `6-0034` |
| **Driver** | `speaker_amp` / `mtk_sp_spk_amp` |
| **IC** | TBD (generic speaker amplifier) |
| **Manufacturer** | TBD |
| **Output power** | TBD |
| **Class** | Class D (typical for mobile) |
| **Interface** | I2C + PDM/DMIC or PWM |

### K.3 Microphones

| Field | Specification |
|---|---|
| **Count** | ≥2 (headset mic + internal mics) |
| **Type** | MEMS PDM (Phase-Digital-Microphone) |
| **Count (internal)** | TBD (typically 2-3 for noise cancellation) |
| **Alsa card** | MediaTek |

---

## L. BATTERY AND CHARGING

### L.1 Battery

| Field | Specification |
|---|---|
| **Technology** | Li-ion (Lithium-ion polymer) |
| **Design capacity** | ~8,588,000 µAh (~8588 mAh) |
| **Typical capacity** | ~2,946,000 µAh (framework reports this — likely a framework-level limit) |
| **Voltage** | 8.400 V (reported — suggests 2-cell series) |
| **Cell configuration** | 2S (2-cell series) — strongly suggested by 8.4V |
| **Max charging current** | 1,000,000 µA (1A at framework level — likely ROM-limited) |
| **Temperature** | 37.0 °C |
| **Health** | GOOD |
| **Manufacturer** | TBD |
| **Part number** | TBD |
| **Protection** | Battery protection circuit (TBD) |

### L.2 Primary Fuel Gauge: MediaTek MT6375

| Field | Specification |
|---|---|
| **IC** | MediaTek MT6375 |
| **I2C address** | `5-0034` |
| **Driver** | `mt6375` / `mtk-gauge` |
| **Type** | Integrated fuel gauge with PMIC functions |
| **Path** | Primary Android battery path |
| **Features** | State-of-Charge (SoC), State-of-Health (SoH), temperature monitoring |

### L.3 Secondary Fuel Gauge: SH366003

| Field | Specification |
|---|---|
| **IC** | SH366003 |
| **Manufacturer** | Sinowealth Electronics |
| **I2C address** | `9-0055` |
| **Driver** | `sh366003_fg` |
| **Type** | Integrated MCU + high-voltage AFE (Analog Front End) |
| **Path** | `3rd-gauge` (secondary/backup) |
| **Features** | Battery protection, SoC, temperature monitoring |
| **AFE** | High-voltage analog front end |
| **Protection** | Over-charge, over-discharge, over-current, short-circuit |

### L.4 Charge Pumps

| IC | I2C Address | Specifications |
|---|---|---|
| **SC8571 (master)** | `11-0066` | Dual-cell, 8A, 98.65% peak efficiency, switched-cap, 50% duty cycle |
| **SC8571 (slave)** | `6-0067` | Same as master, parallel/secondary charging |
| **SC8510 (SC851x)** | `6-0069` | Dual-cell, 10A forward (2:1), 4A charge (1:2), 99.5% efficiency, load-switch |

**Evidence**: I2C bus enumeration, battery/charging docs, web search: SC8571 8A dual-cell,
SC8510 10A 2:1 forward / 4A charger.

### L.5 Additional PMICs

| IC | I2C Address | Specifications |
|---|---|---|
| **RT6160** (Crichtek/Richtek) | `5-0075` | 3A Buck-Boost converter, I2C interface, low quiescent current |
| **RT6160** (Crichtek/Richtek) | `6-0075` | Same as above (second unit) |
| **WL2864C** | `11-0029` | `will,wl2864c_pmu` — Will Semiconductor PMU |

**Evidence**: I2C bus enumeration, web search: RT6160 3A Buck-Boost I2C, WL2864C PMU.

### L.6 USB PD / PPS

| Field | Specification |
|---|---|
| **PD support** | Yes (USB Power Delivery) |
| **PPS support** | Yes (Programmable Power Supply) |
| **Max wired wattage** | 120 W (marketing claim) |
| **State machine** | TBD (OEM protocol? PD/PPS with custom PPS profile?) |
| **Reverse charging** | TBD |

---

## M. LED CONTROLLERS

### M.1 Flash / Torch: Awinic AW36515

| Field | Specification |
|---|---|
| **Chip** | Awinic AW36515 (AW36515E or AW36515A) |
| **I2C address** | `6-0063` |
| **Driver** | `aw36515` |
| **Type** | Dual LED flash driver |
| **Boost converter** | 2 MHz / 4 MHz fixed-frequency synchronous boost |
| **Max flash current** | 2A per channel (constant current) |
| **LED channels** | 2 (dual LED) |
| **Flash mode** | Camera flash, torch (continuous) |
| **Current control** | Software-adjustable constant current |
| **Efficiency** | TBD |
| **Package** | WLP or QFN |

### M.2 IR / Auxiliary: Awinic AW36518

| Field | Specification |
|---|---|
| **Chip** | Awinic AW36518 (AW36518F) |
| **I2C address** | `8-0063` |
| **Driver** | `aw36518` |
| **Type** | Independent 1.5A flash LED driver |
| **Max current** | 1.5A per channel |
| **Channels** | TBD |
| **Purpose** | IR/auxiliary illumination |

### M.3 Work Light: Awinic AW36518_v2

| Field | Specification |
|---|---|
| **Chip** | Awinic AW36518_v2 |
| **I2C address** | `12-0063` |
| **Driver** | `aw36518_v2` |
| **Type** | Independent 1.5A flash LED driver |
| **Purpose** | Work light / warning light controller |
| **Associated apps** | `YftOutdoorLightUlefone`, `YftRedBlueLight` |

### M.4 RGB Notification: Awinic AW2013

| Field | Specification |
|---|---|
| **Chip** | Awinic AW2013 |
| **I2C bus / address** | bus 11 (`i2c@11d71000`, `mediatek,mt6989-i2c`) / `0x45` → `11-0045` |
| **DT node / compatible** | `aw2013@0x45` / `awinic,rgb,aw2013` |
| **Driver** | `leds_rgb_aw2013` (i2c driver name `leds-rgb-aw2013`, vendor_boot ramdisk) |
| **Chip-enable** | GPIO **188** (`aw2013-pwd-gpio`), driven output-high at probe and never released — **no regulator is used** |
| **Channels** | 3 — `reg` 0 = red, 1 = green, 2 = blue |
| **LED class devices** | `/sys/class/leds/{red,green,blue}` (ABI: Lights HAL, init.mt6878.rc, init.yft.rc, FactoryMode) |
| **Per-channel current** | `led-max-microamp = 5000` → `IMAX` code 1 → **5 mA** full scale on all three |
| **PWM resolution** | 8-bit per channel (`PWM(n)` at `0x34+n`) |
| **Effective brightness** | **clamped** to the DT `led-fixed-brightness`: red 64, green 64, blue 128 — any non-zero write produces that value, so each channel is effectively binary |
| **Blink** | hardware blink, 130 ms time step; on 130 ms…16.64 s, off 130 ms…4.16 s (`LEDT0`/`LEDT1`, `LCFG.MD`) |
| **Breathing ramps** | **not used** — `LCFG.FI/FO`, `LEDT0.T1`, `LEDT1.T3` and `LEDT2` are never written by the stock driver |
| **Chip ID / reset** | `RSTR(0x00)` must read `0x33`; single software reset `RSTR = 0x55` at probe |
| **Charging indicator** | in MediaTek power-off-charging boot (mode 8/9) the driver reads `3rd-gauge` `CAPACITY` and lights green ≥ 90 %, red ≤ 15 %, blue 16–89 % |
| **PM** | none — no suspend/resume/shutdown callbacks, no IRQ, no timer, no workqueue |

**Evidence**: full reverse-engineering in
`kernel/phase4-leds-rgb-aw2013-reconstruction.md` and the accompanying
hardware/DT/userspace contracts and register map; the reconstruction is
byte-identical to the stock module in every content-bearing ELF section.

---

## N. HAPTICS / VIBRATION

### N.1 Vibration Motor

| Field | Specification |
|---|---|
| **Motor type** | ERM (Eccentric Rotating Mass) — software reports no LRA characteristics |
| **Vibrator ID** | 1 |
| **HAL** | `vendor.vibrator-default` |
| **Capabilities** | Click, double-click, tick, heavy-click, texture-tick |
| **Resonant frequency** | NaN (not LRA — confirms ERM) |
| **Q-factor** | NaN |
| **Driver IC** | TBD |
| **Interface** | GPIO (direct drive) or PWM |

**Evidence**: `VibratorManagerService` — capabilities flags, supported effects,
no q-factor/resonant frequency (ERM confirmed).

---

## O. PHYSICAL BUTTONS

| Button | Driver | Keycode | Notes |
|---|---|---|---|
| Power | TBD (standard) | KEY_POWER | Standard power button |
| Volume Up | TBD (standard) | KEY_VOLUMEUP | Standard volume |
| Volume Down | TBD (standard) | KEY_VOLUMEDOWN | Standard volume |
| Programmable key 1 | `yft-gpio-keys` | F1 | Custom rugged button |
| Programmable key 2 | `yft-gpio-keys` | F2 | Custom rugged button |

**Evidence**: `yft-gpio-keys` driver emitting F1/F2.

---

## P. COOLING SYSTEM

| Field | Specification |
|---|---|
| **Active cooling** | None (no fan detected) |
| **Passive cooling** | TBD (graphite sheets, copper foil, heat pipe, vapor chamber — physical inspection needed) |
| **Thermal zones** | CPU, GPU, NPU, TPU, SOC, skin, battery, USB port, power amplifier |
| **Thermal types** | CPU/GPU/NPU/TPU/SOC: 85/90/100/117 °C thresholds |
| **Battery thermal** | 50/55/59/60 °C thresholds |
| **Cooling devices** | Mali GPU, charger-cooler, LCD backlight, Wi-Fi, flashlight |
| **Thermal HAL** | AIDL v3 (8 temperature types, 5 cooling devices) |

---

## Q. USB / TYPE-C

| Field | Specification |
|---|---|
| **Controller** | UDC `11201000.usb0` |
| **Interface** | configfs USB gadget |
| **USB version** | USB 2.0 (no SuperSpeed evidence) |
| **OTG** | Supported (configfs host/device) |
| **DisplayPort Alt Mode** | TBD |
| **USB-PD** | Yes (PD + PPS) |
| **Data lines** | USB 2.0 (D+/D-) |

---

## R. ANTENNAS AND RF FRONTEND

| Field | Specification |
|---|---|
| **RF FEM** | TBD (ConnFem research in progress) |
| **Antenna count** | TBD |
| **Cellular antennas** | TBD (4G/5G MIMO likely 4x4) |
| **Wi-Fi antenna** | TBD (2×2 MIMO) |
| **GNSS antenna** | TBD |
| **Antenna switch** | TBD |

---

## S. IR HARDWARE

| Field | Specification |
|---|---|
| **IR blaster** | Unknown (`vendor.ir-default` service present) |
| **IR receiver** | Unknown |
| **IR illuminator** | Possibly AW36518 at `8-0063` (IR camera companion) |
| **Proximity IR LED** | Part of STK3A5X proximity sensor |

---

*This document provides datasheet-level specifications for all hardware components identified in the Ulefone Armor 29 Pro Thermal (GQ5012BF1). Field marked TBD requires physical inspection, teardown, or manufacturer datasheet access for completion.*
