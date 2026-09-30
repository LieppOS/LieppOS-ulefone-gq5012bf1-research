# U9 - battery cells, pack topology, thermistors, gauge interpretation

**Current claim:** "8.4-V reading, 10600-mAh claim, 8594-kuAh gauge design" - topology and reconciliation unknown.

**Previous confidence:** UNKNOWN (recorded as an unreconciled contradiction).

**New evidence**
* **Topology is now unambiguous.** The battery `power_supply` reports `VOLTAGE_NOW = 8397000 uV` **together with** `CONSTANT_CHARGE_VOLTAGE = 4450 mV`. The MT6375 charger node sets `cv = 4450` (per cell) and the direct-charge algorithms set `vbat-cv = 8900` mV (pack) - exactly 2 x 4450. The pack-side gauge prints `Vchg:8900`.
* **The OEM specification closes the arithmetic**: Ulefone states "**21200mAh Battery (Equivalent to 10600mAh, 7.74V)**". 7.74 V is a 2-series nominal voltage (2 x 3.87 V). The headline "21200 mAh" is the 3.87 V-equivalent figure; the pack itself is rated 10600 mAh at 7.74 V (~82 Wh). There is no 2 x 5300 mAh parallel pack, and the earlier "2x5300" reading was wrong.
* **Gauge inventory**: two gauges observe the same pack -
  - `battery` = MT6375 internal gauge at i2c `5-0034` (OCV profile tables `battery0-profile-t0..t5`, 100 x 4 entries each, per-cell OCV up to 4448.4 mV; a second unused profile `battery1` peaks at 4322.0 mV; `bat_type = 0` selects profile 0);
  - `3rd-gauge` = **SH366003** at i2c `9-0055`, the pack-side gauge.
* **Live pack telemetry** (SH366003): `RSOC=79, Volt=8397, Curr=194, Temp=375, SoH:94, cycnt:26, Rc:6713, FCC:8594, Vchg:8900, Ichg=9500, SafetyAlert=0x0000, SafetyStatus=0x0000, PFAlert=0x0000, PF=0x0000`.
  `Rc 6713 / RSOC 79 % = 8497 mAh` full-scale, consistent with `FCC 8594`, so the gauge's coulomb counting is internally coherent.
* **Thermistors**: four board NTC channels exist as `thermal-ntc1/2/3/6`, all `compatible = "mediatek,mt6685-tia-ntc"` with 1328-byte lookup tables, plus the gauge's own `bat_temp` ADC channel (`io-channel-names = bat_volt, bat_temp, ptim_bat_volt, ptim_r, vref`) and a `BATTERY` thermal zone throttling at 50/55/59/60 degC. The pack reports 37.0-37.5 degC.
* **JEITA policy** from `/charger`: charge window 0-55 degC with CV stepping 4.20/4.35/4.40/4.45 V across five temperature bands.

**Contradicting evidence**
The gauge's `CHARGE_FULL_DESIGN` / `FCC` field reads **8594 mAh** where the OEM rates the pack at **10600 mAh** - about 19 % lower. `CHARGE_FULL` reads 2946 mAh, which is inconsistent with both and looks like a framework-side scaling artefact. `SoH:94` and `cycnt:26` show the cell is nearly new, so wear does not explain the gap.

**Internet sources:** VI1, VI2, VI4.

**Local evidence:** VL8, VL9, VL10; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** dmesg gauge lines and `power_supply` dumps from the frozen capture.

**Final conclusion**
* Pack architecture: **2S (two cells in series), Li-ion/Li-polymer, 7.74 V nominal, 8.90 V pack CV = 4.45 V per cell** - PROVEN.
* Rated capacity 10600 mAh at 7.74 V (marketed as "21200 mAh" at 3.87 V) - PROVEN as the OEM rating.
* Two independent gauges (MT6375 internal + SH366003 pack-side), full OCV profile tables, four board NTCs plus a pack thermistor, JEITA-banded CV - PROVEN.
* State at capture: 79 % SoC, 26 cycles, SoH 94 %, no safety or permanent-fail flags - PROVEN.
* **The 8594 mAh vs 10600 mAh discrepancy is real and unresolved.** It is most likely the value programmed into the gauge's design-capacity register rather than a physically smaller pack, but nothing in the capture proves that.

**Final confidence:** topology, chemistry, voltages, gauges, thermistors, health = **PROVEN**. Cell manufacturer, cell model, physical cell count/arrangement = **TEARDOWN_REQUIRED**. True usable capacity vs rating = **UNKNOWN**.

**Remaining uncertainty:** resolve the capacity gap with a full controlled charge/discharge under coulomb counting, or by reading the SH366003 design-capacity register directly. Cell vendor requires opening the pack.

**Impact on final inventory:** YES - the battery row is rewritten with proven topology and health, and the old "does not reconcile" note is replaced by a precise, sourced explanation plus one genuinely open number.

**Answers:** (1) 2S 7.74 V pack, dual gauges, 4 NTCs, 79 %/26 cycles/SoH 94; (2) cell vendor/model and the design-capacity register; (3) yes for topology; (4) yes for the register; (5) yes for the rating; (6) yes for the cells; (7) 2S Li-ion, 10600 mAh @ 7.74 V rated, gauge FCC 8594 mAh; (8) PROVEN topology / UNKNOWN capacity gap / TEARDOWN_REQUIRED cells; (9) yes; (10) yes; (11) no.
