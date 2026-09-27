# Master hardware inventory - Ulefone Armor 29 Pro Thermal / GQ5012BF1

**Audit state:** evidence audit of 2026-09-08, **reconciled after a second-pass UNKNOWN-HARDWARE verification** (`../verification/`). Live source snapshot: 2026-08-31 11:56. No ADB device was attached during either verification pass; both used the frozen capture and extracted stock images.

> **Provenance warning.** The 2026-08-31 capture was taken on a device whose **vendor and kernel are stock but whose system image is a GSI** (`ro.lineage.display.version = LieppOS-23-20260830-VANILLA-EROFS-GSI`, KernelSU-rooted). Kernel, driver, device-tree, bus and vendor-partition facts below are therefore valid; **Android-framework observations are not evidence of stock Ulefone behaviour**. See `../verification/findings/00-snapshot-provenance-correction.md`.

Confidence: PROVEN > STRONGLY_SUPPORTED > LIKELY > POSSIBLE > UNKNOWN > TEARDOWN_REQUIRED.

## Identity

| Field | Value | Confidence |
|---|---|---|
| Product/build | `Ulefone/GQ5012BF1_EEA/GQ5012BF1`, Android 15, `AP3A.240905.015.A2/1761131274` | PROVEN |
| SoC orderable part | **MT6878V/TZA** (device-tree `model-external-name`; internal model string `MT8873`) | PROVEN |
| Platform | MediaTek MT6878 family, marketed Dimensity 7400 | PROVEN |
| Baseband | `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1` | PROVEN |
| Custom version | `DZ_M170_Ulefone_EEA_Armor29Pro_20251022_V35` (ODM project **M170**) | PROVEN |
| ODM software base | shared with other YFT/Ulefone projects and at least one Doogee model (`morphoEISCalibration_DOOGEE_M24PS.bin`) | PROVEN |

## Core, memory and storage

