# Verification sources

Access date: **2026-09-08**. Quality: **A** = vendor/OEM/datasheet primary; **B** = independent database/aggregator; **C** = community/retail listing/inference. Scope: exact-device / exact-chip / family-level / generic.

## Local sources (VL)

| ID | Source path | Exact claim it supports | Quality | Scope |
|---|---|---|---|---|
| VL1 | `workspace/gq5012bf1/snapshots/.../devicetree.tar` -> `/chosen/bootargs` | `lpddr_used_name=MT512GBCAV8U31`, `flash_type=12`, `PreEOLInfo=0x1`, `LifeTimeEstA/B=0x1`, `lcmname=yft_vtdr6115_...` | A | exact-device |
| VL2 | same -> `/model-external-name`, `/model-part-name` | SoC orderable part `MT6878V/TZA` (internal `MT8873`) | A | exact-device |
| VL3 | same -> `/memory@40000000/reg` | 16 GiB physical DRAM window | A | exact-device |
| VL4 | same -> `/connfem` (`hwid gpio`, `parts`, `pinctrl-names`) | 7 selectable FEM pairs; HWID = GPIO 131/132/92; indices 0-2 = nofem+nofem | A | exact-device |
| VL5 | `.../dmesg.txt` ConnFem lines | runtime resolution: FEM not available, BT vid/pid == 0 | A | exact-device |
| VL6 | `kernel-research/nothing-mt6878/.../connfem_dt_parser.c`, `connfem_cfg.c`, `connfem_api.c` | `available = true` iff `fem_info.id != 0`; `nofem` -> id 0 | A | exact-chip (driver) |
| VL7 | `stock/partitions/vendor/firmware/connfem.cfg` | 0 bytes -> no config-file override of the DT result | A | exact-device |
| VL8 | `.../dmesg.txt` SH366003 monitor lines | `Volt=8397 SoH=94 cycnt=26 Rc=6713 FCC=8594 Vchg=8900 Ichg=9500` | A | exact-device |
| VL9 | `.../thermal-power.txt` `===PSY===` block | full power_supply inventory; no wireless supply; `USB_TYPE=... PD PD_PPS`; `CONSTANT_CHARGE_VOLTAGE=4450` with `VOLTAGE_NOW=8397000` | A | exact-device |
| VL10 | DT `/hvbp`, `/pe5`, `/pe5p`, `/charger` | `vbat-cv=8900 mV`; `pe5 ita-level-dual` 6000 mA at `vta-cap-max` 20000 mV; `support-ta = pca_ta_pps, pd_adapter` | A | exact-device |
| VL11 | DT `soc/i2c@11e02000/sensor0@10/sensor-names` | main slot supports `imx989`, `s5kgm2sp`, `imx989cts`, `s5kgn1sp` | A | exact-device |
| VL12 | `.../camera-media.txt` | driver names per camera; RAW16 4096x3072 (cam0) vs 4080x3072 (cam1/2); OIS `[0]`; full stream-config arrays | A | exact-device |
| VL13 | `.../buses.txt` driver symlinks | `hyn_ts` bound at 0-0015; ilitek 0-0041 and chipone 0-0048 unbound; `spi_tiny_lcd_co5300`; `madev`/`microarray_fp_tee`; `sc8510` | A | exact-device |
| VL14 | `stock/partitions/vendor_dlkm/lib/modules/` | no Ilitek/ChipOne modules shipped | A | exact-device |
| VL15 | DT `soc/i2c@11c20000/{hynitron@15, ilitek@41, chipone_tddi@48}` | Hynitron 340x340 single-touch; Ilitek/ChipOne share IRQ 7 / reset 6 with the main FT3680 | A | exact-device |
| VL16 | `stock/.../system/app/M170infisens\|M170infDlp` native libs | `infiray`, `mini640`, `tiny2c`, `MINI225/238/264/640`, `AC020` SDK | A | exact-device |
| VL17 | `stock/.../vendor/etc/init/hw/init.yft.rc` | `/mnt/vendor/nvcfg/infiray`; `fm78100-sensor` sysfs (`objs_temp`/`mems_temp`/`ntc_temp`); ODM-wide option catalogue incl. MT5786 wireless, `aw_vibrator`, `rtc6226` | A | exact-device (ODM-wide file) |
| VL18 | `vendor_dlkm/lib/modules/yft_tiny2c_usb.ko` strings | driver only does 1V8/3V3/5V/IO3V3 power sequencing + `sensor_id` read + `tiny2c_usb_mode` | A | exact-device |
| VL19 | `stock/.../vendor/etc/MNL_Config.xml` | `GnssMode=10` (GPS+GLONASS+Galileo+BeiDou+NavIC), `L1Only=0`, `L5Test=1`, `DisableSignal=0`, L5 DCB calibrated for chip `6637`, OSNMA on | A | exact-device |
| VL20 | `vendor/etc/libnfc-hal-st.conf`, `st21nfc_conf.txt`, `nfc_nci.st21nfc.st.so` | ST21NFC path with `st21nfc_fw7.bin`; HAL also supports ST54J/K/L; UICC+eSE routes | A | exact-device |
| VL21 | stock permissions dirs | only `android.hardware.se.omapi.uicc`; no `se.omapi.ese`; no `android.hardware.telephony.euicc` | A | exact-device |
| VL22 | DT `/regulator-vibrator` + `second_pmic@5/regulators/vibr` | haptics = `regulator-vibrator` on `mt6369_vibr`, 2.2-3.5 V, 680 us ramp; no haptic driver IC | A | exact-device |
| VL23 | DT `second_pmic@5/accdet`, `/fm`, `/fmradio` | 3.5 mm headset detect with 3/4-key thresholds; FM receiver enabled with `fm_lna_gpio`; `gpio-accdet-fm-switch` | A | exact-device |
| VL24 | `stock/.../system_ext/app/YftFmRadio/YftFmRadio.apk`, `vendor/firmware/fm_cust.cfg` | stock FM radio application and FM firmware present | A | exact-device |
| VL25 | `.../identity.txt`, `.../packages.txt` | `ro.lineage.display.version = LieppOS-23-20260830-VANILLA-EROFS-GSI`, KernelSU context, zero Ulefone packages | A | exact-device |
| VL26 | `vendor/etc/camera/eis/morphoEISCalibration_DOOGEE_M24PS.bin` | shared ODM software base with a Doogee model | A | exact-device |
| VL27 | `.../camera-media.txt` lines 31-45 (second pass) | MTK CameraProvider `Physical Devices`: `[00] SENSOR_DRVNAME_IMX989_MIPI_RAW`, `[01] S5KJN1`, `[02] S5KJN1MAIN2`, `[03] OV64B`; per-camera `pixelArraySize` / `physicalSize` / `availableOpticalStabilization = [0]` | A | exact-device |
| VL28 | `.../thermal-power.txt`, `.../telephony.txt`, `.../sensors.txt`, `.../fingerprint.txt`, `.../displays.txt` (second pass) | Thermal HAL cooling devices (no fan/TEC anywhere); `Euicc enabled=false`, `isEmbedded=0`; 5 physical sensors (ICM-4x607, MMC5603, STK3A5x, SPL07); `/dev/madev0` + `/dev/tkcore_fp`; a single SurfaceFlinger display (1080x2400) plus the 340x340 `hyn_ts` digitizer | A | exact-device |

