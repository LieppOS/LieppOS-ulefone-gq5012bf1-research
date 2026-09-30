# U16 - exact limits of OCP2131, WL2864C, RT5133 (and the rest of the power tree)

**Current claim:** "bindings and rail names only".

**Previous confidence:** UNKNOWN.

**New evidence - datasheet-level identification of every enumerated power part**

| Part | Location | What it actually is | Key ratings |
|---|---|---|---|
| **MT6363** | SPMI `pmic@4` | **Main system PMIC** (auxadc, efuse, pinctrl, keys, dynamic-loading throttling) | platform part |
| **MT6369** | SPMI `second_pmic@5` | **Sub-PMIC** with audio codec (`mt6369codec`), headset `accdet`, and the `VIBR` haptic LDO | `mt6369_vibr` 1.2-3.5 V, 680 us ramp |
| **MT6319** | SPMI `mt6319@6` | **External buck regulator** (`extbuck-debug`, `mt6319-6-regulator`) - was entirely absent from the original inventory | - |
| **MT6685** | SPMI `mt6685_mfd` | Clock-buffer / RTC / consys MFD, and the **TIA-NTC thermistor front end** (`thermal-ntc1/2/3/6`) | 4 NTC channels |
| **RT5133** | i2c `5-0018` | **Camera-sensor LDO PMIC**, *not* a system/audio PMIC; frozen runtime evidence shows driver `rt5133` bound, while no standalone module ships (built-in/non-module path) | Datasheet: **8 LDOs** (2 x DVDD, 4 x AVDD, VIO, VAF) + 3 GPOs; runtime binding strongly supports population, but exact die/BOM and rail use remain unverified |
| **WL2864C / WL2868C family** | i2c `11-0029`, bound | Populated **camera LDO PMIC** (Will Semi / OmniVision); exact revision unresolved because the driver/DT supports both IDs | **7 LDOs**: 2 x DVDD, 2 x AVDD, VDDIO, VDDAF, **VDDOIS**; DT-visible rail values listed below |
| **OCP2131** | i2c `6-003e` | **Display bias** (Orient-Chip), bound via `mediatek,i2c_lcd_bias` | programmable dual output (positive/negative), panels up to 10 inch |
| **RT6160(A)** | i2c `5-0075` and `6-0075` | Two DT-declared **single-inductor ACOT synchronous buck-boost** alternates; both unbound | Datasheet: up to **3 A** each; physical population on this unit is **UNKNOWN** |
| **MT6375** | i2c `5-0034` | Charger + fuel gauge + TCPC + ADC | `cv 4450 mV`, `ichg 2000 mA`, `vbus-ov 14500 mV`, 9 ADC channels |
| **SC8571 x2** | i2c `11-0066` master, `6-0067` slave | 2:1 / 4:1 **charge pumps** | exact part: **2-cell, 8 A**, 98.65% peak efficiency, 80-pin CSP; board config caps each instance at 6.55 A |
| **SC8510** | i2c `6-0069` | **Bidirectional** switched-capacitor converter (reverse path) | up to 99.5 % eff., forward 2:1 to 10 A, **reverse 1:2 to 4 A** |
| **SH366003** | i2c `9-0055` | Pack-side **fuel gauge** | reports SoH, cycle count, FCC, Vchg, Ichg, safety/PF flags |

Additional structure: the `charger` framework instantiates `mtk-master-charger`, `mtk-slave-charger`, and four divider abstractions (`mst-div`, `mst-hvdiv`, `slv-div`, `slv-hvdiv`), i.e. both 2:1 and 4:1 modes on both pumps.

**Contradicting evidence**
The original inventory described RT5133 as "the I2C `5-0018` PMIC", implying a system PMIC. Richtek's product page shows the declared part is a **camera** LDO PMIC, while the genuine system PMICs (MT6363/MT6369/MT6319) sit on SPMI. The RT5133 DT declaration and MT6369 active device therefore describe different roles. The frozen runtime bus capture at `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt` shows `5-0018` bound to driver `rt5133`; absence of a `vendor_dlkm` module therefore means a built-in/non-module driver path, not an unbound client.

