# GQ5012BF1 UNKNOWN-HARDWARE second-pass verification report

**Device:** Ulefone Armor 29 Pro Thermal / `GQ5012BF1`
**Verification date:** 2026-09-08
**Scope:** re-check every conclusion from the existing verification pass, attack residual UNKNOWN items with
additional local/runtime/DT evidence and targeted internet/datasheet research, then reconcile the five
authoritative reports under `../../final/`.

## Executive verdict

The second pass did **not** manufacture closure where the evidence stops. It strengthened several hardware
identities, corrected two source/method errors, resolved LN2403 at LIKELY confidence, and deliberately
**downgraded three over-confident conclusions**:

1. **OIS lens ownership:** DW9781C presence and binding remain PROVEN, and all four vendor-HAL cameras expose
   OIS OFF only; the prior "probably main lens" mapping is withdrawn. Sensor0 carries `oisvdd`, sensor4
   carries `oisen`, and bus placement cannot select the gimbal. **Lens mapping = UNKNOWN / TEARDOWN_REQUIRED.**
2. **Camera-LDO / alternate power IC population:** the bound device is in the **WL2864C/WL2868C family**, but
   the shared module name and dual ID table do not reveal the fitted revision. RT5133 and both RT6160 clients
   are unbound; their functions are known from datasheets, but **physical population remains UNKNOWN**.
3. **Fingerprint modality/location:** Microarray/MaDev, SPI and TrustKernel/TkCore integration remain PROVEN.
   A generic display-pattern hook suggests optical operation while one weak review says side-mounted.
   **Die, location, modality and geometry remain TEARDOWN_REQUIRED.**

The strongest positive additions are the direct MTK CameraProvider probe table, the complete bound/unbound bus
parse, exact SC8571 product data, runtime eSIM/cooling/touch corroboration, and a datasheet match for LN2403.

## Constraints and provenance

* No phone was connected during this pass (`adb devices` was empty). No new live command was run.
* All runtime evidence is a deeper read of the frozen capture:
  `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/`.
* That capture used a **LieppOS GSI over stock vendor/kernel**, not the stock Ulefone system. Kernel, driver,
  device-tree, bus and vendor-HAL facts remain valid; Android framework/app behaviour from the capture is
  labelled GSI and is not promoted to `STOCK USES`.
* Stock partitions, DT/DTBO, modules, HALs, firmware, APK native libraries and frozen runtime dumps were read
  offline only. No flash, write, GPIO toggle, register write, bind/unbind, calibration or RF/NV operation was
  performed.
* Internet research used primary vendor/OEM material where available and lower-grade aggregators only with
  explicit quality labels. An OpenAI search quota returned HTTP 429 during part of the work; Exa supplied the
  remaining searches. Misses are recorded as misses, never as proof of absence.

## Audit accounting

| Metric | Result |
|---|---:|
| Original U-items revisited | **24 / 24** |
| Finding documents retained | **26** (U1-U24 + provenance correction + FM/headset discovery) |
| Findings receiving an explicit second-pass update | **16** |
| Internet queries logged | **33** (`Q1-Q33`, no gaps) |
| Local structural queries logged | **28** (`L1-L28`, no gaps) |
| Local evidence sources | **28** (`VL1-VL28`) |
| Internet/datasheet sources | **35** (`VI1-VI35`) |
| New second-pass evidence files | **2** |
| Authoritative final reports reconciled | **5 / 5** |

Counts are intentionally not presented as one exclusive "resolved versus unresolved" number: U1, U2, U9,
U10, U12, U16 and U24 each have a resolved hardware identity/topology plus a named residual question.
`../../final/UNKNOWN-HARDWARE.md` is the authoritative status ledger.

## Second-pass result by U-item

