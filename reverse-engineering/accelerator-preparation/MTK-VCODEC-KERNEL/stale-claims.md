# Stale claims corrected — MTK-VCODEC-KERNEL

Earlier statements in this pack that the completed reconstruction supersedes.

| Stale claim | Where | Correction (measured) |
|---|---|---|
| "Function/data state UNKNOWN / no measured target rebuild parity located" for all five modules | `parity-gaps.tsv` | All five rebuild byte-identically to stock except the 20-byte GNU build ID. See `RECONSTRUCTION-REPORT.md`. |
| "NOT ACCEPTED: full axes/B1-B2 closure not established" | `parity-gaps.tsv`, `STATUS.md` | Full axes closed and B1/B2 proven from a clean checkout. |
| Nothing-ROM donor `957dac18` listed as a *source candidate* for the five modules | `source-lineage.md`, `stock-modules.tsv` | It is **not** the stock source. Building it yields 37 differing functions in `mtk-vcodec-common`, size-differing functions in the encoder, and log-string/mutex differences absent from stock. The exact source is ALPS `5e415e059253`. `957dac18` is retained only for vendor Kconfig/defconfig. |
| The patched mixed workspace `kernel_device_modules-6.1` (`ca8b550b75e8`) as a candidate | `source-lineage.md` | Not needed and not used; no edited working tree participates in the recipe. |
| Export inventory of 58 symbols (`exports.tsv`) | `exports.tsv`, `kernel-abi.md` | Undercount: that table lists only exported **functions**. The true totals are 61 exports in `mtk-vcodec-common` and 14 in `mtk-vcu` (75), because exported **data** objects (module parameters such as `mtk_v4l2_dbg_level`, `mtk_vcodec_vcp`, `vcu_func`, `support_svp_region`, `support_wfd_region`) also carry `__kcrctab` CRCs. The authoritative ledger is `evidence/reconstruction/acceptance/abi-parity.tsv`. |
| Function/data inventories of 491/436 rows | `functions.tsv`, `data-symbols.tsv` | Superseded by the measured ledgers `function-parity.tsv` (491 rows) and `data-parity.tsv` (436 rows) which additionally carry section, offset, size and per-symbol hash with an explicit result column. |
| "`mtk-vcu` … VCU bridge … native/compat ioctls" presented as an active board interface | `kernel-abi.md`, `hardware-contract.md` (pre-closure) | The ioctl surface is real in the shipped binary, but **no node in the stock merged DTB matches any `mtk-vcu` OF alias**. Whether the VCU platform driver probes on GQ5012BF1 is UNKNOWN; the board's firmware path is VCP/TinySys. |
| Codec XML capability rows implying device codec support | `codec-capabilities.tsv` | Unchanged in status (`static declaration`), restated explicitly: the five `c2.mtk.*` hardware components are declarations only; no decode or encode was executed. |

## Still true after closure

* Signed VCP firmware and vendor Codec2/OMX libraries remain proprietary and unreconstructed.
* No runtime, hardware or throughput claim is made anywhere in this pack.
* Provider modules keep their existing owners; only their export ABI was verified here.
