# U11 - wireless charging and reverse wireless charging

**Current claim (original audit):** "50-W wireless and 30-W reverse policy constants + RT6160 rails; receiver/output test absent" - listed as a strongly supported hidden capability.

**Previous confidence:** POSSIBLE / LIKELY (item B12 in the hidden-capability report).

**New evidence - all negative and mutually reinforcing**
1. **No wireless-charging device tree node exists.** A byte-level scan of all 10,504 live device-tree entries for `wireless|wlc|wpc|qi|mt5786|nu16|cps4|stwlc|idtp|rx1619` returned only false positives inside `met/mcupm-rts-header` profiling strings.
2. **No wireless `power_supply` exists.** The complete class listing is `3rd-gauge, battery, mtk-gauge, mtk-master-charger, mtk-mst-div-chg, mtk-mst-hvdiv-chg, mtk-slave-charger, mtk-slv-div-chg, mtk-slv-hvdiv-chg, primary_chg, sc-cp-master, sc-cp-slave`. An Android device with a wireless receiver always exposes a `wireless` supply.
3. **No wireless-charging IC is on any bus.** Every I2C/SPI client was enumerated with address, compatible and bound driver; none is a receiver/transmitter controller.
4. **The ODM does have wireless-charging support - for other projects.** `init.yft.rc` (a shared, platform-wide file) references `/sys/class/wireless_charger/{reverse_charger, rxdetect, wireless_fast_charging}` and `.../13-002b/mt5786group/reverse_charger`. Those paths **do not exist** on this device: there is no i2c-13 bus and no `13-002b` client. This is exactly the kind of ODM option catalogue that must not be mistaken for a bill of materials.
5. **The OEM does not claim it.** Ulefone's own spec sheets list "Supports 120W flash charging" and "Supports **wired** reverse charging, 10W" and say nothing about wireless. GSMchoice's "Wireless battery charging" field is left empty.

**Contradicting evidence:** none. The original audit's "50 W wireless / 30 W reverse" figures do not appear in any Ulefone material for this model and appear to have been carried over from a different device.

**Internet sources:** VI2, VI4, VI6.

**Local evidence:** VL9, VL17, plus the full-tree scan recorded in `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** complete `power_supply` inventory and bus enumeration from the frozen capture.

**Final conclusion**
**The Ulefone Armor 29 Pro Thermal has no wireless charging and no wireless reverse charging.** Its only reverse-power capability is **wired 10 W USB output**, implemented through the SC8510 bidirectional charge pump. The prior claim of 50 W wireless / 30 W reverse is **disproven** and must be removed from every report.

**Final confidence:** **PROVEN absent** (four independent negative lines plus the OEM's own specification, which affirmatively documents the wired-only alternative).

**Remaining uncertainty:** none material. A teardown would confirm the absence of a receiver coil, but no software or specification evidence points to one.

**Impact on final inventory:** YES - this is one of the two most important corrections in this pass. The claim is removed from MASTER-HARDWARE-INVENTORY, from HARDWARE-CAPABILITY-MATRIX and from UNUSED-HIDDEN-CAPABILITIES item B12.

**Answers:** (1) not present; (2) nothing further - the negative is well covered; (3) yes; (4) yes; (5) yes; (6) no; (7) none fitted; wired 10 W reverse via SC8510; (8) PROVEN (absent); (9) yes; (10) yes; (11) yes - a hidden-capability item is deleted.
