# PLATFORM-BATCH-04 offline source reproduction

Frozen exact30 handoff committed before implementation in `f524b1b`.
Manifest SHA256 `77ed42ecdd9b996a78fe7ff7ee387e3c65643162b3e585d6f3424a05f1f01af1`.
Initial7D/23G, real charging14/Type-C6/USB10 source families; canonical ownership unchanged.
See SOURCE-REPOSITORIES.tsv for exact committed recipes and scopes.

## Source inputs and recovered implementation

ALPS `5e415e059253ce0d2e61c97108e5f5785d71f06f`, NothingOSS configuration
`957dac185efe46cbf6336b0fff9516d84c8cd78f`, GKI common
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, Clang17/r487747c
`7775eb113f960bc69a780b621d03a715914d4bca`.
Actual TCPC2.0.31 public lineage: MiCode
`2d6f27aa19d521409f443c8d821e2d475bdc72b6`, branch bsp-chagall-w-oss,
subtree `drivers/misc/mediatek/typec/tcpc`, Git tree
`5166ca2ab7fba22712731484a80657f27641818c`. Its genuine full source archive
is pinned by SHA256 and subtree identity in each recipe, not a private object cache.
The common IIO triggered-buffer implementation is a source-only external witness.

Historical USB/charging/MT6375/TCPC full work was inspected before new RE:
169 whole C/H recovered,38 complete changed files preserved, all composite objects
explicitly mapped in reference/compiled-unit-plan.json. Complete source patches
retain YFT charging/third-gauge behavior, PE/PD policy, MT6375 battery warning-line
layout, Type-C revision repairs and extcon/uSmart/thermal arbitration. Public/historical
source hashes and old mutable/config/header/stock-symvers risks are recorded.
Abandoned worktree and stock-harvested symvers dependencies are replaced by exact
source retrieval/archives, complete patches, genuine source provider compilation.

Kconfig base/config hash is `414cbd58794b6aae24ed2ac0beee4090fcc49967003d940822e72a376900a5fc`.
The genuine host pahole1.32 probe differs from older Batch02 input1.31; preserved
host-config-drift.md records it. No output difference is waived. Type-C water/PD/module
conditionals and actual composite Kbuild units are explicit. Header/config preparation
uses the same verified public common inputs; targets/witnesses are freshly compiled.

## Build from any participating clean source clone

```sh
export TMPDIR=/tmp TMP=/tmp TEMP=/tmp PYTHONDONTWRITEBYTECODE=1
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export JOBS=12
bash scripts/bootstrap.sh /home/armol/kernel-work/my-batch04
bash scripts/bulk-build.sh /home/armol/kernel-work/my-batch04 B1
bash scripts/bulk-build.sh /home/armol/kernel-work/my-batch04 B2
LIEPPOS_VERIFY_JOINT=1 python3 scripts/verify.py /home/armol/kernel-work/my-batch04/out/B1
```

The final joint acceptance intentionally rejects the five incomplete candidates.
Research compare-batch.py/diagnose-incomplete.py preserve all30 measured outcomes;
set LIEPPOS_BATCH_RECIPE to the source clone and pass output/comparison directories.
Do not convert a deterministic failed module into A/B.

## Independent validation and strict acceptance

cleancheck.sh clones three exact committed engines without hardlinks, makes the original
three recipes and development workspace unavailable, bootstraps a separate public-input
workspace, and freshly assembles/compiles joint30 through each engine as B1/B2.
check-determinism.py compares raw/stripped30, all target/provider intermediate objects,
source/config/core symvers/whole target symvers/natural witnesses across and within engines.
Originals are restored by EXIT trap; full proof and logs are preserved under evidence/.

Only structurally parsed GNU20-byte build-ID descriptor differences are normalized.
Every function/instruction/data/object/order/import/export/license/namespace/CRC/KCFI,
raw/semantic relocation, section/layout/symbol/string/modinfo/vermagic/srcversion and
signature axis is checked.25 whole acceptance candidates;five strict unaccepted:
charger_class,mtk_chg_type_det,rt_pd_manager,tcpc_class,tcpc_mt6375. Each has complete
function/data/section/raw+semantic relocation/CRC+KCFI/symbol/metadata mismatch ledgers.
Source-text fingerprint differences are never silently normalized. TCPC's eight actual
PD/CC/sysfs function differences are source behavior, not firmware failures.

The first independent bootstrap found an omitted newly created audio producer Makefile
in the scope patch. It failed before any target compilation, restored originals, and is
preserved in evidence/independent-attempt-01. The full patch now includes new Makefiles;
reassembly yields the same verified development source tree. The corrected fresh-clone
proof—not the failed attempt—is the acceptance evidence.

23 real ELF cases include forbidden srcversion mutation, KCFI prefix, executable/data,
CRC/relocation/symbol/string/modinfo/layout/build-ID structure/signature mutation and
actual rejection of all five unchanged incomplete modules. Public source and all recovered
C/H hashes/full patch reapplication/recovery bundles are independently verified.

## Safety and boundaries

No phone connection, ADB, PD request, USB/charging control, GPIO/MMIO/DMA/firmware/secure
command, flashing or push. Public CI core symvers is a documented source-derived ABI
input, not whole-kernel certification.18 external API slots are generated naturally
from full genuine source; matching a boundary does not certify its whole provider.
PD negotiation, third-gauge firmware/calibration, external controllers and ADSP/SCP USB
audio offload firmware/runtime remain separate. Saved hardware configuration is not a
live measurement; physical thermal/default USB routing remains UNKNOWN where unproven.
