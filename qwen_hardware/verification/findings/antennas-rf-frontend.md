# U8 - antenna count, MIMO and RF filter chain

**Current claim:** "no software inventory".

**Previous confidence:** UNKNOWN.

**New evidence**
* **Wi-Fi/BT front end is now settled** (see `connfem-selected-fem.md`): no external ePA/eLNA. The Wi-Fi/BT/GNSS radio paths terminate at the MT6637 ADIE, whose Wi-Fi 6E coverage (2.4/5/6 GHz) is confirmed by the OEM specification and by `vendor.connsys.wifi.adie.chipid = 0x6637`.
* **Cellular front end remains software-invisible by construction.** MediaTek routes cellular PAs, LNAs, switches, duplexers and antenna tuners over **MIPI RFFE** under modem firmware control; they are not enumerated as Linux devices and appear in neither the device tree nor sysfs. Nothing in the captured data can therefore inventory them.
* Band coverage from the OEM: 5G n1/2/3/5/7/8/20/25/28/38/40/41/66/71/77/78/79; LTE FDD B1/2/3/4/5/7/8/12/13/17/18/19/20/25/26/28A/B/32/66/71. That breadth implies multiple PA modules and a multi-throw antenna switch, but implies nothing verifiable about counts.
* A `POWER_AMPLIFIER` thermal zone exists with throttling thresholds at 68/90/100/110 degC, confirming at least one instrumented cellular PA with a thermal sensor.
* `/fmradio/fm_lna_gpio = <ctrl 72 0>` shows a discrete FM LNA control line, and `accdet/gpio-accdet-fm-switch = <ctrl 195 0>` shows the headset cable is switched in as the FM antenna.

**Contradicting evidence:** none.

**Internet sources:** VI1, VI4 (band lists, Wi-Fi 6E, BT 5.4). VI10 search for FCC internal photos (Q10) returned **nothing** - no FCC internal photo set or teardown for GQ5012BF1 could be located.

**Local evidence:** VL4, VL5; thermal zone list in `thermal-power.txt`.

**Read-only live evidence:** frozen capture only.

**Final conclusion**
* **Wi-Fi/BT/GNSS RF chain: no external FEM - PROVEN.**
* **Cellular antenna count, MIMO order, filter/duplexer chain and antenna-tuner population: not determinable from software at all.** This is not a gap in the capture; it is a property of the MIPI-RFFE architecture.
* A dedicated PA temperature sensor exists, so at least one main cellular PA is present and thermally monitored.

**Final confidence:** **TEARDOWN_REQUIRED** for antenna/filter inventory. **PROVEN** for the Wi-Fi/BT FEM question.

**Remaining uncertainty and what would close it:** FCC internal photographs for the GQ5012BF1 grantee (none published at the time of this pass), a physical teardown with board photography, or RF conducted/radiated measurements with a vector network analyser and a shielded chamber. 4x4 vs 2x2 LTE/NR MIMO could be narrowed non-destructively by reading `dumpsys telephony.registry` cell-info reports while camped on a 4x4-capable network - which needs a live device and a SIM.

**Impact on final inventory:** YES - the Wi-Fi/BT half is resolved and the cellular half is restated as architecturally unreadable rather than merely uncollected.

**Answers:** (1) no Wi-Fi/BT FEM; cellular FE unreadable; (2) internal photos or teardown; (3) partially; (4) only MIMO order, and only with a network; (5) no - nothing published; (6) yes; (7) MT6637-internal PA/LNA for Wi-Fi/BT; cellular FEM set UNKNOWN; (8) TEARDOWN_REQUIRED (cellular) / PROVEN (Wi-Fi-BT); (9) yes; (10) yes; (11) yes.

## Second-pass update (2026-09-08)

A wider search for `GQ5012BF1`, `GQ5012`, Armor 29 Pro Thermal regulatory internals, FCC internal photos,
X-rays and teardown photography (Q18) again found only marketing/comparison pages. No board photograph,
antenna drawing or RF-test exhibit was located. This is a documented negative search, not evidence of
absence: cellular antenna count, MIMO order, tuner/filter/duplexer population and heat-spreader stack remain
**TEARDOWN_REQUIRED / regulatory-exhibit required**.
