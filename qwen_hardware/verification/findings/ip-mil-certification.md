# U22 - IP / MIL certification detail and glass grade

**Current claim:** "IP68/IP69/IP69K, MIL-STD-810H, 2-m/30-min water - OEM claims only".

**Previous confidence:** POSSIBLE (claim-level).

**New evidence**
* Ulefone's product page and two regional storefronts state **IP68 + IP69K + MIL-STD-810H**, with **1.5 m drop resistance** and **30 minutes at 1.5 m water depth**.
* Notebookcheck independently repeats IP68/IP69K, MIL-STD-810H and 1.5 m drop, and gives the mass as about **688 g**.
* GSMArena specifies the main display cover as **Corning Gorilla Glass 3**.
* Supporting hardware context consistent with a sealed rugged build: no removable back, a **3.5 mm headset jack with `accdet` detection** (implying a sealed/gasketed jack), a magnetic/pogo expansion connector in the OEM specification, and an `MD1-SIM1/SIM2-HOT-PLUG-EINT` pair implying a gasketed tray.

**Contradicting evidence**
The original audit recorded "**2-m**/30-min water". Every OEM and independent source reviewed says **1.5 m**. That figure was overstated and is corrected here. The original also listed "IP68/IP69/IP69K"; IP69 and IP69K are effectively the same test designation, so the correct rendering is IP68 + IP69K.

**Internet sources:** VI7 (OEM: IP68/IP69K, MIL-STD-810H, 1.5 m drop, 30 min at 1.5 m), VI8 (Notebookcheck corroboration + 688 g), VI5 (Gorilla Glass 3).

**Local evidence:** none - certification is not a software-visible property. The device tree confirms sealed-design correlates (headset accdet, SIM hot-plug EINTs) but proves nothing about ingress ratings.

**Read-only live evidence:** none applicable.

**Final conclusion**
**IP68 + IP69K and MIL-STD-810H are consistently claimed by the OEM and repeated by independent outlets, with 1.5 m / 30 min water immersion and 1.5 m drop resistance, Gorilla Glass 3 cover, and ~688 g mass.** These remain **manufacturer claims**: no test house report, certificate number or laboratory data was located, and none is normally published for this class of device.

**Final confidence:** **STRONGLY_SUPPORTED as a consistently published claim**; **UNKNOWN as independently verified performance**. Gasket material, adhesive grade, port sealing method and the actual test protocol used = **TEARDOWN_REQUIRED / test-report required**.

**Remaining uncertainty:** obtaining the IEC 60529 and MIL-STD-810H test reports from Ulefone or the certifying laboratory; alternatively an accredited ingress test. Note that **any disassembly or reflashing invalidates the sealing**, so this must not be attempted casually on a working unit.

**Impact on final inventory:** YES - the water-depth figure is corrected from 2 m to 1.5 m, IP69 is folded into IP69K, drop resistance and cover glass are added.

**Answers:** (1) IP68/IP69K + MIL-STD-810H, 1.5 m/30 min, GG3, 688 g; (2) an accredited test report; (3) no; (4) no; (5) yes, at claim level; (6) yes/lab; (7) as above; (8) STRONGLY_SUPPORTED (claim) / UNKNOWN (verified); (9) yes; (10) no; (11) no.
