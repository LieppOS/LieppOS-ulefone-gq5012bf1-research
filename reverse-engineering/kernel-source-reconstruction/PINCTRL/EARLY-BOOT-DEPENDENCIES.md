# First-stage and recovery dependencies

Stock platform vendor ramdisk `lib/modules/{modules.load,modules.load.recovery,modules.dep}`
and the prior `reverse-engineering/boot/module-loading/module-classification.tsv` capture
are the operands. All four exact identities have one canonical stock occurrence in this
ramdisk; no duplicate partition copy is collapsed into an extra target.

| Module | Normal list line | Recovery line | Dependency-resolved sequence | Captured loaded |
|---|---:|---:|---:|---|
| pinctrl-mtk-v2 | 20 | 20 | 20 | yes |
| pinctrl-mt6878 | 21 | 21 | 21 | yes |
| pinctrl-mt6363 | 103 | 101 | 113 | yes |
| pinctrl-mtk-common-v2_debug | 104 | 102 | 114 | yes |

`modules.dep`: v2 has no vendor module dependency; other three depend only on v2.
These are hard symbols, naturally reproduced in one modpost run. No boot/load list is
changed. `arch_initcall`/`late_initcall` labels in module source do not override the loader's
module initialization timing.

## Dependency tree

```
GKI core (pinctrl/gpiolib/regmap/IRQ)
  └─ pinctrl-mtk-v2 (EINT + common-v2 + Paris/MT63xx)
       ├─ pinctrl-mt6878 + /soc/pinctrl + EINT matrix/GIC parent
       │    └─ GPIO/pinctrl/EINT clients (MSDC1, USB glue, PMIC IRQ, touch/NFC/…)
       ├─ pinctrl-mt6363 + parent MT6363 SPMI regmap
       └─ pinctrl-mtk-common-v2_debug
            ├─ mtk-mmc (certified STORAGE), i2c-mt65xx: gpio_dump_regs_range
            └─ mtk-lpm-dbg-common-v2: gpio_dump_regs
```

Pinctrl SoC list lines20–21 precede certified BOOT-CLOCK-CORE lines22–31. They do not
consume clock/regulator handles directly. Peripheral clocks/regulators still must probe
for clients; pinctrl registration alone cannot certify them. MT6363 pinctrl at103 requires
parent SPMI/MFD regmap availability (see DT provider path); its absence of board consumers
is not a legitimate whole-module exclusion.

The STORAGE list at105 onward requires debug104 for mtk-mmc's import and MT6878 for
MSDC1 pins/CD. UFS uses separate host/PHY/clock resources rather than a pinctrl state.
MT6375 parent EINT15 and other power/Type-C consumers make SoC EINT significant to boot
correctness. None of the six clocks or ten storage modules was rebuilt/reclassified by
this package.

**Loaded ≠ bound.** The previous runtime ring buffer begins too late to establish complete
probe chronology. It has generic SPM EINT wake reports, not per-provider registration,
GPIO base/owner or every consumer's selected state. EINT initialization failure is a
warning while pinctrl probe may continue; tests must distinguish both stages.

## Deferred, separately authorized controlled Slot B acceptance

No step below was performed. Slot A must remain known-good with rollback rehearsed; use
only the four same-named accepted outputs in the Slot B vendor_boot ramdisk and preserve
loader order/dependency lists. No broad workspace boot reconfiguration is justified.

1. Capture earliest boot/pstore and compare probe registration, EINT matrix/parent IRQ,
   GPIO chips/bases and pinctrl owners with stock; no EINT-init warning or probe loop.
2. Require first-stage UFS mounts and normal encrypted boot; observe storage errors only.
3. Verify MSDC1 default pinmux/CD binding, normal microSD operation and UHS switching under
   separately approved hardware tests; compare pin ownership before/after.
4. Observe PMIC/Type-C interrupt operation and system wake/suspend/resume; no unexpected
   wake line or interrupt storm. Validate noirq wake/current masks rather than inventing
   a generic pad sleep state.
5. Validate existing NFC/touch/fingerprint/audio/camera/connectivity and thermal/uSmart
   consumer transitions using their own controlled test plans. Capture overlap arbitration
   (e.g. GPIO28 DMIC versus uSmart ID) without direct debug pin writes.
6. Abort on first-stage mount failure, missing GPIO/EINT controller, persistent deferral,
   storage errors, unexpected rail behavior or IRQ storm; roll back immediately.

Do not invoke tristate tests, proc pin-write handlers, manual GPIO toggles or EINT injection
as a substitute for normal consumer testing. RPMB remains observe-only under STORAGE's
security boundary. Source byte identity does not remove deployment/packaging risks.