Every `VL`/`VI` id above is cited by at least one document. The `VL` ids backing U-items are cited
in `../findings/`; **VL2** (SoC orderable part `MT6878V/TZA`) and **VL26** (shared ODM software base
with a Doogee model) and **VL28** (runtime sensor / cooling / HAL inventory) back inventory-level claims
in `../../final/MASTER-HARDWARE-INVENTORY.md` rather than a U-item finding. Second-pass raw extracts are
preserved in `../evidence/live-devicetree-secondpass.txt` and `../evidence/live-runtime-secondpass.md`.

## Internet sources (VI)

| ID | Title | URL | Publisher | Exact claim it supports | Quality | Scope |
|---|---|---|---|---|---|---|
| VI1 | Armor 29 Pro Thermal - Specs | https://store.ulefone.com/pages/armor-29-pro-thermal-specs | Ulefone (OEM) | "21200mAh Battery (Equivalent to 10600mAh, 7.74V)"; ThermoVue T2 640x512, 25 Hz, 12 um, NETD <40 mK, FOV 56x42, -20..550 C, +/-2 C; Wi-Fi 6E 2.4/5/6 GHz; BT 5.4; 120 W; wired reverse 10 W | A | exact-device |
| VI2 | Armor 29 Pro Thermal Version Spec | https://www.ulefone.com/pages/armor-29-pro-thermal-version-spec | Ulefone (OEM) | 120 W flash charging, wired reverse charging 10 W, no wireless charging listed | A | exact-device |
| VI3 | Armor 29 Pro Thermal - Ulefone UK | https://ulefone.co.uk/armor-29-pro-thermal/ | Ulefone (regional OEM) | ThermoVue T2 sensor + "Independent Infrared ISP" + ThermoVue Pro app; 1.04" rear sub-display | A | exact-device |
| VI4 | Armor 29 Pro - Ulefone UK | https://ulefone.co.uk/armor-29-pro/ | Ulefone (regional OEM) | "Charging: 120W (20V/6A)", "Reverse Charging: 10W", headphone jack, Nano+Nano+microSD, band lists | A | exact-device |
| VI5 | Ulefone Armor 29 Pro Thermal - full specs | https://www.gsmarena.com/ulefone_armor_29_pro_thermal_5g-14104.php | GSMArena | Main 6.67" AMOLED 1080x2400 120 Hz 2200 nits peak, Gorilla Glass 3; **secondary rear AMOLED 1.04", 340x340, 600 nits**; 50 MP f/2.0 23 mm 1/1.31" 1.2 um; 64 MP f/1.8 night vision | B | exact-device |
| VI6 | Ulefone Armor 29 Pro technical specifications | https://www.gsmchoice.com/en/catalogue/ulefone/armor-29-pro/ | GSMchoice | "Wireless battery charging" field left empty; USB PD up to 120 W; 16 GB RAM / 512 GB | B | exact-device |
| VI7 | Ulefone Armor 29 Pro Thermal product page | https://www.ulefone.com/products/armor-29-pro-thermal-version | Ulefone (OEM) | IP68/IP69K, MIL-STD-810H, 1.5 m drop, 30 min at 1.5 m water; "1/1.31\" Ultra-Large Sensor"; "50MP Samsung ISOCELL"; 117.3 deg AF ultrawide | A | exact-device |
| VI8 | Ulefone Armor 29 Pro Thermal | https://www.notebookcheck.net/Ulefone-Armor-29-Pro-Thermal.1169895.0.html | Notebookcheck | IP68/IP69K, MIL-STD-810H, 1.5 m drop, ~688 g mass | B | exact-device |
| VI9 | Ulefone Armor 29 Ultra product page | https://www.ulefone.com/products/armor-29-ultra | Ulefone (OEM) | The **Ultra** sibling is the model marketed with the 1-inch Sony IMX989 - explains why the shared DT carries an IMX989 driver | A | family-level |
| VI10 | Charge pump charger product category | https://www.southchip.com/en/product-category/Chargepumpcharger2 | SouthChip (vendor) | Family-level evidence that SouthChip's switched-capacitor charger line provides high-efficiency/high-current direct charging. Values initially attributed to SC8571 from this category page are superseded by the exact-product source VI35 | A | family-level |
| VI11 | SC8510 datasheet summary | https://datasheet.icspec.com/datasheet/datasheetDetail/114604 | icspec (distributor DB) | SC8510 switched-capacitor: up to 99.5% efficiency, forward 2:1 discharge to 10 A, reverse 1:2 charge to 4 A | B | exact-chip |
| VI12 | RT5133 product page | https://www.richtek.com/Home/Products/Power%20Management%20IC/RT5133 | Richtek (vendor) | RT5133 = integrated PMIC with **8 camera LDOs** (2 DVDD, 4 AVDD, 1 VIO, 1 VAF) **+ 3 GPOs** | A | exact-chip |
| VI13 | RT6160A datasheet | https://www.mouser.com/datasheet/2/1458/DS6160A_02-3104604.pdf | Richtek via Mouser | RT6160A single-inductor ACOT synchronous buck-boost, up to 3 A | A | exact-chip |
| VI14 | WL2864C product page | https://www.ovt.com/products/wl2864c/ | Will Semi / OmniVision (vendor) | 7-channel camera LDO: 2 DVDD, 2 AVDD, 1 VDDIO, 1 VDDAF, **1 VDDOIS** | A | exact-chip |
| VI15 | OCP2131 datasheet | https://datasheet4u.com/datasheets/ORIENT-CHIP/OCP2131/1309392 | datasheet4u (aggregator) | OCP2131 = Orient-Chip programmable dual-output (positive/negative) LCD bias for panels up to 10" | B | exact-chip |
| VI16 | CO5300 datasheet (Chipone) | https://datasheet4u.com/datasheets/CHIPONE/CO5300/1577323 | datasheet4u (aggregator) | CO5300 = Chipone single-chip LTPS AMOLED driver with RAM, gate drivers and timing controller (smartwatch-class panels) | B | exact-chip |
| VI17 | CO5300 driver library | https://github.com/Infineon/display-amoled-co5300 | Infineon (GitHub) | CO5300 drives small MIPI-DSI/QSPI AMOLED panels (e.g. 1.43" 466x466) | A | exact-chip |
| VI18 | Mini 640 uncooled LWIR module | https://www.thermal-image.com/product/mini-640-uncooled-lwir-thermal-camera-module/ | module distributor | Mini640: 640x512, 12 um pitch, radiometric version 25 Hz | C | exact-chip |
| VI19 | 640x512 12 um thermal modules (MINI + ASIC) | https://www.gst-ir.net/products/uncooled-thermal-modules/itl-thermal-modules/ | GSTiR | MINI-series 640x512 / 12 um / typical NETD <= 40 mK with companion ASIC | C | family-level |
| VI20 | "Iray Infiray Infisense Mini2 640" listing | https://www.aliexpress.com/i/1005010043564870.html | retail listing | Confirms InfiRay/InfiSense branding on the same Mini640 module family (explains the `M170infisens` app name) | C | family-level |
| VI21 | ST21NFCD product page | https://www.st.com/en/secure-mcus/st21nfcd.html | STMicroelectronics (vendor) | ST21NFCD = single NFC controller IC for mobile, active load modulation | A | exact-chip |
| VI22 | NFC solutions from ST | https://www.mouser.com/pdfdocs/enNFC_Solutions_from_ST.pdf | ST via Mouser | ST21NFC = NFC controller only; ST54 = NFC controller **plus** integrated eSE | A | family-level |
| VI23 | Micron uMCP (UFS-based MCP) | https://www.micron.com/products/multichip-packages/ufs-based-mcp | Micron (vendor) | Micron uMCP5 = LPDDR5X + UFS in one package; "MT" prefix is Micron's part-number namespace | A | family-level |
| VI24 | uMCP part catalog | https://www.micron.com/products/multichip-packages/ufs-based-mcp/part-catalog | Micron (vendor) | Catalogue exists but the exact `MT512GBCAV8U31` SKU page was not retrievable in this pass | A | family-level |

