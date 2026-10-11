# Inventory validation

Checker: `STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py` (expectations from committed
f61ebf03 blobs only).

| Operand set | Result | Identities | Occurrences | system/vendor/boot | Signed system_dlkm |
|---|---|---:|---:|---|---:|
| Private integration worktree | PASS, 0 errors | 458 | 471 | 60/215/196 | 60/60 |
| Replay 1 / Replay 2 | PASS, 0 errors | 458 | 471 | 60/215/196 | 60/60 |
| Live canonical before restoration | FAIL, 180 errors | 458 | 471 | 60/215/196 | 0/60 |
| Live canonical after restoration | PASS, 0 errors | 458 | 471 | 60/215/196 | 60/60 |

Unchanged audit validator: PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES, 0 errors, 458 distinct
identities, 471 occurrences, 457 filenames at f61 (private), after stages 2–3, after 4+5, after 6,
after finalization and in both replays. Both bluetooth.ko identities remain distinct rows.