| ID | Second-pass action/result | Reconciled status |
|---|---|---|
| U1 | Exact `MT512GBCAV8U31` search repeated; no public Micron orderable SKU. Generic preloader LP4/LP5 code is platform capability, not grade proof. | Micron name + 16 GiB PROVEN; LPDDR5 vs LPDDR5X, rate, channels/ranks UNKNOWN |
| U2 | Exact package search repeated; preloader contains generic UFS 3.0/3.1 paths but no selected generation/gear/lane state. | 512 GB/package/health PROVEN; revision/gear/lanes UNKNOWN |
| U3 | MTK CameraProvider runtime enumeration directly reports `IMX989 / S5KJN1 / S5KJN1MAIN2 / OV64B`. Ulefone and exact-device review still specify GN1 for retail model. | this handset's IMX989 runtime match STRONGLY_SUPPORTED; multi-source slot PROVEN |
| U4 | Re-traced DW9781C rails, bus mates and OIS pin groups; all cameras publish OIS `[0]` (OFF only). Sensor0/sensor4 evidence conflicts for ownership. | controller/path + HAL-disabled state PROVEN; lens mapping **UNKNOWN / TEARDOWN_REQUIRED** |
| U5 | Mini640/AC020 market data again matches 640x512, 12 um, <=40 mK, radiometric 25 Hz. No orderable lens/shutter SKU found. | STRONGLY_SUPPORTED; exact module/lens/shutter TEARDOWN_REQUIRED |
| U6 | External BOMs identify FM78100 as a real IR body-temperature part on other devices, supporting the inherited-node-name explanation. Local driver still only sequences InfiRay rails/ID. | thermal-module power/ID role on this board PROVEN |
| U7 | No new contradictory evidence; ConnFem still resolves `nofem + nofem`. | no external Wi-Fi/BT FEM PROVEN |
| U8 | Wider FCC/internal-photo/teardown search returned no usable exhibit. | cellular antenna/filter inventory TEARDOWN_REQUIRED |
| U9 | Charger DT exposes 8.90 V pack CV (4.45 V/cell), JEITA thresholds and dual-gauge topology; no cell marking or metered capacity. | 2S topology PROVEN; cell P/N and 8594-vs-10600 mAh gap unresolved |
| U10 | Exact SC8571 page corrects the part to **2-cell, 8 A, 98.65% peak, CSP80**. Earlier category-page 80 W/10 A attribution withdrawn. Board config remains 2 pumps, up to 6.55 A each, 6 A/20 V system ceiling. | PD/PPS/direct-charge configuration STRONGLY_SUPPORTED; delivered 120 W unmeasured |
| U11 | MT6375 OTG registers confirmed as wired USB reverse-mode evidence, not wireless evidence. | wireless/reverse-wireless PROVEN absent; wired reverse retained |
| U12 | MT6369 VIBR-LDO topology unchanged; no richer haptic IC surfaced. | ERM/DC-LDO topology STRONGLY_SUPPORTED; motor P/N TEARDOWN_REQUIRED |
| U13 | Correct `readlink -f` interpretation confirms Ilitek/ChipOne clients are unbound; active `fts_ts` and `hyn_ts` are input-registered. FocalTech logs `TP Ready, Read ID=0x56`. | active touch pair PROVEN; alternate physical absence STRONGLY_SUPPORTED |
| U14 | CO5300 binds on SPI0 at 60 MHz; Hynitron 340x340 single-touch; OEM/review confirm 1.04-inch 340x340 600-nit rear AMOLED. Only one HWC display appears in capture. | hardware PROVEN; genuine stock UI behaviour unmeasured |
| U15 | `/dev/madev0` + `/dev/tkcore_fp` reinforce Microarray/TEE stack. Family research finds MaDev/MAFP naming but no phone die. Location/modality evidence conflicts. | vendor/bus/TEE PROVEN; die/location/modality/geometry TEARDOWN_REQUIRED |
| U16 | Bound camera PMIC supports WL2864C and WL2868C IDs; exact revision not emitted. RT5133 and both RT6160 clients are unbound. DT-visible WL-family rail values decoded. | functions/family resolved; exact WL revision, unbound population and remaining runtime rails UNKNOWN |
| U17 | ST21NFC family/fw7/routing evidence unchanged; no exact package/HwVersion read. | ST21NFCD class STRONGLY_SUPPORTED; exact orderable part TEARDOWN_REQUIRED |
| U18 | No stock-powered Bluetooth capture; GSI LE-Audio properties remain non-evidence. | Bluetooth 5.4 OEM claim LIKELY; LE Audio/Auracast UNKNOWN |
| U19 | L5 property and 0x6637-specific calibration retained; no open-sky reception measurement. | dual-band multi-constellation config STRONGLY_SUPPORTED; reception unmeasured |
| U20 | Camera blocks re-parsed. Stream arrays remain direct HAL facts; secondary-camera physical-size/pixel-array metadata is internally inconsistent and is now flagged as firmware metadata error. | advertised stream configurations PROVEN; secondary die geometry not proven |
| U21 | Thermal HAL exposes only GPU/charger/flashlight/backlight/Wi-Fi throttling; DT/dmesg contains no fan, TEC, pump, tachometer or BLDC object. | no active cooling PROVEN; passive material stack TEARDOWN_REQUIRED |
| U22 | Wider search found no independent test report/certificate number. | OEM ruggedness claim STRONGLY_SUPPORTED as a claim only |
| U23 | Runtime telephony dump adds `Euicc enabled=false` and `isEmbedded=0 isRemovableEmbedded=0`. | eSIM/eUICC PROVEN absent |
| U24 | LN2403 datasheet found; wiring matches a Natlinear 2 A PWM/PFM buck constant-current LED driver. AW36515, 2 x AW36518 and AW2013 functions mapped. IR DT path plus MTK legacy HAL/LIRC/rc-core/PWM ownership are now closed statically. | bound support tier and ConsumerIR software ABI PROVEN; LN2403 LIKELY; IR emitter/function + passives unresolved |

