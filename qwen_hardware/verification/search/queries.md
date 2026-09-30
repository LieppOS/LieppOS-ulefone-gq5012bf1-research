# Verification search queries

Access date for this verification pass: **2026-09-08**. ADB was **not** available; all "live" evidence is the frozen 2026-08-31 snapshot. A negative search result means only that no useful public source was found - it never proves hardware absence.

## Internet queries actually run (provider: auto / anysearch)

| # | Query | Target unknown | Outcome |
|---:|---|---|---|
| Q1 | `Ulefone Armor 29 Pro Thermal specifications battery mAh thermal camera resolution` | U5, U9, U14, U22 | HIT - official specs incl. 21200 mAh/7.74 V, ThermoVue T2 640x512/25 Hz, 1.04" rear display |
| Q2 | `"Armor 29 Pro" Ulefone thermal imaging InfiRay resolution 640x512 specs` | U5 | provider rate-limited, superseded by Q1/Q9 |
| Q3 | `Ulefone Armor 29 Pro wireless charging support specification` | U11, U10 | HIT - no wireless charging; 120 W (20 V/6 A) PD/PPS; wired reverse 10 W |
| Q4 | `MT512GBCAV8U31 Micron uMCP LPDDR5 UFS part number` | U1, U2 | PARTIAL - Micron uMCP catalog located, exact SKU page not retrievable |
| Q5 | `Micron uMCP5 part number decoder MT512GB LPDDR5X UFS 3.1` | U1, U2 | provider rate-limited |
| Q6 | `SC8571 SouthChip charge pump datasheet 2:1 divider specifications` | U10 | PARTIAL - landed on a family/category page; the 80 W / 10 A values initially transcribed were not tied to SC8571 and are superseded by Q27 / VI35; CSP80 was later corroborated |
| Q7 | `CO5300 AMOLED display driver IC datasheet specifications` | U14 | HIT - Chipone CO5300 LTPS AMOLED driver+RAM+TCON |
| Q8 | `WL2864C OCP2131 RT5133 camera LDO LCD bias datasheet specifications` | U16 | HIT - WL2864C 7-ch camera LDO incl. VDDOIS; OCP2131 dual LCD bias |
| Q9 | `InfiRay Mini640 thermal module 640x512 12um NETD AC020 ASIC specifications` | U5, U6 | HIT - Mini640 640x512, 12 um, NETD<=40 mK, radiometric 25 Hz |
| Q10 | `GQ5012BF1 FCC ID Ulefone Armor 29 Pro internal photos teardown` | U8, U21, U24 | MISS - no FCC internal photos or teardown found |
| Q11 | `Ulefone Armor 29 Pro Thermal IP68 IP69K MIL-STD-810H certification specification` | U22 | HIT - IP68/IP69K + MIL-STD-810H, 1.5 m drop, ~688 g |
| Q12 | `Micron uMCP5 "MT512GB" part number LPDDR5X 16GB 512GB UFS 3.1 mobile` | U1, U2 | MISS |
| Q13 | `ST21NFC ST21NFCD NFC controller family variants specification STMicroelectronics` | U17 | HIT - ST21NFCD single NFC controller, active load modulation; ST54 = CLF+eSE |
| Q14 | `LN2403 LED driver IC datasheet flashlight boost` | U24 | MISS - no datasheet located |
| Q15 | `Richtek RT5133 multi-channel LDO PMIC datasheet camera` | U16 | HIT - 8 camera LDOs (2 DVDD, 4 AVDD, VIO, VAF) + 3 GPOs |
| Q16 | `SouthChip SC8510 charge pump datasheet specifications` | U10, U16 | HIT - switched-cap, 99.5%, forward 2:1 10 A, reverse 1:2 4 A |
| Q17 | `Richtek RT6160 buck-boost converter datasheet 1A` | U16 | HIT - RT6160A ACOT buck-boost, up to 3 A |

## Local "queries" (ripgrep / structural extraction) that produced the decisive evidence

