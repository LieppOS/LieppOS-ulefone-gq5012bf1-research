> **Pass-2 pointer (2026-09-08).** First-pass working material. Where anything here conflicts with `../../final/` or `../../verification/findings/`, the verification pass wins. Two blanket corrections apply: the 2026-08-31 capture ran a **LieppOS GSI**, so its framework-level observations are not stock Ulefone behaviour; and `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this board's bill of materials.

# Condensed evidence: datasheet / vendor capability digest

Capability-layer (layer 1) facts only. `LIVE` = this exact board's driver/DT config (layer 2).
Source IDs (S0x) refer to `../../search/sources.md`.

## SoC / platform

### MediaTek MT6878 = Dimensity 7400 / Dimensity 7400 Ultra (S06, S07, S08)
| Item | Chip capability | Source |
|---|---|---|
| CPU | 4× Cortex-A78 @2.6 GHz + 4× Cortex-A55 @2.0 GHz, 4 nm | S06/S07 |
| GPU | Mali-G615 MC2 (MP2), 128 ALU, Vulkan 1.3 | S07 |
| APU | MediaTek NPU/APU 655 (~15 % vs D7300) | S06/S08 |
| Memory iface | LPDDR5 3200 MHz, 4×16-bit, 25.6 Gb/s; UFS 3.1 | S07 |
| ISP/camera | up to 200 MP single / 2×16/32 MP multi; stock HAL reports `MTKCamHal 3.0.00000` and `mStaticSceneSupportSensorNum:4` | S06/S07 + LIVE |
| Video (chip) | chip class: 4K30 record in aggregator sheet; AV1 decode per MTK D7x00 marketing | S07 (B-quality — needs MTK doc) |
| Display iface | MiraVision 955; WFHD+@120 Hz or FHD+@144 Hz ceiling | S08 |
| Modem | integrated 5G R16, downlink CA (3CC), VoNR, 2G–5G | S06 + LIVE band lists |
| Connect | Wi-Fi 6E class + BT5.x (integrated modem/conn path); GNSS multi-constellation | S06 + LIVE |
| USB (chip) | USB 3.2 gen1-class capable on this SoC family; **stock reports USB 2.0** (S05) | S05/S07 |

### MediaTek MT6375 (S02)
PMIC integrating charger (PE5 source per `mtk_charger_type` values), BC1.2/PE charging, fuel gauge (`mtk-gauge`, `WA_TF_TE` chip ID string), USB Type-C TCPC/PD role manager (`mtk_tcpc 1-0034`), PD/PPS source caps, Hall (`hall_ctrl`), HAPTICS NCP6321-style boost regulator, FM1/FM2 audio PA regulators, RTC (`/dev/rtc1`, `mt66xx_spmc` suspend helper).

### Richtek RT5133 (S02/S03) — main SoC PMIC, `5-0018`
16 buck + 53 LDO style per-leg regulator tree observed (`rt5133,buck{1..16}-fixed`, `rt5133_ldo{va…vm}_ana`, `vm_mirror`) + rtqop recovery/SCP/regctl nvmem cells. Capability detail (current ratings, DVFS domains) not public → UNKNOWN.

### Richtek RT6160(A) (S18) — `rt6160_vbif_0/1`, `rt6160_vpp_0/1`, `rt6160_vsrf1_ant`
ACOT buck-boost, 3 A switch, 2.2–5.5 V in/out, 600 kHz/1.2 MHz, 100 µA IQ, FEM/PA supply use; here configured as **always-on (`regulator-always-on`, boot-on) dual instances** → wireless reverse-charge / boost rail (`vpp`) and `vbif`/`vsrf1_ant` front-end rails.

### Awinic AW88394CSR (S09) — `6-0034` "speaker_amp"
Smart-K Class-D smart PA, integrated smart-boost to 10.25 V, I2S **and TDM** input, 48 kHz, 5.3 W/8 Ω @1 % THD (10.25 V boost), <1 µA shutdown, SKTune/VSys-PWM+I2C mode, AD2B differential, HWID GPIO straps (matches `i2s1-din-hwid-gpios = <&pio 38 39 42 1>`).

### Awinic AW36515 / AW36518 (S10) — `6-0063` / `8-0063` / `12-0063`
Boost flash/IR LED driver. AW36515: dual high-brightness LED channels, boost converter, I2C-programmable flash/torch currents, flash-timeout & thermal fold-back (IVFM/dimmable). AW36518: single independent 1.5 A boost flash channel (EN/GPIO + I2C). LIVE: stock binds AW36515 on I2C-6 (LED "1"), AW36518 on I2C-8 ("3") and AW36518-v2 on I2C-12 ("2").

### Awinic AW2013DNR (S11) — `11-0045`
3-channel constant-current LED sink, ≤15 mA/LED (4 current levels), manual + auto-breathing/pattern mode, I2C. Stock uses only 2 channels for `red`/`green`.

### FocalTech FT3680 / FT3683G family (S15) — `spi3.0 fts_ts@00000000`
FT3680 die: no public datasheet (UNKNOWN). Family capability (FocalTech smartphone TP line): up to 10 mutual-cap touch points, report rate to 360 Hz (FT3683G marketing), GOLED/POLED & TDDI support, "waterproof/heavy rain" touch algorithms, ESP/sleep modes, firmware-over-flash updates. LIVE: `focaltech,panel_max_display_num = <16>`, `touch_num=10`, `esd-enable`, `have_firmware_update`, `load_initial_flag`.

### Samsung ISOCELL S5KJN1 / JN1 (S12) — camera 01 + 02
50 MP, 0.64 µm, 1/2.76″, 4-in-1 remosaic (12.5 MP binned), Smart-ISO Cell, **4K60 and 1080p240** class video, 10-bit class HDR paths. LIVE: sensor sizes configured `4096x3072` (both) + extra `4096x2304` fullsize for cam02; stock records 4K30/1080p30 (per docs/camera-thermal.md + OEM spec).

### OmniVision OV64B (S13) — camera 03
64 MP, 0.7 µm, 4-in-1, on-chip remosaic, **8K30 / 4K60**, 12.5 MP binned at up to 180 fps, 3-exposure staggered (DCG) HDR, 10-bit HDR video. LIVE: `4096x3072` + `8192x6144`, `use_eeprom = <&eeprom_video1>`; HAL reports max preview/capture 8192×6144 @30.

### Sony IMX989 (S14) — camera 00
1″-type, 50.3 MP, 1.6 µm, dual-conversion-gain (DOL) HDR, 8K/4K120-class modes, 8K/4K4K per press marketing. Full datasheet not public ⇒ chip-layer detail marked B/C quality. LIVE: default array `4096x3072`, max stream `8192x6144`, physical size 13.107×9.830 mm (= 8192×6144 @1.6 µm), AF VCM `camera-af-main` `7-000a`, EEPROM `camera-eeprom0` `7-0051`; HAL exposes **no** OIS (`availableOpticalStabilization: [0]`).

### Memsic MMC5603NJ (S16) — `mmc5603_p2` @ `1-0030`
3-axis magnetometer, ±30 G range, 20-bit ADC, 0.0625 mG/LSB, ODR 1…1000 Hz, ~2 mG output noise, ~1° heading accuracy, I2C up to 400/1000 kHz, self-test, flip/orientation-compensated. LIVE: HAL maxRange reported as 32768 µT (= ±32.768 G, i.e. driver-scaled), maxRate 100 Hz (HAL cap), 100 Hz reported sensor.

### Goermicro SPL07-003 (S17) — `spl07_p2` @ `1-0077`
Absolute barometer 300–1100 hPa (≈ +9 000 m … −500 m), supply 1.5–3.6 V / I/O 1.65–3.6 V, −40…+85 °C, I2C/SPI, up to 100 Hz oversampling modes. LIVE: HAL exposes 300–1100 hPa at 10/20/50 Hz.

### InvenSense/TDK icm4n607 (S21 family) — `icm4n607_acc`/`_gyro` @ `1-0068`
Exact part undocumented publicly. Family (ICM-426xx/ICM-4x6xx): 6-axis IMU, accel ±2/4/8/16 g, gyro ±15.6…±2000 dps, gyro noise ~0.005–0.007 dps/√Hz, ODR to 32 kHz (low-power 1 kHz), 2 KB FIFO + FIFO watermark, APEX engine (step/pedometer/tap/drag/no-activity/wrist-off, hardware TAP-with-Android-WoW), RoP self-test, 1.71–3.6 V. LIVE: HAL reports ±2 g (driver default) and ±2000 dps, 500 Hz max rate, "High-G" + "Game VR" + 4 virtual sensors; APEX-class features exist as *vendor extensions* only.

### ST ST21NFCB/ST21NFCD family (S19) — `6-0008`
Single-chip 13.56 MHz contactless front end: card mode (ISO14443 A/B, FeliCa, ISO15693/18000-3M3), reader/writer, NFC-DEP / P2P, CEE, low-power modes, WLCSP64/WFBGA64, EAL5+/PCI-class secure variants. LIVE: NCI HAL `android.hardware.nfc-service.mediatest`, `libst21nfc_aidl_nci_client.so`, firmware `st21nfcbin_hdr_103a13111000_93111.bin` + 3 `.se` images; SE services `com.st.android.nfc_extensions_18/19`; NFC settings flags all zero (see UNKNOWN-HARDWARE).

### Qorvo QM42195 / Skyworks SKY853xx-857xx class Wi-Fi FEMs (S20) — `connfem`
QM42195: Qorvo 5 GHz (5–7 GHz, i.e. 5 GHz + 6 GHz Wi-Fi 6E/7) high-power front-end module (LNA+switch class). SKY85320/SKY85380/SKY85720/SKY85732/SKY85743: Skyworks 2.4/5/6 GHz Wi-Fi FEM family. LIVE: all ten bound as one `mediatek,connfem` multiplexer with HWID-selectable GPIO tables (`bt-hwid-gpios`, `wl-hwid-gpios`) ⇒ multi-source/multi-build RF front end; per-unit population UNKNOWN.

### Thermal core — M170 / M170L2 / "ThermoVue T2" (S21) — `miko_src_sensor@0`, `miko_mcu@0` (FM128 I2C, slave `0x3c`)
No public datasheet for the fitted module. Market analogues (InfiRay M3640T/T2-class, 640×512 12 µm LWIR uncooled VOx): 640×512 @ 12 µm/50° lens, 25 Hz, radiometric −20…+550 °C (analogue parts), NETD ≤40–50 mK, FFC/shutter, USB/UVC or MIPI attachment. OEM claim for this device (S04): 640×512 @ 25 Hz + "super-resolution" 1280×1024 @ 3 fps.

### Southchip SC8571 / SC8510 (S22) — `11-0066`, `6-0067`, `6-0069`
Exact datasheets not public (UNKNOWN capability detail). Family: I2C-programmable switched-capacitor (charge-pump) rechargeable battery charger, ~10 A-class parallel-pump parts in the Southchip charge-pump lineup; live DT sets `compatible = "sc8571_charger"`, `parent_trickle-charger`, `powerntc-temp-ohm = <100>`.

### SinhMicro/other SH366003 (S22) — `9-0055` "3rd-gauge", `sh366003-iconsumer`
Not publicly documented ⇒ UNKNOWN; role per DT/consumer contract: independent 3rd-party fuel gauge (SOC/SoP/coulomb counting) with `i2c_master_stress` debug + `power_supply_get_status` consumer hooks.
