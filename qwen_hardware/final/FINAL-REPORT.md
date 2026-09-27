# Final report - GQ5012BF1 hardware capability audit

**Revised 2026-09-08** after two UNKNOWN-HARDWARE verification passes (`../verification/`). The second pass re-parsed population evidence, re-checked every remaining unknown, and reconciled all five authoritative reports.

## Executive conclusion

The Ulefone Armor 29 Pro Thermal is an **MT6878V/TZA (Dimensity 7400)** rugged phone with four Android cameras, a separate **InfiRay 640x512 radiometric thermal module** on a private USB-UVC path, a **1.04-inch Chipone CO5300 rear AMOLED**, an **MT6637** connectivity die with **no external RF front-end module**, an **ST21NFC controller without an embedded secure element**, a **2S 7.74 V battery charged by two 2-cell/8 A SC8571 charge pumps over PD/PPS at a board-configured ceiling of 120 W**, and an entirely **passive** cooling system. The board contains meaningfully more capability than a generic Android build exposes - but it also contains **less** than the previous edition of this audit claimed.

## The four most important corrections

1. **The "live-stock" capture was not stock.** It was taken on a **LieppOS GSI** over stock vendor/kernel (`ro.lineage.display.version = LieppOS-23-...-GSI`, KernelSU-rooted). Every hardware fact derived from the kernel, drivers, device tree, buses and vendor partition stands. Every *framework* observation - the 500-nit brightness policy, "stock lists 4K30", the enabled LE-Audio properties, the apparent absence of a thermal application - describes the GSI, not Ulefone's software. Genuine stock runtime behaviour has still never been measured.
2. **Wireless charging does not exist on this device.** The previous claim of "50 W wireless / 30 W reverse" is disproven by four independent negatives (no device-tree node, no `wireless` power supply, no receiver IC, no OEM claim). The real capability is **10 W wired reverse output** through an SC8510 bidirectional charge pump. The misleading `mt5786group` sysfs paths come from `init.yft.rc`, a **platform-wide ODM file that enumerates other products' options** - the single most dangerous evidence trap in this codebase.
3. **The IMX989-versus-GN1 contradiction is a multi-source-slot issue, not a reason to merge the names.** The main-camera DT slot declares `imx989`, `s5kgm2sp`, `imx989cts` and `s5kgn1sp` candidates and probes by sensor ID. On this handset, MTK CameraProvider enumerated **`SENSOR_DRVNAME_IMX989_MIPI_RAW`**; camera 0 also reports a 13.107 x 9.830 mm, 1-inch-class physical array. Ulefone and an independent exact-device review instead publish **Samsung S5KGN1, 1/1.31 inch, 1.2 um** for the model. The defensible reading is lot/SKU variation: this unit probed IMX989, while retail literature describes a GN1 population.
4. **There is no external Wi-Fi/BT front-end module.** ConnFem's HWID resolves to `nofem + nofem`; the driver logged "FEM is not available" and Bluetooth logged `BTvid/pid == 0`. The seven alternative FEM pairings in the device tree belong to other boards. There is no hidden RF capability to unlock, and 6 GHz range is bounded by the MT6637's own PA.

## Second-pass reconciliation

* Re-parsing all 53 `buses.txt` blocks with correct `readlink -f` semantics confirmed the active touch/camera/power devices and separated **unbound DT clients** from bound hardware. Ilitek and ChipOne-TDDI remain unbound alternatives; RT5133 and both RT6160 nodes are now explicitly **population UNKNOWN**, not fitted parts.
* MTK CameraProvider's runtime table directly names this handset's four probes: **IMX989 / S5KJN1 / S5KJN1MAIN2 / OV64B**. It also exposes internally inconsistent secondary-camera geometry, so those copied metadata fields are no longer treated as die proof.
* OIS presence remains proven, but the former "probably main lens" assignment is withdrawn: sensor0 has `oisvdd`, sensor4 has `oisen`, and bus placement cannot choose the lens. Exact lens ownership is **TEARDOWN_REQUIRED**.
* Exact-part research corrected SC8571 to **2-cell / 8 A / 98.65% peak / CSP80**, identified LN2403 as a **likely Natlinear 2 A buck LED driver**, and showed that the WL camera-PMIC driver supports both WL2864C and WL2868C without revealing the fitted revision.

## Newly proven hardware

