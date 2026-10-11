# Independent build reproduction — accepted families

Offline/static only. Stock references are authenticated read-only analysis copies.
Never run strip/objcopy against a stock path. All ELF mutations below operate only
on fresh copies of rebuilt modules. Run from space-free workspaces, low priority,
with bounded `JOBS=16` and `PYTHONDONTWRITEBYTECODE=1`.

## Source recovery and build commits

Recovery bundles are committed in `bundles/`; their hashes/trees and successful
`git bundle verify` results are in `evidence/bundle-verification.json`.
Clone with `git clone --no-hardlinks -b codex/all-c-closure <bundle> <fresh-recipe>`.

| Family | Actual tested build commit | Final preserved recipe | B1 / B2 workspaces |
|---|---|---|---|
| CMDQ | 059e2fe439309c3adc2e95b87aa547967e7e5f80 | 0b4b07f38397ca6c0630b9edc5ccf2df9251da1d | /home/armol/kernel-work/allc/cmdq-ws / cmdq-ws2 |
| Connectivity | 40bf42967a213af6faa45a6a579571973b8e5d15 | same | /home/armol/kernel-work/allc/conn-ws1 / conn-ws2 |
| Thermal | 9e0e1a0df474f1e5a748d0302fba8445f13c996d | ff6e97b3bf1f29c1e1fba4ba0c0e28493cbd0698 | /home/armol/kernel-work/allc/thermal-ws1 / thermal-ws2 |

The post-build CMDQ/thermal commits change README documentation and remove an accidental
host pycache only, not build logic/config/source. `SOURCE-CHANGES.tsv` distinguishes tested
and final commits; the provenance collector checks this difference rather than claiming
those later commits themselves were independently rebuilt.

## Pinned input mirrors

These are public-source caches, not unexplained target/provider binaries:

```sh
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export LIEPPOS_MTKACK_MIRROR=/home/armol/kernel-work/allc/mirror
export LIEPPOS_CONN_MIRROR=/home/armol/kernel-work/codex-conn-batch-01/mirror
export LIEPPOS_NATIVE_MIRROR=/home/armol/kernel-work/platform-batch-03-native-inputs
export LIEPPOS_BATCH03_NATIVE_MIRROR="$LIEPPOS_NATIVE_MIRROR"
export JOBS=16 PYTHONDONTWRITEBYTECODE=1
```

Mirrors contain immutable common/KDM/ALPS commits, pinned clang archive, kernel-build-tools,
NothingOSS connectivity source, official GKI artifacts and `mtk-ack.git`. Each bootstrap
verifies its recorded tree/hash. `SOURCE-PINS.tsv` consolidates the upstream provenance.
If mirrors are unavailable, recreate their public inputs at those exact pins; do not copy
objects or silently use an unrelated local tree. Recipes currently require offline mirrors.

## Commands in each independent clone/workspace

CMDQ: `scripts/bootstrap.sh WS`, then `scripts/bulk-build.sh WS B1` (B2 in fresh WS).
Connectivity: the same; its bootstrap includes native tools/artifact verification.
Thermal: `scripts/bootstrap.sh WS`, `scripts/native-bootstrap.sh WS`, then
`scripts/bulk-build.sh WS B1` (repeat independently for B2).
All object/module/native/NKM exit records must be zero before acceptance.

Connectivity: `scripts/accept.sh WS/out/B1 STOCK REPORT` runs strict 17-module acceptance
and the 44 mutation checks; repeat on B2. It no longer has a BTF class-C skip.
CMDQ/thermal joint scope: set `LIEPPOS_VERIFY_JOINT=1` and run
`python3 scripts/verify.py WS/out/B1 STOCK REPORT`, or the same for B2.
For their selected targets, mutation scripts in this research package accept
`RECIPE BUILD_DIR STOCK_DIR REPORT_JSON`:
`cmdq-mutation-test.py` (40 cases) and `thermal-btf-mutation-test.py` (11 cases).

`compare-build-inputs.py FAMILY WS1 WS2 REPORT_JSON` checks recorded object hashes,
compares raw/debug-stripped objects and configuration, and compares natural symvers with
only workspace-path text normalization. This debug stripping is an intermediate-object
diagnostic, not a new module acceptance exception.

## Results

- CMDQ 35/35 joint stock passes in each build; 120/120 stripped-debug objects exact.
- Connectivity 17/17 passes; all 17 stripped modules and 577 objects raw-identical.
- Thermal 34/34 passes; all 34 stripped modules match outside GNU20; 130 vendor objects
  match after debug stripping, native objects separately checked.
- All configs and compared symvers match. Full target ledgers and comparison JSON are
  preserved. Thermal native base `.BTF` matches exactly, not its entire vmlinux ELF.
- No other family's ownership or certification is changed by the joint build scope.

These are independent clean recipe/workspace builds, but use shared authenticated upstream
caches and official GKI core ABI inputs, explicitly recorded above. They are not independent
physical devices or runtime tests. Unaccepted USB/audio/legacy experiments are not recipes
certified by these results.