## Decisive second-pass local evidence

### 1. Correct population parse

`buses.txt` uses `readlink -f <device>/driver`. If the final `driver` component does not exist,
`readlink -f` returns the canonical path ending in `/driver`; that is **not a binding**. If the link exists,
it resolves to `/sys/bus/<bus>/drivers/<name>`.

Re-parsing all 53 blocks produced:

* **28 bound/device-driven clients** in the captured subset;
* **5 unbound clients:** Ilitek 0-0041, ChipOne-TDDI 0-0048, RT5133 5-0018, RT6160 5-0075 and RT6160 6-0075;
* **5 reserved `dummy` clients:** 5-001a, 5-003f, 5-004a, 5-004e and 5-0064.

This confirms the pass-one Ilitek/ChipOne result, but prevents unbound RT5133/RT6160 declarations from being
mistaken for populated hardware. Unbound is **not** proof of physical absence; those parts remain UNKNOWN.
Full table: `../evidence/live-runtime-secondpass.md` (L21).

### 2. Runtime camera identity and metadata quality

MTK CameraProvider reports:

```text
[00] BACK  SENSOR_DRVNAME_IMX989_MIPI_RAW
[01] FRONT SENSOR_DRVNAME_S5KJN1_MIPI_RAW
[02] BACK  SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW
[03] BACK  SENSOR_DRVNAME_OV64B_MIPI_RAW
```

| HAL id | Runtime name | `pixelArraySize` | `physicalSize` mm | OIS modes |
|---:|---|---:|---:|---:|
| 0 | IMX989 | 4096x3072 | 13.107 x 9.830 | `[0]` |
| 1 | S5KJN1 | 8160x6144 | 4.640 x 3.490 | `[0]` |
| 2 | S5KJN1MAIN2 | 8160x6144 | **13.107 x 9.830** | `[0]` |
| 3 | OV64B | 4624x3472 | 6.500 x 4.890 | `[0]` |

Camera 2 reuses the main camera's 1-inch-class physical geometry, while camera 1 advertises a 50 MP array
against a JN1-sized die. Aperture/focal-length tags are absent. Therefore:

* runtime DRVNAME is strong device-identity evidence;
* stream arrays are valid HAL-advertised capabilities;
* copied secondary physical-size/pitch fields are **not** valid silicon proof.

### 3. Power and lighting corrections