* CPU/GPU/APU: 4x Cortex-A78 + 4x Cortex-A55, Mali-G615 MC2 class, MediaTek APU/NPU - platform level.
* **Memory + storage are a single Micron uMCP marked `MT512GBCAV8U31`** (from the bootloader's own detection, `lpddr_used_name=`): **512 GB UFS + 16 GiB LPDDR5-class DRAM**. DRAM window `memory@40000000` = 16 GiB. **PROVEN.** LPDDR5 vs LPDDR5X grade, data rate and channel/rank map remain UNKNOWN.
* Storage controller: UFSHCI at `0x112b0000` with RPMB and two boot LUs. **UFS health at capture: `PreEOLInfo = 0x1` (Normal), `LifeTimeEstA = LifeTimeEstB = 0x1` (0-10 % of rated life used). PROVEN.** Negotiated UFS version and gear/lane count UNKNOWN.
* 5G R16-class modem, 2G-5G, dual-SIM dual-standby. **Two physical Nano-SIM trays plus a dedicated microSD slot; no eSIM/eUICC and no embedded secure element (PROVEN absent).**

## Cameras and optics

Four Android cameras. Runtime driver names and stream tables come from MTK CameraProvider; aperture/focal entries below are **published role specifications**, because the vendor static blocks omit `android.lens.aperture` and `android.lens.focalLength`:

| # | Runtime driver | Facing / role | Max RAW16 stream | Max still | Published aperture / focal | Vendor-HAL OIS modes |
|---|---|---|---|---|---|---|
| 0 | `IMX989_MIPI_RAW` | back, main | 4096x3072 | 8192x6144 (50 MP), incl. 7680x4320 | f/1.9, 23 mm | reported unavailable |
| 1 | `S5KJN1_MIPI_RAW` | front | 4080x3072 | 8192x6144 | f/2.45, 25 mm | reported unavailable |
| 2 | `S5KJN1MAIN2_MIPI_RAW` | back, ultrawide (117.3 deg AF) | 4080x3072 | 8192x6144 | f/2.2, 16 mm | reported unavailable |
| 3 | `OV64B_MIPI_RAW` | back, night vision | 4624x3472 | 9216x6912 (64 MP) | f/1.79, 26 mm | reported unavailable |

Static-metadata caveat: camera 2 (`S5KJN1MAIN2`) publishes an 8160x6144 `pixelArraySize` with camera 0's 13.107 x 9.830 mm physical geometry, and camera 1 combines JN1-sized geometry with an 8160x6144 array. These fields are internally inconsistent; stream modes are HAL facts, but secondary-module die size/pitch must remain unproven.

* **The main slot is multi-source.** `sensor0` declares `imx989`, `s5kgm2sp`, `imx989cts` and `s5kgn1sp` candidates and binds by sensor-ID probe. On this handset MTK CameraProvider explicitly enumerated **`SENSOR_DRVNAME_IMX989_MIPI_RAW`**; camera 0 also publishes `physicalSize = 13.107 x 9.830 mm` and a 4096x3072 binned pixel array, self-consistent with the 1-inch-class IMX989. Ulefone and an independent exact-device review instead specify **Samsung S5KGN1, 1/1.31 inch, 1.2 um** for the model. The evidence supports lot/SKU variation, not a combined sensor name. **Runtime match STRONGLY_SUPPORTED; slot variability PROVEN.**
* Actuators: three AF VCMs - `main_vcm` (i2c 7-000a), `main2_vcm` (4-000b), `main4_vcm` (2-000d) - plus a **bound DW9781C OIS controller** at 4-000e. Lens ownership is **UNKNOWN**: sensor0's pinctrl group has `oisvdd_on/off`, sensor4's has `oisen_on/off`, and the actuator shares i2c-4 with sensor1 + sensor4 while sensor0 is on i2c-7. All four vendor-HAL cameras report `availableOpticalStabilization = [0]` (OFF only).
* Four camera EEPROMs: 7-0051, 4-0050, 2-0050, 4-0051.
* Camera power: a **bound WL2864C/WL2868C-family** 7-channel camera LDO (2 DVDD, 2 AVDD, VDDIO, VDDAF, **VDDOIS**) at 11-0029. Its shared driver and dual ID table support both revisions; exact die is UNKNOWN. `RT5133@18` is an 8-channel camera-LDO alternate by datasheet but is unbound and has no shipped module, so physical population is UNKNOWN.
* Flash/IR: bound AW36515 dual-channel 2 A (6-0063), AW36518 1.5 A (8-0063), AW36518-v2 1.5 A (12-0063), plus bound AW2013 RGB at 11-0045. `/yft_camplight` has red/blue/power GPIOs and PWM wiring matching a **Natlinear LN2403 2 A buck constant-current LED driver** (part LIKELY, node/wiring PROVEN). `/irtx-pwm` uses PWM0 and `mt6369_vio28`; the AOSP AIDL service wraps the selected MTK `consumerir.common.so` LIRC backend. Software ownership/ABI is PROVEN; emitter/function remain unverified.

## Thermal imaging

* **InfiRay / InfiSense Mini640-class uncooled LWIR module** with the InfiRay **AC020** processing ASIC, marketed by Ulefone as **"ThermoVue T2"**: **640 x 512, 12 um pitch, NETD < 40 mK, radiometric, 25 Hz**, FOV 56 x 42 deg, -20 to 550 degC, +/-2 degC. **STRONGLY_SUPPORTED.**
* Image data arrives over an **internal USB UVC link**, handled in userspace by the InfiRay SDK (`libAC020sdk.so`, `libircmd020.so`, `libusbuvccamera020.so`, `libdualuvccamera020.so`, ...). It is therefore **not** an Android camera. Stock applications: `M170infisens.apk`, `M170infDlp.apk`; per-unit calibration in `/mnt/vendor/nvcfg/infiray`.
* The I2C node named **`fm78100` (8-003c) is not a thermopile**: it is bound to `tiny2c_usb-sensor` (`yft_tiny2c_usb`) and only performs 1.8 V/3.3 V/5 V/IO-3.3 V power sequencing, `sensor_id` readout and a `tiny2c_usb_mode` switch. The name is inherited from a different ODM variant. **PROVEN.**

## Displays and touch

* **Main:** 6.67-inch AMOLED, 1080x2400, 60/90/120 Hz, 2200 nits peak (OEM), Gorilla Glass 3; panel driver string `yft_vtdr6115_fhdp_dsi_cmd_hx_dphy_667_ky_lcm_drv`, command mode. Display bias by **OCP2131** (dual-output programmable, 6-003e). An unused alternative main panel `jdi,nt36672e,vdo,60hz` exists in the device tree.
* **Rear sub-display:** **1.04-inch AMOLED, 340 x 340, 600 nits peak**, driven by a **Chipone CO5300** single-chip AMOLED driver on SPI0 at 60 MHz (`spi_tiny_lcd_co5300`), with D/C, reset, TE and 1.8 V/2.8 V enables plus a `tiny_lcd_adc` channel. It is **not** an Android display; it is controlled through vendor sysfs. **PROVEN.** (The earlier "3.97-inch" figure was wrong.)
* **Main touch:** FocalTech FT3680-family `fts_ts` on SPI3, 10-point, IRQ 7 / reset 6; runtime `TP Ready, Read ID=0x56`. **Rear touch:** bound **Hynitron `hyn_ts`** at 0-0015, native 340x340, single-touch. Ilitek 0-0041 and ChipOne-TDDI 0-0048 are unbound alternate-vendor entries sharing the active pin lineage, and no driver module for either ships. Active pair PROVEN; physical absence of alternates STRONGLY_SUPPORTED.

## Audio, haptics, indicators

* **Codec inside the MT6369 sub-PMIC** (`mt6369codec`); **Awinic AW88394** smart PA at 6-0034 (ID 0x2049).
* **Two built-in analog microphones, PROVEN**: bottom/main -> AIN0/PGA_L/ADC_L/UL1_CH1 and back/sub -> AIN2/PGA_R/ADC_R/UL1_CH2. Stock DT and the HAL's MicInfo branch select AMIC, not the dormant AP/SCP DMIC alternatives. No enabled separate microphone IC or third fitted mic was found.
* **3.5 mm headset jack, PROVEN**: `mt6369-accdet`, `status = "okay"`, efuse-calibrated, three- and four-button remote threshold tables; its microphone is a separate accessory input.
* **FM radio receiver, PROVEN**: `mediatek,fm` + `mediatek,fmradio` (`status = "okay"`), discrete `fm_lna_gpio` (pin 72), FM firmware (`fm_cust.cfg`, `soc_fm_v1_patch/coeff.bin`), stock `YftFmRadio.apk`, and headset-as-antenna switching via `gpio-accdet-fm-switch` (pin 195). Only receive-side firmware ships - **FM transmit should be assumed unavailable**.
* **Haptics:** an **ERM motor driven directly from the MT6369 `VIBR` LDO** through the generic `regulator-vibrator` driver, board window 2.2-3.5 V, 680 us enable ramp. **There is no haptic driver IC**, so amplitude/frequency-controlled haptics are not achievable on this hardware. Motor part number TEARDOWN_REQUIRED.
* AW2013 RGB indicator at 11-0045.

## Sensors, security, connectivity

* ICM-4N607-class 6-axis IMU (1-0068), Memsic MMC5603 (1-0030), Sensortek STK3A5X ALS/PS, SPL07-003 barometer (1-0077).
* **Fingerprint: Microarray (MaFinger/MaDev)** module on SPI1 at 8 MHz (`/dev/madev0`, `microarray_fp_tee`, `microarray.fingerprint.default.so`), reset GPIO 30 / IRQ GPIO 3, using `/dev/tkcore_fp` for TrustKernel/TkCore TEE transport. A generic `tplcd_pattern` hook suggests optical operation, while one low-quality review says side-mounted; neither identifies the die or physical mounting. **Exact die, location, modality and geometry are TEARDOWN_REQUIRED.** Vestigial `goodix-fp` and `focaltech,fp` nodes are ODM alternates.
* **Connectivity ADIE: MT6637** (Wi-Fi and GNSS chip IDs 0x6637). OEM: Wi-Fi 6E (2.4/5/6 GHz), Bluetooth 5.4.
* **No external Wi-Fi/BT front-end module is fitted.** The ConnFem HWID resolves to `nofem + nofem` and the driver logged "FEM is not available" with `BTvid/pid == 0`; `connfem.cfg` is empty. The seven alternative FEM pairs in the device tree are other boards' options. **PROVEN.**
* **GNSS: five constellations - GPS, GLONASS, Galileo, BeiDou, NavIC - plus QZSS, in dual-band L1 + L5/E5a/B2a**, with B1C/L1C/E5B/B2B enabled, L5 differential-code-bias calibration keyed to chip `6637`, a separate multi-band power model and **Galileo OSNMA enabled**. **STRONGLY_SUPPORTED** (configuration level; no fix was recorded).
* **NFC: ST21NFC-family controller** at 6-0008 running `st21nfc_fw7.bin` with board-specific CustomA/CustomB RF parameters, a DPC table and an explicit antenna configuration. **Controller-only - no embedded secure element**; off-host routing is UICC-only (`android.hardware.se.omapi.uicc` is the only SE feature declared). ST21NFCD-class: STRONGLY_SUPPORTED; exact part TEARDOWN_REQUIRED.

## Power and physical

* **System power tier (SPMI):** **MT6363** main PMIC, **MT6369** sub-PMIC/codec/accdet/VIBR, **MT6319** external buck, **MT6685** clock/RTC/consys MFD providing the **TIA-NTC** front end for four board thermistors (`thermal-ntc1/2/3/6`).
* **Charging tier (I2C):** bound **MT6375** buck charger/gauge/TCPC (5-0034; `cv 4450 mV`, `ichg 2000 mA`, `vbus-ov 14500 mV`); **two bound SC8571 charge pumps** (master 11-0066, slave 6-0067), exact-part rating **2-cell / 8 A / 98.65% peak / CSP80**, board-capped at 6.55 A each; bound **SC8510** bidirectional pump (6-0069) for wired reverse; bound **SH366003** pack gauge (9-0055). Two RT6160A nodes (5-0075, 6-0075) are unbound alternates; their physical population is UNKNOWN.
* **Battery: 2S (two cells in series), 7.74 V nominal, 8.90 V pack CV = 4.45 V per cell. PROVEN.** Ulefone rates it 10600 mAh at 7.74 V (marketed as "21200 mAh" at 3.87 V, ~82 Wh). Capture state: 8.397 V, 79 %, 26 cycles, SoH 94 %, no safety or permanent-fail flags. **The gauge's design-capacity/FCC field reads 8594 mAh, ~19 % below the OEM rating - an unresolved discrepancy.** Cell vendor/model TEARDOWN_REQUIRED.
* **Charging protocols: USB PD 3.0 with PPS only - no UFCS, no proprietary protocol** (`POWER_SUPPLY_USB_TYPE = ... PD PD_PPS`; `support-ta = "pca_ta_pps", "pd_adapter"`). Configured ceiling **6 A at 20 V = 120 W** (`/pe5 ita-level-dual`), matching Ulefone's "120W (20V/6A)". **Wired reverse output 10 W** via SC8510. **No wireless charging and no wireless reverse charging exist** - no device-tree node, no `wireless` power supply, no receiver IC, and the OEM does not claim it. **PROVEN absent.**
* USB-C is specified as USB 2.0; PD/TCPC/OTG paths present.
* **Rugged:** IP68 + IP69K, MIL-STD-810H, **1.5 m** drop resistance, **30 minutes at 1.5 m** water depth, Gorilla Glass 3, ~688 g. Manufacturer claims; no test report located.
* **Cooling is entirely passive**: nine thermal zones, four board NTCs plus PMIC sensors, and ten purely electrical cooling devices (backlight, charger, Wi-Fi, GPU devfreq, flashlight, CPU/GPU/modem throttling). **No fan, pump or TEC exists.** Heat-spreader material stack TEARDOWN_REQUIRED.

## Evidence index

`../verification/findings/` (per-topic resolutions), `../verification/evidence/` (device-tree and runtime extracts), `../verification/search/` (queries and sources), `../search/sources.md`, `../evidence/`, `../subsystems/`, and the original baseline `../../hardware/MASTER-HARDWARE-INVENTORY.md`.
