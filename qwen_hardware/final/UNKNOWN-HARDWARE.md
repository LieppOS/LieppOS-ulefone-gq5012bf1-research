# Unknown hardware and unresolved questions

**Revised 2026-09-08** after second-pass verification in `../verification/`. Each row carries the reconciled status; UNKNOWN/TEARDOWN_REQUIRED is retained whenever software cannot identify physical population. Full reasoning for every row is in `../verification/findings/`.

Status vocabulary: PROVEN, STRONGLY_SUPPORTED, LIKELY, POSSIBLE, UNKNOWN, TEARDOWN_REQUIRED.

## Resolved or substantially narrowed

| ID | Question | Outcome | Status | Finding |
|---|---|---|---|---|
| U1 | DRAM vendor/part/channel/speed | **Micron uMCP `MT512GBCAV8U31`, 16 GiB LPDDR5-class**, from the bootloader's own detection. Grade/data-rate/channel map still open. | RESOLVED (identity) / UNKNOWN (timings) | `dram.md` |
| U2 | UFS vendor/device/gear/health | **512 GB UFS die in the same Micron uMCP**; UFSHCI at 0x112b0000 with RPMB + 2 boot LUs. **Health PROVEN: PreEOL Normal, life-time A/B 0-10 %.** Gear/version still open. | RESOLVED (identity+health) / UNKNOWN (gear) | `ufs.md` |
| U3 | Main camera die; IMX989 vs GN1 | **Multi-source slot** (`imx989` / `s5kgm2sp` / `imx989cts` / `s5kgn1sp`). This handset's MTK CameraProvider runtime enumeration is **`SENSOR_DRVNAME_IMX989_MIPI_RAW`** with 1-inch-class geometry; Ulefone and an independent exact-device review document S5KGN1 retail population. | RESOLVED for this capture / variant-dependent by lot | `camera-main-identity.md` |
| U5 | Thermal detector, NETD, radiometry | **InfiRay/InfiSense Mini640-class, 640x512, 12 um, NETD < 40 mK, radiometric 25 Hz, AC020 ASIC** ("ThermoVue T2"). | STRONGLY_SUPPORTED | `thermal-detector.md` |
| U6 | Role of "FM78100" | Not a thermopile: it is the **power-sequencing and `sensor_id` endpoint of the InfiRay module**; the name is inherited from another ODM variant. | PROVEN | `fm78100-role.md` |
| U7 | Selected ConnFem FEM pair | HWID resolves to **`nofem + nofem`** - **no external Wi-Fi/BT front-end module**; MT6637 internal PA/LNA only. | PROVEN | `connfem-selected-fem.md` |
| U9 | Battery cells / topology / thermistors | **2S, 7.74 V nominal, 8.90 V CV (4.45 V/cell)**, dual gauges, 4 board NTCs + pack thermistor, 79 %/26 cycles/SoH 94. Capacity gap remains. | RESOLVED (topology) / UNKNOWN (capacity gap) | `battery-pack.md` |
| U10 | 120 W and UFCS/PD/PPS profiles | **PD + PPS only; UFCS absent.** 6 A at 20 V = 120 W configured; 2 x bound SC8571 (exact part: 2-cell, 8 A, 98.65% peak; board caps each at 6.55 A) + SC8510 reverse; 10 W wired reverse. | RESOLVED configuration / delivered power unmeasured | `charging-capabilities.md` |
| U11 | Wireless / reverse-wireless hardware | **Not present.** No node, no `wireless` power supply, no receiver IC; OEM claims wired-only 10 W reverse. Prior "50 W wireless / 30 W reverse" claim disproven. | PROVEN (absent) | `wireless-charging.md` |
| U12 | Haptic motor and driver | **ERM motor on the MT6369 `VIBR` LDO via `regulator-vibrator`, 2.2-3.5 V; no haptic driver IC.** Motor P/N still open. | RESOLVED (topology) / TEARDOWN_REQUIRED (part) | `haptics.md` |
| U13 | Is Ilitek 0-0041 populated? | **No** - Ilitek and ChipOne-TDDI are alternates sharing FT3680's IRQ/reset pins, with no driver shipped. | STRONGLY_SUPPORTED | `ilitek-population.md` |
| U14 | Rear panel DDIC and Hynitron model | **Chipone CO5300** driving a **1.04-inch 340x340 AMOLED, 600 nits**, on SPI0 at 60 MHz; Hynitron single-touch digitizer. (Prior "3.97-inch" corrected.) | PROVEN | `rear-display.md` |
| U16 | OCP2131 / WL286x / RT5133 / RT6160 limits and population | Active tier identified: OCP2131 bound display bias and a bound **WL2864C/WL2868C-family** 7-LDO camera PMIC with several DT rail values. Exact WL revision UNKNOWN. RT5133 and 2 x RT6160 are identified by datasheet but unbound; physical population UNKNOWN. | RESOLVED (functions) / UNKNOWN (WL revision, unbound population, runtime rails) | `power-support-ics.md` |
| U17 | ST21NFC variant | **ST21NFC-family controller-only CLF** (ST21NFCD class) with `st21nfc_fw7` and board RF tuning; **no eSE**, UICC-only off-host routing. | STRONGLY_SUPPORTED | `st21-variant.md` |
| U19 | GNSS constellations and L5 | **GPS + GLONASS + Galileo + BeiDou + NavIC + QZSS, dual-band L1 + L5/E5a/B2a**, L5 DCB calibrated for chip 0x6637, OSNMA enabled. | STRONGLY_SUPPORTED | `gnss.md` |
| U20 | Camera `availableStreamConfigurations` | **Fully decoded** for all four cameras (211-215 rows, six formats, up to 8192x6144 / 9216x6912, 8K still on the main camera). | PROVEN | `camera-stream-configurations.md` |
| U22 | IP/MIL detail and glass grade | IP68 + IP69K, MIL-STD-810H, **1.5 m** drop, 30 min at **1.5 m**, Gorilla Glass 3, ~688 g. (Prior "2 m" corrected.) Claim-level only. | STRONGLY_SUPPORTED (claim) | `ip-mil-certification.md` |
| U23 | eSIM / eUICC presence | **Not present.** No feature declaration, no LPA, only `se.omapi.uicc`; OEM lists Nano + Nano + microSD. | PROVEN (absent) | `esim-euicc.md` |
| U24 | Hidden board-level support ICs | SPMI PMIC tier, CO5300, SC8510, FM/headset paths and complete lighting tier catalogued. **LN2403 now LIKELY identified as Natlinear 2 A buck LED driver**; IR PWM path is proven but emitter/usable HAL unverified. Passives remain invisible. | RESOLVED (bound active parts) / LIKELY (LN2403) / TEARDOWN_REQUIRED (passives/emitter) | `hidden-support-ics.md` |