| Part/node | Second-pass reading |
|---|---|
| SC8571 x2 | bound master/slave; exact product = 2-cell, 8 A, 98.65% peak, CSP80; board caps each at 6.55 A |
| SC8510 | bound bidirectional switched-cap path; explicit forward/reverse voltage and OCP ranges; wired reverse power |
| WL286x @ 11-0029 | bound `wl2864c` driver from `custom_ldo_wl2868`; DT carries both 0x28 and 0x82 IDs; family proven, exact revision UNKNOWN |
| RT5133 @ 5-0018 | 8-LDO camera PMIC by datasheet; client unbound, no module; physical population UNKNOWN |
| RT6160 @ 5/6-0075 | buck-boost capability known; both clients unbound; physical population UNKNOWN |
| OCP2131 @ 6-003e | bound `I2C_LCD_BIAS` / `mediatek_drm_gateic`; panel positive/negative bias path |
| AW36515 | bound dual independent 2 A flash/torch/IR driver |
| AW36518 x2 | two bound 1.5 A flash/torch/IR-family drivers |
| AW2013 | bound RGB indicator/pattern driver |
| LN2403 path | node and GPIO/PWM wiring PROVEN; Natlinear 2 A buck LED-driver identity LIKELY |
| `/irtx-pwm` | enabled PWM0 path on `mt6369_vio28`; AOSP AIDL wrapper selects MTK `consumerir.common.so` -> `/dev/lirc0` -> rc-core/`mtk_irtx_pwm.ko`; emitter/function unverified |

### 4. Other runtime corroboration

* Touch: FocalTech `fts_ts` on SPI3 is input-active and logs ID `0x56`; Hynitron `hyn_ts` is bound at 0-0015
  with native 340x340 axes. Ilitek/ChipOne alternatives are unbound.
* Audio capture: DT plus the HAL MicInfo selector prove two built-in AMICs: bottom/main on AIN0/ADC_L/UL1_CH1 and back/sub on AIN2/ADC_R/UL1_CH2. DMIC/ThreeMic routes are unused BSP capability; runtime acoustics remain unverified.
* Fingerprint: `/dev/madev0` (`mafinger_device`) and `/dev/tkcore_fp` (`tkcore_client_device`).
* Telephony: `Euicc enabled=false`; active subscription `isEmbedded=0 isRemovableEmbedded=0`.
* Cooling devices exposed to Android: `devfreq-13000000.mali`, `charger-cooler`, `flashlight_cooler`,
  `lcd-backlight`, `wifi-cooler`; no active cooling object.
* Physical sensor families exposed by HAL: ICM-4x607 accel/gyro, MMC5603 magnetometer, STK3A5x ALS/PS and
  SPL07 barometer; the remaining HAL entries are MTK fused/virtual sensors.

Raw extracts: `../evidence/live-devicetree-secondpass.txt` and `../evidence/live-runtime-secondpass.md`.

## Internet/datasheet outcomes that changed a conclusion

| Source | Quality/scope | Effect |
|---|---|---|
| SouthChip SC8571 exact page + exact-part datasheet listing (VI35) | A/B, exact chip | corrects SC8571 from misattributed category values to 2-cell/8 A/98.65%/CSP80 |
| Natlinear LN2403 datasheet listing (VI29) | B, exact chip | raises LN2403 identity from UNKNOWN to LIKELY when combined with exact DT PWM/power wiring |
| WL2864C/WL2868C family pages (VI14, VI28) | A/B, exact family | identifies camera-LDO function/VDDOIS but does not choose the local die revision |
| Awinic AW36515/AW36518 material (VI32) | A, exact chip | attributes all three bound flash/IR drivers and their current class |
| DeviceSpecifications exact-device review + Ulefone spec (VI25, VI27) | B/A, exact device | independently supports the GN1 retail population, 2-cell battery, rear-display geometry and published charging claims |
| FM78100 wearable BOMs (VI30) | C, family context | explains why an alternate ODM project named an IR-temperature node `fm78100`; does not override this board's bound driver role |
| Microarray MaDev/MAFP family evidence (VI31) | C, family context | corroborates vendor naming only; no die/modality closure |

Unproductive searches are also retained: exact Micron package decode, regulatory internals/teardown,
Microarray phone die, exact thermal lens/shutter SKU, and an explicit primary-source fingerprint location.

## Remaining open evidence requests

