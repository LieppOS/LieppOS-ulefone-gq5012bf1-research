# Four-identity audit closure

Final accepted maintained source commit: `33130d53c94404f65e1661ffa4113bde21cb4b08`.
Initial reconstruction/source commit: `b6aaaf3d7ae0bdbc853ba6fe5c6890aa386a91ff`.
Research reconstruction checkpoint: `c0811c1`. Baseline audit: `70e9611`.

**Exactly four identities D → A**: mt6315-regulator, mt6363-regulator,
mtk-dvfsrc-regulator, rt6160-regulator. All other454 rows unchanged.458 identity keys,
471 stock partition occurrences and457 filenames preserved. Component owner/status,
stock hash/path/size, loading phase and necessity fields unchanged for all identities.
The sole load-order metadata correction is RT6160 **133→124** (recovery122), backed by
actual hashed stock load files; none of those files changed.

Current classes: **A124, B1, C4, D186, E0, F0, G143**.
Totals: **125 source-certified /333 uncertified /458 distinct binaries**.
First-stage contract gaps:161→157; actual hardware necessity remains independently bounded.
Queue:152 projects. Next: `CANDIDATE:device_modules:drivers/interconnect/mediatek`:
`mmqos-common.ko`, `mmqos-mt6878.ko`, `mtk-emi.ko`. No next-group work started here.

Final validator: **PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES**, **zero errors**.
Audit mutation suite: **14/14 pass**. Complete-ELF verifier mutations: **9/9 pass**.
Fresh final-commit clone bootstrapped solely from the separately preserved public regulator
mirror and independently passed B1/B2 plus all stock/code/data/ABI/KCFI/relocation checks.
The original independent run also demonstrated the development tree could be unavailable.
Two generated Python cache files were removed before final acceptance; no tracked.o/.ko/.pyc
exists in the final maintained recipe. No C/compiler/build logic changed during that cleanup.
Initial evidence is retained, not silently replaced by the second run.

Graph validation:42 target DT regulator nodes,32 target supply links,84 source/DT checks,
114 independent fdtget checks,402 identical static/live controller properties and262 typed
clock/domain/ICC references across both operands. No operating voltages measured; both
RT6160 I2C clients unbound in the preserved capture. MFD/SPMI/DVFSRC source gaps remain.

Workspace taxonomy remains100 DONE /36 PARTIAL /3 BLOCKED /0 TODO. Authoritative pre-existing
manifest drift sets are identical:19 hash/size discrepancies in five components,408
unregistered files in nine and one duplicate. No component promotion, alias ownership
change, completed-package edit or concealment of old drift.

No ADB, PMIC/regulator/GPIO setting, voltage/current change, hardware power transition,
firmware/calibration operation, reboot, flash, slot switch, experimental module load or push.
