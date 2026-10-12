# Stock inventory

| Check | Before (4e47a5b9) | After (integration) |
|---|---|---|
| verify-inventory.py | PASS, 0 errors, 458/471 | PASS, 0 errors, 458/471 |
| 471 stock `.ko` sha256 | snapshot `stock-operands.sha256` | byte-identical list |
| stock identity fields (sha256/size/filename/paths/partitions) of 458 rows | — | unchanged 458/458 |
| `bluetooth.ko` identities | 2df021ea…, d2659fb3… | both retained and distinct |

Partition occurrences: 60 signed system_dlkm, 215 vendor_dlkm, 196 vendor_boot. Stock files were read only. The
integration worktree used a reflink copy for validator input.