| # | Command intent | Target |
|---:|---|---|
| L1 | untar `devicetree.tar`, walk `/proc/device-tree`, build phandle index, decode `connfem/epa-elna-mtk/parts` | U7 |
| L2 | read `/chosen/bootargs` for `lpddr_used_name`, `flash_type`, `PreEOLInfo`, `LifeTimeEstA/B`, `lcmname` | U1, U2, U14 |
| L3 | `rg -i 'connfem\|epa\|elna\|hwid' dmesg.txt` | U7 |
| L4 | `rg -i 'sh366003\|sc8571\|mt6375' dmesg.txt` (gauge/charger register dumps) | U9, U10 |
| L5 | enumerate every `compatible` under `soc/i2c@*` and `soc/spi*`, with `reg` + `status` | U13, U14, U15, U16, U24 |
| L6 | parse `buses.txt` driver symlinks to separate BOUND from NOT-BOUND clients | U13 |
| L7 | list `vendor_dlkm/lib/modules/*.ko` and diff against DT clients | U13 |
| L8 | decode `sensor-names` string lists for sensor0/1/2/4 | U3 |
| L9 | parse `android.scaler.availableStreamConfigurations` / HEIC arrays per camera | U20, U3 |
| L10 | full-tree byte scan for `wireless\|wlc\|mt5786\|nu16\|cps4\|stwlc\|idtp\|rx1619\|ufcs` | U10, U11 |
| L11 | decode `/charger`, `/hvbp`, `/pe5`, `/pe5p`, `/pe45`, `/pe2`, `/pe`, `mtk-gauge` profiles | U9, U10 |
| L12 | `POWER_SUPPLY_*` block extraction from `thermal-power.txt` | U9, U10, U11 |
| L13 | `unzip` + `strings` on `M170infisens.apk` / `M170infDlp.apk` native libs | U5, U6 |
| L14 | `strings` on `vendor_dlkm/lib/modules/yft_tiny2c_usb.ko` | U6 |
| L15 | read `vendor/etc/MNL_Config.xml` | U19 |
| L16 | read `vendor/etc/libnfc-hal-st.conf`, `st21nfc_conf.txt`, `strings nfc_nci.st21nfc.st.so` | U17 |
| L17 | grep stock permissions for `euicc`, `se.omapi.*` | U17, U23 |
| L18 | `rg -o '/sys/[^ ]+' vendor/etc/init/hw/init.yft.rc` (ODM option catalogue) | U11, U12, U24 |
| L19 | decode `second_pmic@5/accdet` and `/fm`, `/fmradio` | new findings |
| L20 | read `ro.lineage.display.version` / `packages.txt` to establish snapshot provenance | cross-cutting correction |

## Second-pass internet queries (access date 2026-09-08, provider: exa; OpenAI-backed search hit a 429 quota cap and was unavailable)