| Priority | Unknown | Safest closing evidence |
|---:|---|---|
| 1 | genuine Ulefone stock framework behaviour | fresh read-only stock capture: properties, packages, `dumpsys`, camera profiles, display policy, BT state |
| 2 | Bluetooth LE Audio/Auracast | stock boot, enable BT, read HCI `LE Read Local Supported Features` and `Read Local Supported Commands`; no writes |
| 3 | UFS version/gear/lanes + DRAM grade/rate/topology | read-only vendor sysfs/debugfs nodes on rooted stock; exact Micron datasheet if later published |
| 4 | runtime regulator state + WL2864C/WL2868C revision | read `/sys/class/regulator/*/{name,microvolts}` and any driver's read-only chip-ID/debug node; do not probe registers blindly |
| 5 | battery 8594-vs-10600 mAh discrepancy | SH366003 read-only design-capacity output or metered full cycle with thermal monitoring |
| 6 | actual 120 W delivery/derating | certified 20 V/6 A PPS source plus inline meter and temperature logging |
| 7 | GNSS L5 reception | open-sky `GnssStatus`/raw measurement log on stock |
| 8 | OIS lens mapping | module EEPROM/BOM or controlled optical actuator correlation; no blind I2C writes |
| 9 | fingerprint die/location/modality | observe stock enrolment for location/illumination; package marking requires teardown |
| 10 | antennas, filters, cooling materials, passives, IR emitter | FCC internal photos, repair documentation or teardown with layer/marking photography |

Before any experiment, preserve stock images, modem NV/calibration, camera EEPROMs, fingerprint/TEE data and
`/mnt/vendor/nvcfg/infiray`. Opening the chassis invalidates confidence in IP68/IP69K sealing.

## Reconciliation of authoritative reports

All five authoritative reports were updated in place and checked for stale cross-file claims:

1. `../../final/FINAL-REPORT.md`
   * adds the second-pass correction ledger;
   * replaces SC8571 80 W/10 A wording;
   * removes fitted RT5133/RT6160 and exact WL2868C claims;
   * downgrades OIS lens ownership and fingerprint modality/location.
2. `../../final/MASTER-HARDWARE-INVENTORY.md`
   * records CameraProvider runtime DRVNAMEs and metadata defects;
   * separates bound power devices from unbound alternatives;
   * maps the complete lighting tier and updates touch/eSIM/fingerprint evidence.
3. `../../final/HARDWARE-CAPABILITY-MATRIX.md`
   * restores strict CHIP / BOARD / STOCK separation for OIS, rear display, ConsumerIR and fingerprint;
   * records exact SC8571 capability and WL/RT population gaps.
4. `../../final/UNKNOWN-HARDWARE.md`
   * changes U4 to UNKNOWN/TEARDOWN_REQUIRED;
   * changes U15 modality/location to TEARDOWN_REQUIRED;
   * expands U16 residuals and records U24's LN2403 improvement.
5. `../../final/UNUSED-HIDDEN-CAPABILITIES.md`
   * keeps DW9781C as fitted-but-HAL-disabled without assigning a lens;
   * updates direct-charge and lighting limits;
   * explains that the IR PWM path has only an example HAL and that passive heat-spreader composition remains open.

Automated checks found no malformed Markdown table rows, all 19 finding files named by
`UNKNOWN-HARDWARE.md` exist, all cited `VL`/`VI` identifiers resolve, and the five reports agree on these
critical facts: SC8571 2-cell/8 A, OIS lens ownership UNKNOWN, WL exact revision UNKNOWN, RT5133/RT6160
population UNKNOWN, LN2403 LIKELY, fingerprint modality/location TEARDOWN_REQUIRED.

## Deliverables

* `../evidence/live-devicetree-secondpass.txt` - raw/decoded DT node evidence.
* `../evidence/live-runtime-secondpass.md` - corrected bound/unbound parse, camera runtime table, touch,
  fingerprint, cooling, eSIM and physical-sensor evidence.
* `../search/queries.md` - Q1-Q33 and L1-L28 with outcomes.
* `../search/sources.md` - VL1-VL28 and VI1-VI35 with quality/scope and confidence changes.
* `../findings/` - 26 finding documents; 16 carry explicit second-pass updates.
* `../../final/{FINAL-REPORT,MASTER-HARDWARE-INVENTORY,HARDWARE-CAPABILITY-MATRIX,UNKNOWN-HARDWARE,UNUSED-HIDDEN-CAPABILITIES}.md`
  - reconciled authoritative reports.

**Bottom line:** the second pass increased useful certainty by identifying LN2403, correcting SC8571 and
strengthening direct runtime identities; just as importantly, it removed unsupported certainty from OIS
ownership, fingerprint modality and unbound power-IC population. The remaining UNKNOWN and
TEARDOWN_REQUIRED entries are evidence boundaries, not omissions.
