# Four-identity audit closure

Maintained source commit: `0c128caa3b6d875fe4525e52f3dbea52d96c9070`.
Research reconstruction checkpoint: `9599bc7c76be70b17f6190fd7c39f4a3e47bc8f3`.
Baseline audit checkpoint: `3fb8eac` (117 certified /341 uncertified).

The audit's exact four pinctrl identities moved **D → A**. No other454 canonical rows
changed; all458 identity keys and every stock occurrence remain. Component ownership,
component status, load phase/order, stock SHA256/path and necessity fields are unchanged
for every identity (`evidence/inventory/audit-scope-result.json`). All four remain in the
first-stage contract, whose uncertified count moves165→161. One debug-module DONE/source
discrepancy is resolved without a component status change.

Current classes: **A120, B1, C4, D190, E0, F0, G143**.
Totals: **121 certified /337 uncertified /458 distinct binaries**;457 filenames,
471 partition occurrences. The source queue has153 projects; PINCTRL is no longer pending.
Next: `CANDIDATE:device_modules:drivers/regulator`:
`mt6315-regulator.ko`, `mt6363-regulator.ko`, `mtk-dvfsrc-regulator.ko`, `rt6160-regulator.ko`.
No next-group reconstruction was started under this scope.

Validator: **PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES**, zero errors.
Audit mutation suite: **14/14 pass** (`evidence/inventory/audit-mutation-tests.txt`).
Dedicated complete-ELF verifier mutation suite: **9/9 pass** (pristine/ID accepted;
instruction/table/CRC/metadata/relocation/symbol edits rejected on disposable copies).
DT parser crosschecked against fdtget on5 complete resource properties; static/live mux,
GPIO, state references and EINT configurations agree after excluding availability and
synthetic OF node-name metadata—not behavior. MSDC0 runtime disable remains explicit.

Workspace taxonomy remains100 DONE /36 PARTIAL /3 BLOCKED /0 TODO. All pre-existing
manifest drift sets match the authoritative audit baseline:19 hash/size discrepancies,
408 unregistered files and one duplicate; none concealed or repaired.
No GPIO operation, EINT triggering, state selection, ADB, reboot, flash, runtime module
load, slot switch, firmware/calibration access or push occurred.