## Second-pass internet sources (VI25-VI34)

| ID | Title | URL | Publisher | Exact claim it supports | Quality | Scope |
|---|---|---|---|---|---|---|
| VI25 | Ulefone Armor 29 Pro Thermal - editor review | https://www.devicespecifications.com/en/editor-review/48a012d | DeviceSpecifications | Main camera = **Samsung S5KGN1, 1/1.31", 1.2 um**; rear 1.04" AMOLED 340x340 600 nits inside the camera island; 21200 mAh (2-cell) pack; 120 W wired / 10 W reverse | B | exact-device |
| VI26 | Review: Ulefone Armor 29 Pro specs and features | https://unite4buy.com/review/Review-Ulefone-Armor-29-Pro/ | unite4buy | "huge 21200 mAh battery, old Li-Pol technology", >3 cm thickness, >600 g, **additional 1.04-inch AMOLED screen in the rear shell**, **side fingerprint scanner**, LED light panel | C | exact-device/sibling |
| VI27 | Armor 29 Pro Thermal Version spec page (camera text) | https://www.ulefone.com/pages/armor-29-pro-thermal-version-spec | Ulefone (OEM) | "50MP Main Camera **Samsung GN1** CMOS sensor, 1.2um, 7 piece lens, FOV 85deg, f/1.95 large sensor"; "50MP+64MP+50MP"; sensor list includes **Infrared sensor** and **Thermal sensor** | A | exact-device |
| VI28 | WL2864C/WL2868C product overview | https://en.sekorm.com/doc/2485162.html (family) / https://www.ovt.com/products/wl2864c/ | Will Semiconductor via aggregator / vendor | WL2864C and WL2868C are 7-channel camera PMICs (2x DVDD, 2x AVDD, VDDIO, VDDAF, **VDDOIS**), 5 VIN + VSYS, I2C, WLCSP20. Local module/DT supports both; the exact fitted revision is unresolved | A/B | exact-family |
| VI29 | LN2403 datasheet listing | https://datasheet4u.com/datasheets/natlinear/LN2403/1316527 and http://www.dcx-ic.com/baiguangLEDqudong/314.html | Natlinear via aggregators | LN2403 = CMOS **PWM/PFM buck constant-current LED driver, up to 2 A**, 2.5-6.0 V supply, 40 uA quiescent, 100 % duty capable, SOT23-5, with OVP/OCP/OTP protection | B | exact-chip |
| VI30 | Wearable product BOMs naming FM78100 | https://wotchout.com/en/product/medicalwatch1/ and https://www.alibaba.com/product-detail/Open-API-4G-Elderly-Watch-Fall_1601297702503.html | device resellers | FM78100 is listed as the **infrared (contactless) body-temperature sensor** in 4G smartwatch BOMs -> the DT node name `fm78100` does denote a real IR temperature part, on other ODM builds | C | family-level |
| VI31 | libfprint-microarray (MicroarrayTechnology MAFP) | https://github.com/jdillon/libfprint-microarray | community | Microarray Technology's fingerprint family is marketed as **MaDev / MAFP**; confirms the vendor behind `madev`/`mafinger` naming | C | family-level |
| VI32 | AW36515 / AW36518 datasheets | https://www.awinic.com/en/productDetail/AW36518FCR and https://xonstorage.z8.web.core.windows.net/pdf/awinic_aw36515fcr_apr22_xonlink.pdf | Awinic (vendor) / distributor | AW36515 = high-efficiency **dual independent 2 A** flash/torch/IR LED driver with 2 MHz or 4 MHz synchronous boost and IVFM; AW36518 = **independent 1.5 A** flash/IR LED driver, FCQFN 1.6x1.2-10L; both have published MTK driver packages | A | exact-chip |
| VI33 | CO5300 datasheet (Chipone) full text | https://admin.osptek.com/uploads/CO_5300_Datasheet_V0_00_20230328_07edb82936.pdf and https://components.espressif.com/components/espressif/esp_lcd_co5300/versions/2.0.3/readme | Chipone via module vendor / Espressif | CO5300 = single-chip RAM display driver for **LTPS AMOLED** with gate drivers + TCON + level shifters, interfaces **SPI / QSPI / MIPI-DSI**, TE output available - matching the `spi_tiny_lcd_co5300` driver on SPI0 at 60 MHz | A | exact-chip |
| VI34 | MediaTek MT6375 charger driver (open-source MTK BSP) | https://github.com/Mandi-Sa/micode-xaga-s-oss/blob/xaga-s-oss/drivers/power/supply/mt6375-charger.c | MTK BSP via GitHub mirror | MT6375 register set = buck **charger** with CHG_EN/BUCK_EN, BATFET delay/disconnect, VBUS OVP, AICR/MIVR input limits, OTG_CV/OTG_CC (reverse mode) and battery-protection interrupts - i.e. MT6375 is the SoC-side charger/PMIC, not a display part | B | exact-chip |
| VI35 | SC8571 exact product page and datasheet listing | https://www.southchip.com/en/product/SC8571 and https://en.sekorm.com/doc/3680367.html | SouthChip (vendor) / Sekorm | **2-cell, 8 A switched-capacitor direct charger**, 98.65% peak efficiency, integrated FETs optimised for 50% duty cycle so cable current is half battery current; exact-part listing identifies an **80-pin CSP, 3.425 x 4.151 mm** package | A/B | exact-chip |

