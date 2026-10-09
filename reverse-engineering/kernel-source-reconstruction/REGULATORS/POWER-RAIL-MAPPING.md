# GQ5012BF1 regulator architecture and register behavior

## Evidence vocabulary

- **PROVEN_RUNTIME:** only what an existing capture actually establishes. No runtime
  voltages/currents, regulator state or PMIC chip-id measurement was gathered here.
- **ENABLED_IN_STOCK_DT:** available node and its configured constraints/references; not
  proof of successful probe, output use or physical population.
- **STOCK_BINARY_IMPLEMENTATION:** callbacks, tables and constants from the accepted
  source, whose entire compiled ELF matches stock outside GNU ID metadata.
- **SOURCE_REFERENCE_ONLY:** other compatible profiles/capabilities or disabled DT consumers.
- **UNKNOWN:** actual board measurements, physical part identity, current state and omitted
  by-name/firmware-managed relationships without sufficient evidence.

All regulator-name nodes, constraints, flags and exact raw DT properties are retained in
`evidence/hardware/DT-RAILS.tsv`. All source descriptor/control fields and tables are in
SOURCE-RAILS.tsv / SOURCE-DESCRIPTORS.json. These are generated from the accepted compiler's
preprocessing, not a generic datasheet. Never interpret driver range bounds as measured volts.

## Topology

| Block | Stock DT identity | Driver selection | Instantiation evidence |
|---|---|---|---|
| Main PMIC | `/soc/spmi@1cc04000/pmic@4`, `mediatek,mt6363`, SID4 | generic `mtk-spmi-pmic` MFD creates platform `mt6363-regulator` | enabled DT,36 declared regulator nodes; binding/registration unknown |
| External buck block | `/soc/spmi@1cc04000/mt6319@6`, `mediatek,mt6319`, SID6 | parent MFD common profile populates child `mt6319-6-regulator`, compatible `mediatek,mt6315_6-regulator` | enabled DT;3 declared outputs; exact physical die identity unknown |
| Logical core request | `/soc/dvfsrc@1c00f000`, `mediatek,mt6878-dvfsrc` | `mtk-dvfsrc` creates platform `mtk-dvfsrc-regulator` | enabled DT;one dvfsrc-vcore node; not a physical PMIC |
| Buck-boost candidates | I2C5/6 address0x75 (`richtek,rt6160`) | rt6160 I2C driver | enabled DT;**both client driver links unresolved in existing stock capture** |

The MFD/PMIF and DVFSRC providers are not source-certified by this four-module task.
Parent source describes16-bit regmap register addresses,8-bit data, max0xffff over SPMI;
child register addresses below are relative to the appropriate PMIC slave, not physical MMIO.
MT6319 is not a mistaken filename: the regulator-compatible explicitly selects the MT6315
register/descriptor ABI. Do not rename ownership or infer a different chip from node names.

## MT6315 regulator implementation and board delta

Four VBUCK descriptors:192 selectors, encoded0..191,6,250µV steps up to1,193,750µV.
Stock DT constraints on the three declared outputs are300,000..1,193,750µV. Zero-selector
encoding is not evidence that the phone ever operates a rail at0V.

- Common enable register0x1440: per-buck bits0..3; enable/disable write set(+1)/clear(+2)
  aliases rather than read-modify-write. Low-power bits use0x1443.
- VSEL registers:0x1449/0x144b/0x144d/0x144f, mask0xff; DA voltage/status pairs at
  0x1499/0x149d,0x1519/0x151d,0x1599/0x159d,0x1619/0x161d.
- Getter selects DA voltage when the DA enable/QI bit is set, otherwise programmed VSEL.
- Mode register0x16b1; AUTO→NORMAL, force PWM→FAST, LP→IDLE. Leaving IDLE waits100..110µs.
- SID6's source defaults size3, VBUCK1 mask0xb; **stock DT overrides buck-size=4 and mask=1**,
  VBUCK3 mask=4. Registration attempts all four descriptors; VBUCK3 has no declared rail
  child. Absence of a DT constraint node is not proof of failed registration or missing silicon.
- Shutdown writes protection keys0x9c/0xea at0x3a0/0x39f, sets bit0 at0x139, clears keys.
  No shutdown or power transition was executed here.
- No explicit suspend/remove callbacks or configurable current-limit operation. Probe
  failures for individual rails are logged and continued; aggregate success is not proof
  every rail registered. No direct hardware fault-notifier or power-good callback beyond
  DA on/off status is provided by this driver.

## MT6363 implementation

39 source descriptors:10 bucks,3 SSHUB variants,7 SRAM LDOs,18 table LDOs and current-only
ISINK_LOAD. Stock declares36: the three SSHUB descriptors are not declared in DT. The
probe still iterates all39; unspecified/failed registrations remain unknown, not invented.

Driver selector tables:
- VS2:0..1.6V,12.5mV steps; VS1:0..2.2V,12.5mV.
- VBUCK1..7/VS3 and SSHUB:0..1.19375V,6.25mV steps.
- Seven SRAM outputs:0.4..1.19375V,6.25mV steps.
- Six complete discrete LDO tables are retained in SOURCE-DESCRIPTORS.json. Typical VUFS18
  shares the0.6..2.1V/100mV table; VUFS12 uses the nonuniform0.55..1.85V table; VEMC uses
  the16-entry1.2..3.5V table. None of those names fixes the operating voltage.

