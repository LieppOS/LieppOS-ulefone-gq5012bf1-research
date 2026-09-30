# U10 - 120 W charging, PD / PPS / UFCS profiles

**Current claim:** "paths and claims; 5-V/1-A observed" - protocol set and power ceiling unverified; UFCS suspected.

**Previous confidence:** POSSIBLE.

**New evidence**
* **Supported charging protocols are enumerated by the kernel**: `mtk-master-charger` reports `POWER_SUPPLY_USB_TYPE = [Unknown] SDP DCP CDP PD PD_PPS`. **UFCS is absent from the list**, and no UFCS node, driver or string exists anywhere in the device tree (verified by a full-tree byte scan).
* **The direct-charge algorithms and their ceilings were decoded**:
  | Node | Purpose | Adapter current levels | Adapter voltage window | Pack CV |
  |---|---|---|---|---|
  | `/pe5` | PE 5.0 dual-pump | `ita-level-dual = 6000, 4500, 3400, 2000 mA` | 13.6 - 20.0 V | 8750 mV |
  | `/pe5p` | PE 5.0 Plus | `ita-level = 5000, 4500, 3750, 3000 mA` | 14.0 - 20.0 V | 8900 mV |
  | `/hvbp` | high-voltage battery pump | `ita-level = 2500..2000 mA` | up to 11.0 V | 8900 mV |
  | `/pe45`, `/pe2`, `/pe` | legacy PE / dual-switch | 3.0 - 3.2 A | 5 - 12 V | - |
  `6000 mA x 20 V = 120 W`, matching Ulefone's published "**Charging: 120W (20V/6A)**" exactly.
  All direct-charge nodes declare `support-ta = "pca_ta_pps", "pd_adapter"` - **PPS only**, no proprietary or UFCS adapter class.
* **The hardware that delivers it**: two **SouthChip SC8571** charge pumps in master/slave (`sc,sc8571-master` at i2c `11-0066`, `sc,sc8571-slave` at `6-0067`). The exact-product page specifies a **2-cell, 8 A switched-capacitor direct charger with 98.65% peak efficiency**; the part uses an 80-pin CSP package (VI35). The two-chip 2:1 divider pair is matched to the 8.9 V pack and the board itself configures up to 6.55 A per instance. Four `power_supply` abstractions exist: `mtk-mst-div-chg`, `mtk-mst-hvdiv-chg`, `mtk-slv-div-chg`, `mtk-slv-hvdiv-chg` (2:1 and 4:1 modes, master and slave).
* **Reverse path**: a **SouthChip SC8510** bidirectional switched-capacitor converter at i2c `6-0069` (`sc,sc8510`, driver `sc851x`) - forward 2:1 up to 10 A, **reverse 1:2 up to 4 A** - which is the mechanism for Ulefone's "wired reverse charging, 10 W" from a 2S pack to a 5 V USB output.
* **Pack-side ceiling**: the SH366003 reports `Ichg = 9500 mA` at `Vchg = 8900 mV` (~84.5 W into the pack, consistent with ~120 W at the wall minus conversion and cable loss).
* Safety envelope: `vbus-ov = 14500 mV` on the MT6375 path, `vbus-sw-ovp-voltage = 22000000 uV` system-wide, `chg-time-max = 5400 s` for direct charge.
* Observed state in the capture was only `CC = 500 mA, AICR = 500 mA, MIVR = 4500 mV` - i.e. an SDP/USB host, not a charger. That is why the original audit saw "5 V / 1 A".

**Contradicting evidence:** none. The earlier suspicion of UFCS support is positively refuted.

**Internet sources:** VI1, VI2, VI4 (120 W = 20 V/6 A, PD/PPS, 10 W wired reverse); VI10 (SC8571 ratings); VI11 (SC8510 bidirectional ratings).

**Local evidence:** VL9, VL10; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** `power_supply` USB-type list and charger register dump from the frozen capture.

**Final conclusion**
The charging system is a **USB PD 3.0 with PPS** design - **no UFCS, no proprietary protocol** - implemented as **2S direct charging through a dual SC8571 charge-pump pair**, configured for **up to 6 A at 20 V (120 W)** via MediaTek's PE 5.0 algorithm, with an SC8510 providing the reverse 1:2 path for **10 W wired reverse output**. Every number in Ulefone's published charging claim is now corroborated by board configuration and component ratings.

**Final confidence:** protocol set (PD + PPS, no UFCS) = **PROVEN**. 120 W configuration and the silicon capable of it = **STRONGLY_SUPPORTED** (configuration and component ratings agree; no wall-power measurement was made). 10 W wired reverse path = **STRONGLY_SUPPORTED**.

**Remaining uncertainty:** actual delivered power, thermal derating curve and time-to-full need a **certified 20 V/6 A PPS source with inline power logging**, which is a physical test, not a read-only query.

**Impact on final inventory:** YES - charging row rewritten; UFCS removed from all reports; the capability matrix "120-W untested" cell becomes "120 W configured, PD/PPS only, unmeasured".

**Answers:** (1) PD+PPS, 120 W config, dual SC8571, SC8510 reverse; (2) a metered charge run; (3) yes; (4) yes (`/sys/class/power_supply/*` during charge); (5) yes; (6) no; (7) USB PD 3.0 PPS 20 V/6 A with 2 x SC8571 + SC8510; (8) PROVEN protocols / STRONGLY_SUPPORTED power; (9) yes; (10) yes; (11) yes.

## Second-pass update (2026-09-08)

**Rating correction with a source change.** The SC8571 *exact-product* page describes a **2-cell, 8 A
switched-capacitor direct charger at 98.65% peak efficiency**; the accompanying exact-part datasheet listing
identifies an **80-pin CSP, 3.425 x 4.151 mm** package (VI35). The earlier "80 W / 10 A" values were copied
from the vendor's category page and cannot be tied to SC8571, so they are withdrawn; `CSP80` itself is
corroborated and retained. What actually
bounds the design is the board config: `ichg 390..6550 mA`, `ilimit 600..6550 mA` on two bound instances
(master `11d71000/sc8571@66`, slave `11e01000/sc8571@67`), `charger/battery-cv = 4450000` per cell with
`vbat-cv = 8900 mV` pack, and `max-charger-voltage = 12500000` (L21, VL10).

The reverse path is now quantified too: `sc851x-charger@6f` (`sc,sc8510`) exposes `vsys 3500..12500 mV`,
`vbus 4000..11000 mV`, `ichg 0..12750 mA`, `vfet_fwd 4300..5700 mV`, `vfet_rvs 4500..5900 mV` and separate
forward/reverse OCP windows - an explicitly bidirectional 2:1 / 1:2 pump (VI16), i.e. the silicon behind
**wired** 10 W reverse output. Note that MT6375's `OTG_CV`/`OTG_CC` fields (VI34) are wired USB-OTG
reverse-mode registers and must not be read as wireless-charging evidence; the wireless verdict stays
PROVEN-absent.
