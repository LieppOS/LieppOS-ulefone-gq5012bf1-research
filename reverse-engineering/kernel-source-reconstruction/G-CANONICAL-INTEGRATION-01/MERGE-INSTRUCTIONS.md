# Merge record and replay instructions

Both stages were applied to canonical by fast-forward only, after confirming canonical was clean, unlocked and at
the expected parent.

| Step | Commit | Parent |
|---|---|---|
| Stage A merge (research history) | c9f1ad50 | 0390534d + claude/remaining-kernel-source-batch-01 |
| Stage A CAS | e66cfcf7 | c9f1ad50 |
| Stage B merge (Codex history, package only) | 6f67a4bf | e66cfcf7 + codex/g-source-recovery-batch-01 |
| Stage B CAS + this package | see `git log` on master | 6f67a4bf |

## To replay on a different base

1. `git worktree add -b owner/g-source-replay <ROOT>/ulefone-gq5012bf1-research-owner-g-source-replay <HEAD>`.
   The helper only accepts worktree names starting with `ulefone-gq5012bf1-research-owner-g-source`.
2. Reflink-copy `workspace/gq5012bf1` and `kernel/nothing-module-index.csv` from canonical, and verify the 471
   sha256 list.
3. Merge `codex/g-source-recovery-batch-01` (no audit change).
4. Dry run:
   `python3 reverse-engineering/kernel-source-reconstruction/G-SOURCE-RECOVERY-BATCH-01/scripts/reconcile-owner.py <D> --expected-head <HEAD> --report <dir>/plan.json`.
   Conflicts or protected newer A/B rows stop the run; review them before continuing.
5. Run again with `--apply`, then restore the "Completed integration" queue header and append the batch.
6. Rerun the validator, `test_validate.py` and the inventory check.

Do not merge `codex/g-source-audit-proposal`: it carries a full-audit snapshot from ee1803b7. Nothing was pushed.
