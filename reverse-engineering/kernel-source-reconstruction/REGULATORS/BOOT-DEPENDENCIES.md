# Early boot, supplier ordering and deferred runtime validation

## Actual partition-specific lists

Exact list paths, hashes and sequence numbers are preserved in evidence/inventory/LOAD-ORDER.tsv.
The four binaries occur only in vendor_boot's platform ramdisk. All four are listed in both
normal and recovery first-stage contracts; no list or stock partition was modified.

| Module | Normal position | Recovery position | Source boundary after this closure |
|---|---:|---:|---|
|pinctrl-mtk-v2 /pinctrl-mt6878|20/21|20/21|priorA witnesses, unchanged|
|clk-common /clk-mt6878|22/23|22/23|priorA witnesses, unchanged|
|mtk-spmi-pmic|35|35|G; parent regmap/MFD/IRQ resources, not certified here|
|spmi-mtk-pmif|36|36|D; SPMI transport provider, not certified here|
|**mt6315-regulator**|**37**|**37**|four-targetA|
|**mt6363-regulator**|**38**|**38**|four-targetA|
|mtk-scpsys /mtk-scpsys-mt6878 /bringup|41/42/43|41/42/43|D; power-domain consumers/providers separate|
|mtk-dvfsrc|44|44|D; four import/type witnesses only|
|**mtk-dvfsrc-regulator**|**45**|**45**|four-targetA|
|pinctrl-mt6363 /debug|103/104|101/102|priorA witnesses, unchanged|
|mtk-mmc /ufs-mediatek-mod|107/112|105/110|priorA storage witnesses, unchanged|
|i2c-mt65xx|118|116|D; bus transport not certified here|
|**rt6160-regulator**|**124**|**122**|four-targetA, both I2C clients unbound in preserved capture|

`mtk-dvfsrc-start` is also a separately loaded vendor_dlkm module (normal list167), not
another member of the first-stage four-module target set. Its parent-created device is not
proof its driver has bound. Numbering is one-based physical lines in the actual lists.

**Stale field:** canonical audit inherited RT6160 load_order133 from an older module
classification record. Actual hashed load files prove124(normal)/122(recovery). The review
corrects only that target's load_order to124 and retains actual recovery mentions; no
unrelated inherited positions are silently repaired. Every actual load-list byte is unchanged.

## Device dependencies, not just imports

- The regulator module can register its driver before its device/regmap is available.
  Load-list order does not establish synchronous successful PMIC probing. MFD35 before
  PMIF36 is compatible with deferred registration; do not reorder it speculatively.
- PMIC slave4's enabled MT6363 MFD reference creates the named regulator child and OC
  resources; SID6's MT6319 common MFD profile populates the MT6315_6-compatible DT child.
  Required regmap must exist first; per-rail registration failures are continued by stock code.
- MT6315/MT6363 use no symbol imports from pinctrl modules, but bus IRQ/control pin setup
  and pinctrl core callbacks remain device-level prerequisites. PMIC pinctrl103 is not
  evidence that regulator registration38 must await that child.
- DVFSRC has actual symbol dependency on mtk-dvfsrc44, which creates its platform device
  and has post softdep on the regulator. The logical vcore node represents voltage requests;
  its helper's physical vcore relationship points to SID6.VBUCK4.
- SCPSYS ISP/camera domain supplies point toSID6.VBUCK1. Successful registration of the
  regulator driver cannot certify SCPSYS sequencing or camera domain transitions.
- UFS's vcc/vccq supplies point to MT6363 VEMC/VUFS12; those are configured prerequisites
  for the stock UFS path. MMC0 uses VEMC/VUFS18/DVFSRC but is disabled in the captured live
  tree. Neither finding proves every regulator rail/module is indispensable to mounting
  the first filesystem, or that all declared initial constraints represent operating volts.
- RT6160 loads after UFS; neither client was bound in the existing capture and no supply
  links target them. This is not an F exclusion/removal-safety proof: unpowered/population,
  userspace/by-name consumers, vendor assumptions and alternate boot states remain unknown.

## Conditions for future controlled Slot B verification

**Not authorized or performed now.** Obtain separate approval and a recoverable, verified
baseline with known rollback/SlotA preservation and image/signature/KMI policy before any
replacement is integrated. Retain stock load lists and exact DT first; do not enable dormant
nodes or repair source-reference quirks during the initial verification.

A separately reviewed plan should compare driver/module bindings, registered regulator names,
consumer attachments and existing fault/deferred-probe logs, then assess storage/platform
boot, CPU/GPU/camera/modem relationships and suspend/resume against stock. Voltage/current/
PMIC writes, forced state transitions, OC tests and GPIO manipulations require their own
explicit safety authorization and hardware limits; no value in these DT tables is a blanket
safe voltage target. Preserved unbound RT6160 state must not be turned into an assumed duty
to make it bind. Firmware/secure-world PM votes and dependency source certification remain
separate. All runtime acceptance is UNKNOWN/deferred; the offline four-module source proof
has no unresolved behavior-bearing binary residue.