**Internet sources:** VI12 (RT5133), VI14/VI28 (WL2864C/WL2868C family), VI15 (OCP2131), VI13 (RT6160A), VI35 (SC8571 exact part), VI11 (SC8510).

**Local evidence:** VL13, and the SPMI/I2C enumeration in `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** bus enumeration and charger register dump from the frozen capture.

**Final conclusion**
The populated power tree is stratified as **MT6363 main PMIC + MT6369 sub-PMIC/codec + MT6319 external buck + MT6685 clock/RTC/NTC** on SPMI; bound I2C devices include **MT6375 charger/gauge/TCPC, 2 x SC8571 charge pumps, SC8510 reverse pump, SH366003 pack gauge, WL2864C/WL2868C-family 7-channel camera LDO with VDDOIS, RT5133 camera LDO, and OCP2131 display bias**. The two RT6160A nodes remain unbound alternates whose physical population is unknown.

**Final confidence:** identities/functions of bound devices and the WL2864C/WL2868C family = **PROVEN / STRONGLY_SUPPORTED**; exact WL die revision = **UNKNOWN**. RT5133 camera-LDO role and runtime driver binding are **PROVEN**, while exact die/BOM and rail use remain **UNKNOWN**. RT6160 functions are proven at datasheet level, but their clients remain unbound and population is unknown. Per-rail runtime settings beyond DT-visible values remain **UNKNOWN**.

**Remaining uncertainty:** read `/sys/class/regulator/*/{name,microvolts}` on a rooted stock boot to capture the actual rail settings. Register-level probing is explicitly out of scope (write access is forbidden and unnecessary).

**Impact on final inventory:** YES - three previously unlisted power ICs are added (MT6363, MT6369, MT6319, MT6685), RT5133 is reclassified, and every part gains a rating.

**Answers:** (1) all parts identified with ratings; (2) the programmed per-rail values; (3) yes for identity; (4) yes for the rail values; (5) yes; (6) no; (7) see the table; (8) PROVEN identities / UNKNOWN board-programmed limits; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

* **A WL2864C/WL2868C-family camera LDO PMIC is populated; exact revision is UNKNOWN.** The node is named
  `wl2864c_pmu@29` / `will,wl2864c_pmu`, the bound module is `custom_ldo_wl2868`, and the node carries a
  two-variant ID table (`id_val_2864 = 0x28`, `id_val_2868c = 0x82`, `id_mask = 0xFF`). Neither software name
  is the probed ID value, so selecting WL2868C would be false certainty. Programmed
  rails visible in DT: `avdd1 = avdd2 = 2850 mV`, `dvdd1 = dvdd2 = 1200 mV`, `vref = rvp = 1800 mV`, enables
  on GPIO 69/131/187, plus **`ois-en-gpios = <133>`** (L21, VI28). Both parts are the same 7-channel family
  (2x DVDD, 2x AVDD, VDDIO, VDDAF, **VDDOIS**), so only the die revision is in question.
* `rt5133@18` (Richtek 8-LDO camera PMIC, VI12) is `status = "okay"` and the frozen runtime bus capture shows
  I2C `5-0018` bound to driver `rt5133`. No standalone module appears in `vendor_dlkm`, so this is a
  built-in/non-module driver path. Both `rt6160@75` instances (`richtek,rt6160`, `richtek,rt6160-vbb`; ctrl
  words `0x11` / `0xa6`) remain unbound alternate declarations; their population is **UNKNOWN**, not "not fitted".
* `lcd_ocp2131@3e` binds `I2C_LCD_BIAS` from module `mediatek_drm_gateic` with five enable GPIOs
  (61, 124, 39, 40, 188): the panel-bias / gate-IC supply path (VI15). MT6375 is confirmed as the
  SoC-side **buck charger** PMIC (BATFET, VBUS OVP, AICR/MIVR, OTG CV/CC), not a display part (VI34).
* Unchanged: per-rail *programmed* limits live in driver defaults and runtime registers, so they stay
  UNKNOWN without a live `i2cget`/debugfs read.