| # | Query | Target unknown | Outcome |
|---:|---|---|---|
| Q18 | `Ulefone Armor 29 Pro Thermal teardown FCC internal photos antenna internals` | U8, U21, U24 | MISS - only model-comparison tables (playgist) and product pages; **no teardown, no FCC internal photos** |
| Q19 | `Micron uMCP MT512GBCAV8U31 LPDDR5 UFS datasheet` (re-run of Q4/Q12) | U1, U2 | MISS - Micron uMCP family pages only; the exact SKU is still not in any public catalogue |
| Q20 | `MediaTek Dimensity 7400 MT6878 specifications LPDDR5X UFS 3.1` | U1, U2 | HIT (family) - MT6878 host interface ceiling LPDDR5/LPDDR5X + UFS; no device-specific memory part |
| Q21 | `InfiRay Mini640 AC020 thermal module 640x512 NETD datasheet` | U5, U6 | HIT - Mini640 class 640x512 / 12 um / NETD <= 40 mK / radiometric 25 Hz with AC020-class ASIC (corroborates Q9) |
| Q22 | `Microarray MaFinger MAPD002 optical in-display fingerprint Android` / `Microarray MaDev MAFP fingerprint sensor` | U15 | MISS for the device part - only the vendor's generic MaDev/MAFP family evidence (VI31); die stays TEARDOWN_REQUIRED |
| Q23 | `"FM78100" IC datasheet` + `FM78100 temperature sensor` | U6 | PARTIAL - FM78100 appears only as a contactless IR **body-temperature sensor** in wearable BOM lists (VI30); no STMicro/FMSI-style datasheet. Supports the "inherited alternate-variant name" reading |
| Q24 | `LN2403 datasheet LED driver boost` (re-run of Q14) | U24 | **HIT (was MISS in pass 1)** - LN2403 = Natlinear PWM/PFM buck **constant-current LED driver, 2 A, SOT23-5** (VI29) |
| Q25 | `Will Semiconductor WL2868C PMIC AMOLED/camera datasheet I2C` | U16 | HIT - WL2864C/WL2868C = 7-channel camera LDO PMIC (2x DVDD, 2x AVDD, VDDIO, VDDAF, **VDDOIS**), 5 VIN + VSYS, WLCSP20 (VI28) |
| Q26 | `Richtek RT5133 multi-channel LDO camera PMIC datasheet` | U16 | HIT - corroborates VI12: 8 camera LDOs + 3 GPOs |
| Q27 | `Southchip SC8571 charge pump datasheet NVDC` | U10, U16 | HIT with **correction** - the exact SC8571 product page specifies a **2-cell, 8 A** switched-capacitor direct charger at 98.65% peak efficiency; the exact-part datasheet listing gives **80-pin CSP, 3.425 x 4.151 mm**. Earlier category-page 80 W / 10 A values are withdrawn (VI35) |
| Q28 | `Awinic AW36515 AW36518 datasheet flash LED driver MediaTek` | U24 | HIT - AW36515 = dual independent 2 A flash/torch/IR LED driver; AW36518 = single 1.5 A flash/torch/IR LED driver (both I2C, MTK driver packages published) (VI32) |
| Q29 | `Ulefone Armor 29 Pro Thermal secondary rear display mini screen specs` | U14, U16 | HIT - OEM store + GSMArena + independent review all confirm the **1.04" 340x340 600-nit rear AMOLED sub-display** and the main 6.67" 1080x2400 AMOLED (VI5, VI25) |
| Q30 | `Ulefone Armor 29 Pro main camera sensor Samsung GN1 1/1.31 1.2um` | U3 | HIT - OEM spec text "50MP Main Camera **Samsung GN1** CMOS sensor, 1.2um, 7 piece lens, FOV 85, f/1.95" and "50MP+64MP+50MP"; independent review states S5KGN1 (VI7, VI25) -> the OEM-facing identity of the main slot remains GN1 even though this unit probes as IMX989 |
| Q31 | `MediaTek MT6375 PMIC datasheet backlight LED flash charger` | U9, U10, U16 | HIT - MT6375 is MediaTek's I2C **buck charger** PMIC (BATFET, VBUS OVP, AICR/MIVR input limits, OTG CV/CC reverse mode), corroborating its role as the SoC-side charger rather than a display/LED part (VI34) |
| Q32 | `OCP2131 LCD bias AVDD AVEE datasheet OneChip AMOLED` | U16 | HIT - OCP2131 = Orient-Chip programmable dual-output (positive/negative) LCD bias for TFT panels, single-inductor boost+inverting (corroborates VI15) |
| Q33 | `site:ulefone.com Armor 29 Pro Thermal side-mounted fingerprint sensor` + exact-device review cross-check | U15 | UNCLEAR - one low-quality review says side-mounted, but OEM/GSMArena passages retrieved did not explicitly settle location; conflicts with generic `tplcd_pattern` hook, so die/location/modality stay TEARDOWN_REQUIRED |

## Second-pass local queries (L21-L28)

See `../evidence/live-runtime-secondpass.md` for the full extracted tables.

| # | Command intent | Target |
|---:|---|---|
| L21 | re-parse every `buses.txt` block with correct `readlink -f` semantics -> 28 bound / 5 unbound / 5 `dummy` | U13, U14, U15, U16, U24 |
| L22 | MTK CameraProvider `Physical Devices` enumeration (`SENSOR_DRVNAME_*`) + per-camera static metadata | U3, U4, U20 |
| L23 | InputReader/EventHub device list + `fts_check_fw_normal:TP Ready,Read ID=0x56` | U13, U14 |
| L24 | Thermal HAL `Current cooling devices from HAL` + full-tree fan/TEC/BLDC scan | U21 |
| L25 | `Euicc enabled=`, `SubscriptionInfoInternal ... isEmbedded=` | U23 |
| L26 | HAL instance inventory for `ir`, `nfc`, `lights`, `vibrator`, `biometrics.face` | U24 |
| L27 | `fingerprint.txt` device nodes (`/dev/madev0`, `/dev/tkcore_fp`) | U15 |
| L28 | physical sensor list from `sensors.txt` (ICM-4x607, MMC5603, STK3A5x, SPL07) | inventory |
