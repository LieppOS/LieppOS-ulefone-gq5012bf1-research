# Owner integration: tmem_ffa C→A (narrow CAS)

Canonical was **not** modified by Stage C.

## The proposal

| | |
|---|---|
| `AUDIT-DELTA.tsv` | 14 field rows for `tmem_ffa.ko@707e2667…` against canonical `4e47a5b9` |
| `PROPOSED-AUDIT.patch` | sha256 `80fff24e…`; scratch validator PASS, 0 errors; **A421 B1 C10 D3 E0 F0 G23 = 422/458**; 14/14 audit mutations; inventory 458/471; all 457 other rows byte-identical (`evidence/audit-scratch/invariants.txt`) |
| Applier | `scripts/audit-delta.py`: the reviewed display applier adapted for the C→A identity; it refuses canonical and the research worktree |

## Ownership note for the owner

The row's `source_group`/`source_owner` moves from `G-SOURCE-RECOVERY-BATCH-01:NORMAL-WORLD-SECURE-TRANSPORT`
(completed and integrated; it left tmem_ffa C) to `OEM-SOURCE-GAP-CLOSURE-01:TRUSTKERNEL-ABI`. The new
`source_repo` is the fork, `../android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1`. Codex's secure_transport
repository and its eight A rows are unchanged.

**Alternative:** if the owner prefers to keep a single repository, fast-forward secure_transport to fork commit
`9ee50d3` + `15e7e8d` instead. Both are descendants of 00929490, so no rewrite is needed. Then rerun `plan` with
the adjusted REPO.

## Steps

1. **Check canonical** is clean and idle. If HEAD ≠ `4e47a5b9`, rerun `audit-delta.py plan --canonical-base <new>`
   and treat any changed `expected_before` as a conflict.
2. **Check the fork repo:** `../android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1` must be at
   `15e7e8d8d4f9cbf56982791b2fac0e54087d0f49` and clean. If it is absent, clone `bundles/trustkernel-abi.bundle` and run `bundle verify`.
3. **Apply in an integration worktree:** merge `claude/oem-source-gap-closure-01`, run `audit-delta.py apply
   <worktree> --expected-head <HEAD>` from the research worktree, and require the diff to equal
   `PROPOSED-AUDIT.patch`.
4. **Land it:** move the scratch output into the integration package, commit, fast-forward canonical. Rerun the
   validator, `test_validate.py` and the inventory check live. Do not push.
