# Status board - GQ5012BF1 hardware audit

Two passes are complete.

* **Pass 1 (inventory)** - 24 subsystem reports (all 19 required categories plus aliases and cross-reference extras) plus five final reports. Working material now lives in `../subsystems/`, `../findings/`, `../evidence/` and `../search/`, each carrying a "superseded in part" banner.
* **Pass 2 (verification, 2026-09-08)** - `../verification/`: all 24 entries of `UNKNOWN-HARDWARE.md` investigated, 26 finding documents written (U1-U24 plus the snapshot-provenance correction and the FM-radio/headset-jack discovery), and the five final reports rewritten. See `../verification/final/VERIFICATION-REPORT.md`.

No ADB device was available in either pass. All live evidence is the frozen 2026-08-31 capture, which - as pass 2 established - was taken under a **LieppOS GSI** over stock vendor/kernel.

## Verification outcome by unknown

| ID | Topic | Status after pass 2 |
|---|---|---|
| U1 | DRAM | RESOLVED (Micron uMCP `MT512GBCAV8U31`, 16 GiB) / timings UNKNOWN |
| U2 | UFS | RESOLVED (512 GB, health PROVEN) / gear UNKNOWN |
| U3 | Main camera die | RESOLVED - dual-source slot; this unit IMX989 |
| U4 | OIS/VCM/lens mapping | LIKELY (main lens group) |
| U5 | Thermal detector | STRONGLY_SUPPORTED - InfiRay Mini640-class + AC020 |
| U6 | FM78100 role | PROVEN - thermal-module power/ID endpoint |
| U7 | ConnFem selection | PROVEN - `nofem + nofem` |
| U8 | Antennas / MIMO / filters | TEARDOWN_REQUIRED (cellular) / PROVEN (no Wi-Fi-BT FEM) |
| U9 | Battery pack | RESOLVED (2S, 7.74 V) / capacity gap UNKNOWN |
| U10 | Charging profiles | RESOLVED - PD+PPS, 120 W configured, no UFCS |
| U11 | Wireless charging | PROVEN ABSENT |
| U12 | Haptics | RESOLVED - ERM on MT6369 VIBR, no haptic IC |
| U13 | Ilitek population | STRONGLY_SUPPORTED - not populated |
| U14 | Rear display | PROVEN - Chipone CO5300, 1.04" 340x340 |
| U15 | Fingerprint die | TEARDOWN_REQUIRED (vendor PROVEN) |
| U16 | Power IC limits | RESOLVED (identities) / rail values UNKNOWN |
| U17 | ST21NFC variant | STRONGLY_SUPPORTED - controller-only, no eSE |
| U18 | Bluetooth LE Audio | UNKNOWN - needs a stock capture |
| U19 | GNSS constellations | STRONGLY_SUPPORTED - 5 constellations + QZSS, L1+L5 |
| U20 | Camera stream configs | PROVEN - fully decoded |
| U21 | Cooling stack | TEARDOWN_REQUIRED (no active cooling PROVEN) |
| U22 | IP/MIL certification | STRONGLY_SUPPORTED as a claim |
| U23 | eSIM / eUICC | PROVEN ABSENT |
| U24 | Hidden support ICs | RESOLVED (13 parts added) / passives TEARDOWN_REQUIRED |

## Deliverables

* 5 final reports (`../final/`), all rewritten in pass 2
* 26 verification findings (`../verification/findings/`) - U1-U24 plus `00-snapshot-provenance-correction.md` and `fm-radio-and-headset-jack.md`
* 2 primary-evidence extracts (`../verification/evidence/`)
* verification query and source logs (`../verification/search/`)
* `../verification/final/VERIFICATION-REPORT.md`
* 24 subsystem reports and the pass-1 working logs, all banner-marked as superseded in part
