# Integration plan (as executed)

| Stage | Input | Method | Gate |
|---|---|---|---|
| 0 Preflight | worktrees/branches/processes | read-only | canonical clean at f61ebf03; no active writer; no PLATFORM-BATCH-05 |
| 1 Baseline | f61ebf03 | private worktree `ulefone-gq5012bf1-research-canonical-integration`, operands from verified private dataset | verify-inventory PASS; validator PASS A244/B1/C14/D91/G108; 14/14 |
| 2+3 Staged batches | 55dab18a ⊂ 437ebd57 | `merge --ff-only` (canonical unchanged since their base) | validator PASS A323/B1/C20/D60/G54; 14/14 |
| 3b History | f00bd8af, 40bfedda, fb558640, 143a6db2 | `merge --no-ff`, assert tree unchanged | tree adcdf7de unchanged ×4 |
| 3c Research | 7e196c32, 652e4195 | `merge --no-ff` (new directories only) | audit unchanged vs 437ebd57 |
| 4 ALL-C | 10 C→A | re-verify 196 acceptances + 258 ELF mutations; verify 4 bundles; fast-forward 4 maintained repos; CAS | see stage 4+5 |
| 5 Supersede | 32 A rows | CAS source_commit + appended reverify evidence; refreshed proof-input hashes for files inside fast-forwarded repos only | combined 4+5 validator PASS A333/B1/C10/D60/G54 |
| 6 USB | 22 fields / 5 C | original USB AUDIT-DELTA rechecked against 437ebd57 | validator PASS; class unchanged |
| 7 Narrative | SUMMARY.md / queue | `finalize-summary.py` (idempotent, anchors must match once) | validator PASS |
| 8 Replay | f61ebf03 → integration | `owner-replay.sh` ×2 | byte-identical |
| 9 Stock | canonical shared copies | STOCK-INVENTORY-INTEGRITY restore-operands.py dry-run → apply | dry-run == preserved plan; after PASS 458/471 |
| 10 Canonical | master | `merge --ff-only` integration branch, live validation | live validator PASS, 14/14, inventory PASS |

Scripts: `scripts/plan-canonical.py`, `apply-canonical.py`, `finalize-summary.py`,
`build-tables.py`, `owner-replay.sh`. Every expected value comes from committed blobs.
