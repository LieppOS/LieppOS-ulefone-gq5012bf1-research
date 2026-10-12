# Stock inventory

`STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py` (unchanged) results:

| Point | Result | Identities | Occurrences | Signature census |
|---|---|---:|---:|---|
| Stage A integration worktree | PASS, 0 errors | 458 | 471 | 60 signed system_dlkm (721-byte), 196 vendor_boot, 215 vendor_dlkm |
| Stage B owner worktree | PASS, 0 errors | 458 | 471 | same |
| live canonical after fast-forward | PASS, 0 errors | 458 | 471 | same (see `evidence/live-post/`) |

- The sha256 list of all 471 stock `.ko` (canonical and the reflink copies in both private worktrees) equals the
  list recorded before KDM-INTEGRATION-01.
- No stock file was written, stripped or re-signed. Every comparison used read-only operands.
- Both distinct `bluetooth.ko` identities (`2df021ea…`, `d2659fb3…`) are kept.
- No stock identity field (`stock_sha256`, `stock_size`, `filename`, `stock_paths`, `partitions`) changed for any
  of the 458 rows in either stage.
