# U19 - actual GNSS constellations and L5 support

**Current claim:** "L5 property and service fields; no fix" - real constellation and band support unknown.

**Previous confidence:** POSSIBLE.

**New evidence - the vendor GNSS configuration file resolves this in detail**

`vendor/etc/MNL_Config.xml` (MediaTek MNL, version 21111601.6.00.00):

| Feature | Setting | Meaning |
|---|---|---|
| `GnssMode` | **10** | format string maps 10 to **`GP+GL+GA+BD+NI`** = GPS + GLONASS + Galileo + BeiDou + **NavIC/IRNSS** |
| `L1Only` | **0** | multi-band operation enabled (not restricted to L1) |
| `L5Test` | **1** | search and use **GPS L5** satellites regardless of their health flag |
| `DisableSignal` | **0** | bitmask with nothing disabled: **B1C, GPS L1C, QZSS L1C, E5B and B2B are all enabled** |
| `DCB` | per-chip tables | **L5 differential code bias calibrated for chip `6637`**: `L5_DCB_GPS, L5_DCB_QZSS, L5_DCB_CNSS, L5_DCB_GALILEO = -8.16, -8.34, -10.82, -9.17`; an alternate set exists for chip `6686` |
| `CAIC` | L1 = 1 560 000 000 Hz, L5 = 1 170 000 000 Hz | explicit L1 and **L5 band centre frequencies** |
| `GNSSPower` | 51.9 / **100.2** / 58.5 / 106.7 mW | separate power model for **single-band vs multi-band tracking and acquisition** |
| `OSNMA` | **1** | **Galileo OSNMA** navigation-message authentication enabled |
| `GGTO` | GLONASS/BEIDOU/GALILEO/**NAVIC** time offsets | all four inter-system time offsets calibrated |
| `GLP`, `Bluesky`, `SwitchTIA`, `CoTMS`, `PSO` | enabled | low-power, position-aiding (driving mode), TIA switching and co-existence features on |

Supporting evidence: the calibrated chip ID `6637` matches `vendor.connsys.gps.adie.chipid = 0x6637`; `vendor.debug.gps.support.l5 = 1`; services `vendor.gnss-default` and `agpsd` were running; QZSS appears in the DCB and DisableSignal tables even though it is not in the `GnssMode` mnemonic (it is handled as a GPS augmentation).

**Contradicting evidence:** none. Ulefone's public page lists "GPS / GLONASS / ..." without detail, which is consistent but less specific.

**Internet sources:** VI4 (OEM navigation list).

**Local evidence:** VL19.

**Read-only live evidence:** GNSS properties and running services from the frozen capture; **no satellite fix was recorded**.

**Final conclusion**
The GNSS engine in the **MT6637** is configured for **five constellations - GPS, GLONASS, Galileo, BeiDou and NavIC - plus QZSS augmentation**, in **dual-band L1 + L5/E5a/B2a** operation, with **B1C, GPS L1C, QZSS L1C, E5B and B2B all enabled**, per-chip **L5 differential-code-bias calibration**, a distinct multi-band power model, and **Galileo OSNMA authentication turned on**. This is a fully provisioned dual-band multi-constellation receiver, not a marketing claim.

**Final confidence:** **STRONGLY_SUPPORTED** at the board-and-vendor-configuration layer (the strongest level obtainable without a sky view). Actual satellite reception, per-band C/N0 and time-to-first-fix = **UNKNOWN**.

**Remaining uncertainty:** an **open-sky test** with `GnssStatus`/`GnssMeasurement` logging (or the bundled `YGPS` engineering app, which is present in the stock `system_ext/app`) would demonstrate real L5/E5a/B2a tracking. This is a measurement, not a configuration question.

**Impact on final inventory:** YES - the GNSS row moves from "L5 flag set, no fix" to an enumerated, calibrated multi-band multi-constellation configuration; the hidden-capability entry is upgraded accordingly.

**Answers:** (1) 5 constellations + QZSS, L1+L5, OSNMA, calibrated for 0x6637; (2) an actual open-sky fix log; (3) yes; (4) yes - `GnssStatus` logging is read-only; (5) partially; (6) no; (7) MT6637 dual-band GNSS, GPS+GLONASS+Galileo+BeiDou+NavIC+QZSS; (8) STRONGLY_SUPPORTED; (9) yes; (10) yes; (11) yes.
