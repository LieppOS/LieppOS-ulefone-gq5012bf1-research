# GQ5012BF1 tkcore Phase 3D — full export consumer scan

Scope: every `.ko` in the research repository — **620 files scanned**, covering
the stock vendor-ramdisk population and every reconstructed/acceptance build.
The known consumer set was *not* assumed complete.

## Results

| Export | Placements | Distinct binaries | Consumers |
|---|---:|---:|---|
| `tee_clkmgr_handle` | 5 | 3 | `tkcore_drv` |
| `tee_spi_transfer` | 7 | 5 | `microarray_fp_tee` |
| `tee_spi_cfg_padsel` | 0 | 0 | **NO_STOCK_CONSUMER_FOUND** |
| `tee_spi_transfer_disable` | 0 | 0 | **NO_STOCK_CONSUMER_FOUND** |

No consumer outside `tkcore_drv` and `microarray_fp_tee` imports any of the four.

## Per-consumer detail

### tee_clkmgr_handle

| Module | Placement | Load index | Imported CRC | Provider CRC | Verdict |
|---|---|---:|---|---|---|
| `tkcore_drv.ko` (stock) | `vendor-ramdisks/platform-extracted/lib/modules` | 101 | `0x6913f6b2` | `0x6913f6b2` | NATURAL |
| `tkcore_drv.ko` (stock, oracle copies) | `phase4-tkcore/oracle`, `phase4-tkcore-drv/oracle` | — | `0x6913f6b2` | `0x6913f6b2` | NATURAL |
| `tkcore_drv.natural.ko` | `phase4-tkcore-drv/build` | — | `0x6913f6b2` | `0x6913f6b2` | NATURAL |
| `tkcore_drv.stockabi.ko` (shipped) | `phase4-tkcore-drv/build` | — | `0x6913f6b2` | `0x6913f6b2` | NATURAL |

Call site: `call_tee`, one direct `R_AARCH64_CALL26`. No indirect/KCFI
expectation applies — the edge is a direct call.

### tee_spi_transfer

| Module | Placement | Load index | Imported CRC | Provider CRC | Verdict |
|---|---|---:|---|---|---|
| `microarray_fp_tee.ko` (stock) | `vendor-ramdisks/platform-extracted/lib/modules` | 127 | `0x184ce7da` | `0x184ce7da` | NATURAL |
| `microarray_fp_tee.stock.ko` | `phase4-fingerprint/oracle` | — | `0x184ce7da` | `0x184ce7da` | NATURAL |
| `microarray_fp_tee.recon.ko` | `phase4-microarray-fp-tee/build` | — | `0x184ce7da` | `0x184ce7da` | NATURAL |
| `microarray_fp_tee.recon-stockabi.ko` | `phase4-microarray-fp-tee/build` | — | `0x184ce7da` | `0x184ce7da` | NATURAL |
| `microarray_fp_tee.ko` | `phase4-spi-mt65xx/acceptance` | — | `0x184ce7da` | `0x184ce7da` | NATURAL |

Call sites: **five**, all inside `init_connect`, all direct calls. Stock KCFI
of the provider is `0xffeb18b3`, which the island reproduces exactly.

### tee_spi_cfg_padsel / tee_spi_transfer_disable

`NO_STOCK_CONSUMER_FOUND`. Both are retained and exported because **stock
tkcore exports them**; a provider that dropped them would not be ABI-complete.
Their correctness therefore rests entirely on the stock oracle, which is why
both were reconstructed to exact size and exact KCFI.