* **Memory and storage are one Micron uMCP marked `MT512GBCAV8U31`** - 512 GB UFS plus 16 GiB LPDDR5-class DRAM - identified by the bootloader itself. **UFS health is directly readable and excellent**: PreEOL Normal, life-time estimates A and B both in the 0-10 % band.
* **Battery topology is 2S**: 7.74 V nominal, 8.90 V pack CV = 4.45 V per cell, dual gauges (MT6375 internal + SH366003 pack-side), four board NTC thermistors, 26 cycles and SoH 94 % at capture. Ulefone's "21200 mAh" headline is the 3.87 V-equivalent of a 10600 mAh / 7.74 V pack.
* **Charging is PD 3.0 with PPS only** - **UFCS is positively absent** - configured for 6 A at 20 V (120 W), matching Ulefone's published "120W (20V/6A)". Two bound SC8571 devices form the direct-charge pair; the exact-product specification is 2-cell, 8 A, 98.65% peak efficiency, while the board caps each instance at 6.55 A.
* **The thermal core is an InfiRay/InfiSense Mini640-class module with an AC020 ASIC** (640x512, 12 um, NETD < 40 mK, radiometric 25 Hz), branded "ThermoVue T2". The node named `fm78100` is **not** a thermopile - it is the module's power/ID endpoint.
* **The rear display is a 1.04-inch 340x340 AMOLED on a Chipone CO5300** - not the 3.97-inch panel previously recorded.
* **A whole PMIC tier was missing from the inventory**: MT6363 main PMIC, MT6369 sub-PMIC (audio codec, headset accdet, haptic LDO), MT6319 external buck, MT6685 clock/RTC and NTC front end. RT5133 is a **camera** LDO PMIC by datasheet, not a system PMIC, but its DT client is unbound and no module ships; physical population is therefore **UNKNOWN**. The bound camera-LDO device is in the WL2864C/WL2868C family, with exact revision also UNKNOWN because the shared driver/DT supports both IDs.
* **Two built-in analog microphones are selected and routed**: bottom/main on MT6369 AIN0/ADC_L/UL1_CH1 and back/sub on AIN2/ADC_R/UL1_CH2. Generic DMIC/ThreeMic paths are unused platform capability; the headset mic is separate.
* **An FM radio receiver and a 3.5 mm headset jack**, neither previously documented, both fitted and both supported by stock software.
* **GNSS is genuinely multi-band and multi-constellation**: GPS, GLONASS, Galileo, BeiDou, NavIC and QZSS on L1 plus L5/E5a/B2a, with L5 differential-code-bias calibration keyed to the fitted 0x6637 die and Galileo OSNMA enabled.
* **All four cameras' stream configurations are now fully decoded** - 211 to 215 entries each across six formats.

## Newly disproven assumptions

| Claim in the previous edition | Verdict |
|---|---|
| 50 W wireless charging, 30 W reverse wireless | **disproven** - no wireless hardware at all; 10 W **wired** reverse |
| UFCS fast-charge support | **disproven** - `SDP DCP CDP PD PD_PPS` only |
| Alternate RF FEMs selectable by HWID | **disproven** - board is `nofem + nofem` |
| Rich haptics might be unlockable | **disproven** - ERM on a DC LDO, no haptic IC |
| Possible active fan/TEC cooling | **disproven in software** - all cooling devices are electrical throttling; vapour-chamber/graphite material remains teardown-only |
| Rear display is 3.97 inch | **corrected** - 1.04 inch, 340x340 |
| Water resistance 2 m / 30 min | **corrected** - 1.5 m / 30 min |
| RT5133 is "the PMIC" | **corrected** - it is an 8-channel camera LDO PMIC |
| Battery marketing is 2 x 5300 mAh | **corrected** - 2S pack, 10600 mAh at 7.74 V |
| BT LE Audio suggested by properties | **withdrawn** - those properties came from a GSI |

## What remains genuinely open

The highest-value unknowns are now few and specific: the **OIS-to-lens mapping** (the DW9781C is bound, but sensor0 carries `oisvdd` while sensor4 carries `oisen`), the **cellular antenna and filter chain** (architecturally invisible to software), the **Microarray fingerprint die/location/modality**, **Bluetooth LE Audio capability**, the **8594 mAh gauge value versus the 10600 mAh rating**, **UFS gear and DRAM timings**, the **WL2864C-vs-WL2868C revision and physical population of unbound RT5133/RT6160 alternatives**, the **cooling material stack**, and - most importantly - **what the real stock framework does at runtime**, which has never been captured.

## Practical value for a custom ROM

The defensible opportunities are the fitted-but-HAL-disabled DW9781C path (lens ownership still unknown), the camera high-rate and full-resolution modes, the spare flash/IR channels and AW2013 pattern engine, sensor rates above the HAL caps, dual-band GNSS, and the direct-charge stack. Two features are at risk of being *lost* rather than gained: the **FM radio** and the **private rear-display path**, both of which exist only in vendor code. Preserve stock images, modem NV and calibration, camera EEPROMs, fingerprint/TEE data, and the **InfiRay thermal calibration in `/mnt/vendor/nvcfg/infiray`** before any experiment.

USB remains a hard limit: the product specification says USB 2.0, and software cannot create SuperSpeed lanes or DisplayPort wiring. Nor can software add wireless charging, an eSIM, an embedded secure element, an LRA, or an external RF front end - all of which are now positively established as absent.

## Deliverables

* `MASTER-HARDWARE-INVENTORY.md` - consolidated bill of materials with per-item confidence.
* `HARDWARE-CAPABILITY-MATRIX.md` - the chip/board/stock three-layer model, with GSI-versus-stock provenance marked.
* `UNUSED-HIDDEN-CAPABILITIES.md` - real headroom, plus an explicit list of removed/disproven items.
* `UNKNOWN-HARDWARE.md` - resolved and still-open questions with the exact physical evidence each would need.
* `../verification/` - both verification passes: 26 per-topic findings, second-pass DT/runtime evidence extracts, and the complete query/source log.
* `../subsystems/`, `../findings/`, `../evidence/`, `../search/` - the original working material.

**Bottom line:** this is a feature-rich, heavily vendor-gated board whose real capabilities are now largely pinned down with primary evidence. The most valuable outcome of this pass is not the list of things the phone can do - it is the list of things the previous audit believed it could do, and it cannot.
