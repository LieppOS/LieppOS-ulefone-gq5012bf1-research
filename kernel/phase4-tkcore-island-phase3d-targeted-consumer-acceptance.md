# GQ5012BF1 tkcore Phase 3D — targeted consumer edge acceptance

Scope-limited on purpose. This is **not** the final three-consumer acceptance,
which stays deferred to Phase 3E together with todo #18.

Only the edges belonging to the four newly closed exports were examined, and
every consumer was treated as read-only.

## Edge results

| Consumer | Edge | Consumer CRC | Island provider CRC | Classification |
|---|---|---|---|---|
| `tkcore_drv` (frozen stock) | `tee_clkmgr_handle` | `0x6913f6b2` | `0x6913f6b2` | **NATURAL** |
| `tkcore_drv.stockabi` (shipped) | `tee_clkmgr_handle` | `0x6913f6b2` | `0x6913f6b2` | **NATURAL** |
| `microarray_fp_tee` (frozen stock) | `tee_spi_transfer` | `0x184ce7da` | `0x184ce7da` | **NATURAL** |
| `microarray_fp_tee.recon-stockabi` | `tee_spi_transfer` | `0x184ce7da` | `0x184ce7da` | **NATURAL** |
| — | `tee_spi_cfg_padsel` | — | `0x56729869` | NO_STOCK_CONSUMER_FOUND |
| — | `tee_spi_transfer_disable` | — | `0xadb9b21c` | NO_STOCK_CONSUMER_FOUND |

No edge is `HISTORICAL_STOCK_WITNESS` and no edge is `BLOCKED`.

## What changed for the frozen consumers

Nothing. Neither `tkcore_drv` nor `microarray_fp_tee` was rebuilt, re-linked,
re-spelled or edited. Their existing `__versions` records already name the CRCs
the island now produces naturally, which is exactly the required outcome:

- `microarray_fp_tee`'s single tkcore runtime witness (`tee_spi_transfer`) is
  now satisfiable by a **NATURAL_TKCORE_PROVIDER** edge;
- `tkcore_drv`'s `tee_clkmgr_handle` witness is likewise naturalisable.

Both were achieved without touching consumer source, so the §25 and §26 stop
conditions were not triggered.

## Techniques explicitly not used

No CRC injection, no `__versions` editing, no `__kcrctab` editing, no fake
`Module.symvers`, no ELF patching, no export-name fabrication.

## Still deferred

`workspace/phase4-tkcore-island/acceptance/` remains empty. Full `tkcore_drv`,
`tmem_ffa` and `microarray_fp_tee` natural-link acceptance is **not** claimed
and must not be, because five stock functions remain unimplemented.