### Confidence changes produced by the second pass

| Item | Pass 1 | Pass 2 | Why |
|---|---|---|---|
| U24 LN2403 | node PROVEN, **part UNKNOWN** | **LIKELY = Natlinear LN2403 2 A buck LED driver** | datasheet-class identification now available (VI29); the DT drives it with a PWM enable pair (`ln2403_pwmon` / `ln2403_pwmoff_high/low`) + dedicated power/enable GPIOs, which is exactly a buck-LED-dimmer wiring |
| U10 SC8571 rating | 80 W / 10 A / CSP80 initially attributed from category page (VI10) | **2-cell, 8 A switched-cap direct charger, 98.65% peak, CSP80** (VI35) | exact-product source corrects the current/power attribution; exact-part listing independently confirms CSP80 |
| U16 camera LDO variant | WL2864C (DT name) | **WL2864C/WL2868C family proven; exact revision UNKNOWN** | bound module is `custom_ldo_wl2868`, while DT carries both `id_val_2864 = 0x28` and `id_val_2868c = 0x82`; without the probed ID register neither name selects the die (VL13 + L21 + VI28) |
| U3 main die | IMX989 STRONGLY_SUPPORTED on this unit; OEM says GN1 | unchanged, now **doubly corroborated**: runtime `SENSOR_DRVNAME_IMX989_MIPI_RAW` (L22) vs three OEM/retail sources naming S5KGN1 (VI7, VI25, VI27) | dual-source main-camera BOM remains the only reading consistent with both |
| U6 `fm78100` | repurposed node = thermal-module power/ID endpoint (PROVEN from driver strings) | unchanged; **external corroboration** that FM78100 really is an IR temperature part on other builds (VI30) | strengthens the "inherited variant name" explanation |
| U24 flash/auxiliary lighting | partially catalogued | AW36515 + 2x AW36518 + AW2013 RGB + LN2403 path identified with datasheets | L21 + VI29 + VI32 |
