# Independent reproduction and resource limits

Three committed maintained engines ownSLBC1, modem9 and shared infrastructure12. `scripts/prove-fresh-builds.py` recovers each exact tip from its Git bundle into separate B1/B2 clones, runs full `git fsck`, rejects Git alternates and bootstraps immutable source/toolchain/config inputs. It renames only this task's three original repositories and three development workspaces out of their original paths for **all six builds**, restoring them in `finally`. Other agents' paths and shared mirrors are never hidden or edited.

The full source/module/object files are actually hashed, not just SHA text compared. Raw `.ko`, stripped `.ko`, all provider/target/native intermediate objects, assembled target tree, configuration, core GKI symvers and all joint ABI CRC/license/namespace/source-relative producer records must agree. Raw symvers text and authentic hashes are retained; only absolute producer workspace spelling is resolved in comparing ABI records, not ELF/CRC acceptance.

Per build, the unchanged strict verifier must accept20 complete stock modules with only the structural20-byte GNU build-ID descriptor different and must reject the two natural C BTF helpers. Their separate residual diagnosis must prove every other byte/layout identical and type/string-reference bijections without rewriting BTF. This is a negative expectation, not an A/B normalization.

Actual mutation controls include original/GNU20 positives and code, data/rodata, CRC, `.modinfo`, raw relocation, symbol table, KCFI prefix, ELF layout, appended signature-trailer and BTF corruption negatives. Stock originals are SHA-verified and read-only; mutated temporary copies alone are edited. Current unmodified C helper outputs must remain strict rejections.

## CPU policy requested by the user

All continuing builds run with **four jobs, hard four-core affinity and nice10**. Affinity/priority apply to git/tar/clang/make/pahole children as well as compilation. Each source engine defaults to four jobs, including modules_prepare. Large pin-file hashes stream at Git's1MiB big-file threshold without changing the expected tree identity. No other agent's process was reprioritized or killed.

The first independent proof completedSLBC B1/B2, then stopped when a toolchain pin-check Git process was killed. Failure logs/outputs are preserved under `evidence/independent-proof/`; all originals were restored. The final low-CPU proof starts in a new unused root and does not reuse those compiled objects.

## Artifact locations

- Final six-run actual results: `evidence/independent-proof-pathmaps/result.json`.
- Complete reports/config/ABI/object manifests/mutations: `evidence/independent-proof-pathmaps/{slbc,modem,shared}-{B1,B2}/`.
- Actual workspaces: `/home/armol/kernel-work/codex-audio-dependencies-batch-02/independent-proof-{low-cpu,pathmaps}/`.
- The first low-CPU attempt passes all raw/stripped modules but rejects26 preparation/tool objects with workspace-specific debug/__FILE__ paths. Its failure and actual objects remain preserved. Shared engine HOSTCFLAGS/KAFLAGS/KCPPFLAGS_COMPAT now map paths during compilation, never by postprocessing. Only its changed B1/B2 builds are rerun; the four unchanged SLBC/modem records are rehashed from every actual original file/source/config/ABI and retained, not relabelled as newly built.
- Git recovery bundles: `evidence/bundles/`, with committed tips and SHA in SOURCE-REPOSITORIES.tsv.
- Development successes/failures: `evidence/{slbc,modem,shared}-development/`.

Reproduction command (requires a new unused proof root if already completed):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/prove-fresh-builds.py
```

The current fixed proof path intentionally refuses to replay an existing build as new proof. Source/toolchain snapshots are offline/read-only inputs. No stock or original partition image, phone, firmware, experimental module load, live canonical audit or remote repository is modified.
