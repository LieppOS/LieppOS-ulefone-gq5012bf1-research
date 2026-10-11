# Deterministic owner-ready integration — never apply to a competing checkout

This is a validated staging branch, not authorization to change canonical master. Do not push or touch the phone. Wait for Claude's Category-C closure and any PLATFORM-BATCH-05 activity to finish. All scripts default to dry-run or operate only on private worktrees; owner CAS/installer explicitly refuse canonical and the Category-C worktree.

## 1. Record current owner state

From the canonical research repository (read-only):

```sh
ROOT='/home/armol/androido_dalykai/LieppOS custom ROM'
C="$ROOT/ulefone-gq5012bf1-research"
H=$(git -C "$C" rev-parse HEAD)
I=$(git -C "$C" rev-parse codex/completed-batches-integration)
git -C "$C" status --porcelain
git -C "$C" worktree list
```

Stop if an agent is still writing/committing in the intended destination. Record actualH/I; do not replaceH with f61 or reset any branch. Inspect newer A/B source certifications, C evidence/source-owner updates, source repository HEADs and PLATFORM-BATCH-05 rows. Final target counts are recomputed from exact identities;302/156 is the recorded f61 staging result only.

## 2. Restore shared stock only through its owner

If shared copies still differ, follow the preserved STOCK-INVENTORY-INTEGRITY/MERGE-INSTRUCTIONS.md dry-run/image authentication/quarantine/apply procedure. It repairs only exactly signature-stripped occurrences and rejects other damage before writing. Only the owner, after quiescing users, may repair the canonical shared path. Never change expected SHA/size, copy a rebuilt module under a stock name or strip signatures for comparison.

This task did not restore that path. Owner can validate a new private worktree against the existing authenticated immutable dataset before live repair; live canonical integration still requires a passing actual live inventory.

## 3. Create a new owner-only private staging worktree at CURRENTH

```sh
D="$ROOT/ulefone-gq5012bf1-research-owner-integration"
git -C "$C" worktree add -b owner/completed-batches-final "$D" "$H"
P="$ROOT/ulefone-gq5012bf1-research-codex-integration/reverse-engineering/kernel-source-reconstruction/COMPLETED-BATCHES-INTEGRATION-01"
export PYTHONDONTWRITEBYTECODE=1 JOBS=4
python3 "$P/scripts/install-packages.py" "$D" --commit "$I" --report /home/armol/kernel-work/owner-package-plan.json
# inspect report: every differing existing research file must be reconciled first
python3 "$P/scripts/install-packages.py" "$D" --commit "$I" --report /home/armol/kernel-work/owner-package-install.json --apply
```

Installer recovers committed blobs, preserves every already-identical file and **aborts before writes on any different existing package file**. It never installs a stale audit. Preserve both investigations if Claude/owner already changed research under an original package; substantive overlap is an owner decision, not a forced merge/overwrite.

## 4. Supply authentic PRIVATE operands and baseline inputs

PopulateD's exact stock paths with separate reflink/read-only copies from the verified restored dataset; never symlink the whole stock tree to damaged canonical files. Copy the exact partition load lists. Verify every458 identity/471 occurrences and60/215/196 partition counts using the unchanged integrity checker. Git-ignored historical research/saved offline capture inputs may be aliased only after comparing their already-committed workspace/review-input hashes. Do not run a new ADB capture.

For the original recorded baseline, `scripts/prepare-private.py` is the tested setup implementation for the dedicated integration worktree; it deliberately refuses a different canonical HEAD. Do not rerun it blindly against a newer owner baseline. Use its explicit471-copy/hash/read-only logic and the new current baseline assertions, or reuse the existing authenticated private dataset with the owner's reviewed copying procedure. Saved `evidence/private-stock.json` enumerates actual sources/hashes.

```sh
python3 "$D/reverse-engineering/kernel-source-reconstruction/STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py" "$D" --json /home/armol/kernel-work/owner-inventory.json
(cd "$D/reverse-engineering/kernel-source-parity-audit/scripts" && python3 validate.py && python3 test_validate.py -v)
```

All six maintained source repositories must have the reviewed commits/bundles/config/patch/donor pins available. Do not checkout/reset an active source repo. If its newer legitimate tip changes evidence files, recover the old tip to a new private source clone or review a new successful source delta; update references only with proof. Stop on a baseline input/hash/audit failure, not a waiver.

## 5. Owner CAS dry run, then apply inD only

```sh
python3 "$P/scripts/reconcile-owner.py" "$D" --expected-head "$H" --report /home/armol/kernel-work/owner-CAS-plan.json
# review changed fields, protected newer A/B identities and conflicts
python3 "$P/scripts/reconcile-owner.py" "$D" --expected-head "$H" --report /home/armol/kernel-work/owner-CAS-result.json --apply
```

Planner checks exact identity/SHA/size and every source-owned field. Identical prior application is idempotent. Newer validated A/B entire identities are protected (no A/B→C demotion and no older source/parity-owner metadata overwrite). Other changed C/source-owner/JSON fields stop before target writes; preserve Claude's newer proof and explicitly reconcile. Unselected395 rows at f61 remain untouched; on newer baselines the same exact63 selection remains narrow.

Apply regenerates current ownership/gaps/projects/queue/summary/hash artifacts using the same tested staging derivative function, runs unchanged validator and14 mutation tests, and checksH did not advance. It does not force302 counts, does not change stock definitions and does not commit/push automatically. Original actual63-target proof remains traceable; repeat full source builds only for missing/invalid/changed input evidence.

## 6. Validate, preserve, commit; live integration is a separate owner decision

Run inventory checker again, validator/mutations, all source/bundle checks, targeted row diff and package preservation/overlap review. Record current and resulting class counts, any protected Claude A/B identities and all resolutions. Ensure source proofs are for the exact chosen tips; six C obligations cannot be silently waived.

Commit only validated privateD audit+research, keeping original detailed packages and raw logs/symvers empty namespace columns verbatim. At quiescent current canonical HEAD, the owner may merge/cherry-pick a freshly reviewed integration. **Do not unconditionally merge the original f61 staging audit over newer master**: its clean validated output is a reference, whereas the narrow CAS/replayed owner commit preserves new work. If canonical advances meanwhile, repeat the dry-run at a new private worktree; never reset/rebase Claude.

Actual tested replay: fresh f61 private worktree applied1063 CAS fields,14 tests passed, resulting ALL table byte-identical to staging. `evidence/owner-replay.json/log`, `owner-reconciled-audit.json`, `owner-mutations.log` and9 CAS mutation cases demonstrate this procedure.

Committed-blob installer also tested independently:1475-file dry-run/install PASS; a synthetic differing research-file overlap is rejected before any writes (all1475 hashes unchanged). Reports installer-dry-run.json, installer-apply.json and installer-overlap-rejection.json preserve the exact tested commit.

No flash/reboot/slot switch/module load/firmware or image edit follows from kernel source certification.