Selected register witnesses (complete descriptor fields, masks, calibration/mode/op control
addresses for every rail are in the generated source ledger):

| Descriptor | Enable register/mask | VSEL register/mask | LP register/mask |
|---|---|---|---|
|VEMC|0x1c23/0x1|0x1b40/0xf, bank selected by TOP_TRAP|0x1c23/0x2|
|VUFS12|0x1c31/0x1|0x1f92/0xf|0x1c31/0x2|
|VUFS18|0x1c3f/0x1|0x1f18/0xf|0x1c3f/0x2|
|VBUCK5|0x0240/0x20|0x0251/0xff|0x0246/0x20|
|VBUCK6|0x0240/0x40|0x0252/0xff|0x0246/0x40|
|VSRAM_APU|0x1e9d/0x1|0x1b47/0x7f|0x1e9d/0x2|
|VSRAM_CPUM|0x1e1d/0x1|0x1b45/0x7f|0x1e1d/0x2|

Buck/linear1 enable uses SET/CLR aliases; table/linear2/SSHUB paths use core regmap ops.
PWM changes unlock buck control with0x5543. DT mode encodings0/1/2 map to NORMAL/FAST/IDLE;
LDOS permit0/2. Although of_map_mode maps3→STANDBY, set_mode rejects it; **no selected DT
rail allows mode3**. This is a reference capability inconsistency, not a stock DT conflict.
Current-only ISINK_LOAD toggles0xff at ISINK_EN_CTRL0 and0xf0 at CTRL1; it does not expose
set_current_limit. Source ordering of its enable/disable writes is preserved.

VEMC unlocks with0x9c9c and selects lower/upper nibble according to TOP_TRAP=0/1. Its
invalid-trap getter returns-EINVAL; the setter's unchanged default branch does not write
VSEL. VA15's protected path also updates an EFUSE-named reserved configuration field.
Neither behavior was rewritten or exercised on a device.

The set_load callbacks use LP thresholds100mA(bucks)/10mA(table LDOs) to restore saved
hardware OP_EN/OP_CFG or force normal mode; these are **load-policy thresholds, not a
programmable current limit**. Probe backs up three OP_EN bytes + OP_CFG(+5); backup failure
sets the threshold to0, disabling that load-control feature. Rails with no threshold do
nothing in set_load. The driver has no explicit suspend/resume/remove/shutdown callbacks.

Twenty named over-current resources are supplied by the MFD reference implementation.
When available, a threaded high-trigger IRQ is disabled, enabled-state checked, OC event
notified, then reenabled through delayed work (default10ms; DT override property supported).
Optional/missing IRQ or per-rail failure is continued, so probe success does not certify all
fault paths. No OC event or IRQ was triggered in this task.

## DVFSRC logical regulator

The MT6878 parent compatible selects one VCORE descriptor with **575000/600000/650000/725000µV**
selectors. Other compiled SoC/VSCP profiles are SOURCE_REFERENCE_ONLY here. Its operations
are list/get/set selector, not enable/disable or direct PMIC regmap access. Set dispatches
VCORE_REQUEST to the parent, then emits the PM-QoS trace; the void API cannot establish
hardware transition success and the callback returns0. Get queries the parent's current
level and propagates its error. DVFSRC/SPM resources are0x1c00f000/0x1c001000, size0x1000
in each case. Physical VCORE target is linked by dvfsrc-helper.vcore-supply to6_vbuck4;
this explains request vs physical rail, without measuring how firmware votes are applied.

## RT6160: preserved capability, unbound capture

Two nodes have no target DT supply consumers or phandles, and no enable GPIO or
richtek,vsel-active-low flag. Driver default active VSELH=0x05; suspend VSELL=0x04.
I2C regmap8/8, max0x05, flat cache, STATUS0x02 volatile. DEVID0x03 upper nibble must be0xa0.
Driver range2.025..5.2V in25mV steps (128 selectors); DT node5 permits that range,
node6 requests fixed3.25V. Both always-on declarations are configuration only.

Optional enable GPIO: enable drives high, waits100..200µs and syncs cache; disable makes
cache-only/dirty and drives low. Without GPIO, enable returns0 and disable-EINVAL. Mode
AUTO/NORMAL vs FPWM/FAST uses CNTL0x01 bit3. Suspend voltage uses the opposite VSEL bank;
ramp table1000/2500/5000/10000µV/µs chooses next larger speed (0→fastest).
Error flags from STATUS: bits4/1→overtemperature,3→undervoltage,2→overcurrent,
**bit0 set→FAIL in stock code**; do not change polarity using a generic datasheet assumption.
No IRQ handler, configurable current-limit operation or explicit PM callback is registered.

Source ignores stock node5's `is-existed=0`; it is not a reliable probe-disabling property.
Existing capture shows literal unresolved `/devices/.../5-0075/driver` and6-0075 paths,
not `/sys/bus/i2c/drivers/rt6160`. The following rt6160 text is client-name, not binding.
No probe failure cause, PCB population or removal safety is inferred from this evidence.