## Still open

| ID | Question | Current best answer | Status | Exact physical evidence required |
|---|---|---|---|---|
| U4 | VCM <-> OIS <-> lens mapping | DW9781C is fitted/bound and three AF VCMs are fitted, but sensor0 carries `oisvdd`, sensor4 carries `oisen`, and the actuator shares sensor1/sensor4's bus. No software artefact assigns it safely to one lens; all cameras expose OIS OFF only. | **UNKNOWN / TEARDOWN_REQUIRED** | camera-module EEPROM/BOM, teardown, or controlled actuator-to-image-path test |
| U8 | Antenna count, MIMO order, filter chain | Wi-Fi/BT: **no external FEM (PROVEN)**. Cellular front end is MIPI-RFFE and architecturally invisible to software | **TEARDOWN_REQUIRED** | FCC internal photographs (none published for GQ5012BF1) or a teardown; RF test equipment for MIMO order |
| U15 | Microarray fingerprint die P/N, location and modality | Microarray/MaFinger on SPI1 at 8 MHz behind TrustKernel/TkCore TEE. Generic `tplcd_pattern` suggests optical; one review says side-mounted. Neither is die/location proof. | **TEARDOWN_REQUIRED** | package marking and physical mounting; stock enrolment observation can narrow modality/location |
| U18 | Bluetooth revision, LE Audio, Auracast | MT6637 controller with no external FEM; OEM claims BT 5.4. The LE-Audio properties seen earlier came from a **GSI**, not stock | **UNKNOWN** | enable BT on **stock** and capture HCI `LE Read Local Supported Features` + `Read Local Supported Commands` (read-only) |
| U21 | Cooling material stack | Passive only - **no fan, pump or TEC exists (PROVEN)**; graphite/copper/vapour-chamber composition unknown | **TEARDOWN_REQUIRED** | teardown with layer photography |
| U1b | LPDDR grade, data rate, channels/ranks | LPDDR5-class on an MT6878 controller | **UNKNOWN** | rooted DRAM debugfs read, or Micron datasheet for the SKU |
| U2b | UFS version and negotiated gear/lanes | UFS with RPMB + 2 boot LUs | **UNKNOWN** | rooted `ufs_version` / `current_gear` sysfs read |
| U9b | 8594 mAh gauge design vs 10600 mAh rating | Most likely the value programmed into the gauge, not a smaller pack | **UNKNOWN** | full metered charge/discharge, or read the SH366003 design-capacity register |
| U10b | Delivered charging power and derating | 120 W configured and silicon-capable | **UNKNOWN** | certified 20 V/6 A PPS source with inline power logging |
| U16b | Runtime-programmed per-rail voltages/current limits | several WL-family values are visible in DT (AVDD 2.85 V, DVDD 1.2 V, VREF/RVP 1.8 V); remaining live regulator state is unmeasured | **UNKNOWN (remainder)** | `/sys/class/regulator/*/{name,microvolts}` read on a rooted stock boot |
| U24b | Passives: ESD arrays, level shifters, crystals, RF filters | not software-visible by nature | **TEARDOWN_REQUIRED** | board photography |
| NEW | Genuine **stock** framework behaviour (brightness curve, camera video menu, LE Audio toggles) | never measured - the only capture was a GSI | **UNKNOWN** | a fresh read-only capture on the untouched stock system |

**Policy:** Unknown is a valid result. It must not be silently converted into an installed part, a chip ceiling, or a stock feature. Equally, a *negative* established by several independent lines of evidence (U11 wireless charging, U23 eSIM, U7 external FEM) is a genuine finding, not an absence of information.
