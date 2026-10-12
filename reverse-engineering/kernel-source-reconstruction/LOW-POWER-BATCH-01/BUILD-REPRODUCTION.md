# Build reproduction

## Development (quarantined)

`/home/armol/kernel-work/low-power-batch-01/dev` was renamed to `quarantined-development` before the proof.
It was not deleted, and `prove-fresh.sh` refuses to run while the original path exists. D1, D2 and D3 logs and
outputs are in `evidence/development/`.

## Independent proof (`scripts/prove-fresh.sh`)

`EXPECT_COMMIT=185621496e49… prove-fresh.sh B1 56-59` and `… B2 60-63` ran in parallel, each at nice 10 with
JOBS=4 on its own four-CPU set. Each build:
1. Clones `bundles/low-power.bundle` with `--no-hardlinks`. The clone must be at the exact commit, have no
   alternates, and pass `fsck --full` and `bundle verify`.
2. Bootstraps a fresh workspace offline from the read-only `interconnect-pin-mirror`: common, clang
   (tree-hashed), kdm + alps and GKI symvers. The KDM-only batch needs no BTF base, and the script fails if
   one appears.
3. Runs `bulk-build.sh`, the unchanged strict `verify.py` with full ledgers, and `mutation-test.py`.

Stock operands are a read-only flat copy of the 12 targets. That copy was taken from a private copy of all 471
stock occurrences, verified identical to canonical.

| Check | B1 | B2 | B1 vs B2 |
|---|---|---|---|
| object / native / module exit | 0/0(skipped)/0 | 0/0(skipped)/0 | — |
| provider witnesses | 39/39 | 39/39 | identical objects |
| whole-file acceptance | 12/12 | 12/12 | identical normalized hashes |
| ELF mutation controls | 162/162 | 162/162 | — |
| raw + stripped .ko (24 files) | — | — | byte-identical |
| intermediate objects (221) | — | — | byte-identical |
| vendor `.config` (b826d842) | — | — | identical |
| natural provider symvers (39) | — | — | identical |
| batch Module.symvers | — | — | identical after mapping the absolute workspace path |
| assembled KDM tree / target source tree | 5bd6f968 / 0a404b5f | same | equal to `reference/` |

B1 outputs and intermediates are also identical to development D3 and D1.
