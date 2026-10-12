# Owner integration procedure (narrow compare-and-swap)

Nothing in canonical master was edited. The canonical audit is unchanged on this branch. The proposal is:

- `AUDIT-DELTA.tsv`: 304 field rows over 16 identities. Each row has `expected_before` (canonical
  21ec8901) and `proposed_after`, and is keyed by module_id + stock SHA256 + size + path.
- `scripts/audit-delta.py`: the applier. It refuses the canonical checkout and stops before writing on any
  CAS/identity mismatch. It updates source-reviews / review-input-hashes for these 16 only, runs the reviewed
  `regenerate()` unmodified, restores the canonical queue header and runs the unchanged validator and the
  14 mutation tests.
- `PROPOSED-AUDIT.patch` (SHA256 `ecc89333…`): the exact resulting audit diff, produced in a disposable
  scratch worktree whose audit tree equals 21ec8901's. Scratch results are in `evidence/audit-scratch/`:
  validator PASS, 0 errors, A349 B1 C10 D44 E0 F0 G54, 458/471, mutations 14/14.

## Steps

1. Confirm canonical is idle, clean and still at `21ec8901` (`git status`, `git worktree list`, process cwd scan).
   If it advanced, rerun `audit-delta.py plan --canonical-base <new>`. Any changed `expected_before`
   for these 16 rows is a conflict to reconcile explicitly, never overwrite.
2. Source: `../android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` must be at
   `8e7a66e130a532972be636499e24bb72b302718c`, clean. If absent, clone `bundles/boot-dependencies.bundle`
   and check `git bundle verify` plus `fsck --full`. The input hashes of all its recipe files are recorded per row.
3. Stock: `STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py <canonical>` must PASS 458/471.
4. Merge this research branch (`codex/boot-dependency-batch-01`, new directory only). Then, in a private
   integration worktree (never canonical directly), with verified operands and `kernel/nothing-module-index.csv`
   (SHA256 06f48542…) in place:
   `python3 <branch>/…/BOOT-DEPENDENCY-BATCH-01/scripts/audit-delta.py apply <integration-worktree> --expected-head <its HEAD>`.
   The result must equal `PROPOSED-AUDIT.patch` when the base is 21ec8901.
5. Commit in the integration worktree, fast-forward canonical, then rerun the inventory, validator and
   `test_validate.py` live. No push.

The batch claims no runtime, flash, hardware or firmware behaviour, and makes no provider ownership change.
