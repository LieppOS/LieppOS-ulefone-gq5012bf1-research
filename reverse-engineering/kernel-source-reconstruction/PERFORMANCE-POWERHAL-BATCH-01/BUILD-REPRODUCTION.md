# Build reproduction

## Development (quarantined)

`/home/armol/kernel-work/performance-powerhal-batch-01/dev` was renamed to `quarantined-development` before the
proof. It was not deleted, and `prove-fresh.sh` refuses to run while the original path exists.

- **D1:** produced by `scripts/dev-kdm.sh`.
- **D3:** produced by the committed `bulk-build.sh` at repo 66aa137.

Logs, acceptance and provider ledgers are in `evidence/development/`.

## Independent proof (`scripts/prove-fresh.sh`)

`EXPECT_COMMIT=7a1a1e298a2a… prove-fresh.sh B1 56-59` and `… B2 60-63` ran in parallel, each at nice 10 with JOBS=4.
Each one:

1. Clones `bundles/performance.bundle` with `--no-hardlinks`. The clone is checked for the exact commit, no
   alternates, `fsck --full` and `bundle verify`.
2. Bootstraps a fresh workspace offline from the read-only `interconnect-pin-mirror`: common, clang
   (tree-hashed), kdm + alps5e41 (tree-verified) and GKI symvers.
3. Runs `bulk-build.sh`, which creates the vendor kout (`.config` b826d842) itself.
4. Runs the unchanged strict `verify.py` with full ledgers, then `mutation-test.py`.

The stock operands are a read-only flat copy of the 14 targets. That copy was taken from a private copy of all 471
stock occurrences, whose sha256 list is identical to canonical.

| Check | B1 | B2 | B1 vs B2 |
|---|---|---|---|
| object / native / module exit | 0 / 0 (none) / 0 | 0 / 0 (none) / 0 | — |
| provider witnesses | 98/98 | 98/98 | identical natural symvers |
| whole-file acceptance | 14/14 | 14/14 | identical normalized hashes |
| ELF mutation controls | 189/189 | 189/189 | — |
| raw + stripped .ko (28 files) | — | — | byte-identical |
| intermediate objects (197) | — | — | byte-identical |
| vendor `.config` | b826d842 | b826d842 | identical (only the absolute path differs in the list) |
| joint-extra / batch Module.symvers | — | — | identical, after mapping the workspace path for the batch file |
| assembled KDM tree / target source tree | dbfeac27 / 92fa0e65 | same | equal to `reference/` |

B1 outputs equal development D3 and D1 byte-for-byte. Total proof wall time was about 4 minutes per build.
