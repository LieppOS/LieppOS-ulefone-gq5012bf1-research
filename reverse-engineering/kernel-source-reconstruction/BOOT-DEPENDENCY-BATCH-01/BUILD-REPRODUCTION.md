# Build reproduction

## Development (quarantined)

`/home/armol/kernel-work/boot-dependency-batch-01/dev` was renamed to
`.../quarantined-development` before the proof. It is not deleted or reused. `prove-fresh.sh` refuses to
run while the original path exists. Development logs and outputs (D1, D2, D3) are preserved in `evidence/development/`.

## Independent proof (`scripts/prove-fresh.sh`)

- **Run:** `EXPECT_COMMIT=8e7a66e1… prove-fresh.sh B1 56-59` and `… B2 60-63`, in parallel.
  Each runs at nice 10 with `JOBS=4` on its own four-CPU set.
- **Fresh source:** each tag starts from a `--no-hardlinks` clone of `bundles/boot-dependencies.bundle`
  (SHA256 in SOURCE-REPOSITORIES.tsv). The clone must be at the exact commit, have no alternates, and pass
  `fsck --full` and `bundle verify`.
- **Fresh workspace:** each tag gets a new workspace with an offline bootstrap of every pin: common,
  clang (tree-hashed), kdm + alps, GKI symvers, kernel-build-tools/pahole, GKI vmlinux and MTK ACK. The
  OEM split-BTF base is rebuilt from source (`.BTF` `cafe5987…` in both).
- **Build and checks:** then `bulk-build.sh`, the unchanged strict `verify.py` (full ledgers) and
  `mutation-test.py`.
- **Inputs:** offline mirrors are read-only (`interconnect-pin-mirror`, `platform-batch-03-native-inputs`,
  `allc/mirror`). Stock operands are a read-only flat copy of the 16 targets. That copy is taken from a
  private copy of all 471 occurrences, verified identical to the canonical tree.

| Check | B1 | B2 | B1 vs B2 |
|---|---|---|---|
| object / native / module exit | 0/0/0 | 0/0/0 | — |
| provider witnesses | 66/66 | 66/66 | identical witness objects |
| whole-file acceptance | 16/16 | 16/16 | identical normalized hashes |
| ELF mutation controls | 222/222 | 222/222 | — |
| raw + stripped .ko (32 files) | — | — | byte-identical (`SHA256SUMS`) |
| intermediate objects (189: KDM targets + witnesses + native) | — | — | byte-identical |
| prepared configs (vendor b826d842, native) | — | — | identical |
| natural provider symvers (66) / native Module.symvers (7999) | — | — | identical |
| batch Module.symvers | — | — | identical after mapping the absolute workspace path in the producer column |
| assembled KDM tree / target source tree | 14ca2d63 / c59256fa | same | equal to `reference/kdm-tree.txt` / `target-tree.txt` |

B1 raw/stripped outputs and intermediates are also identical to development D3.

Failed attempt preserved: `evidence/failed-proof-01`. Bundle verification was run outside a repository,
so it failed before any build. Fix: verify inside the fresh clone.
