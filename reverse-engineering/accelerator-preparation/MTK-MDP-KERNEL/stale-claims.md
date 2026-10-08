# Stale-claim corrections — MTK-MDP-KERNEL

Corrections produced by the measured reconstruction. The preparation material is otherwise
preserved as-is; these entries supersede it where they conflict.

## 1. Donor choice: the first-listed candidate is wrong for `mtk-mml.ko`

`source-candidates.tsv` listed the NothingOSS `957dac185efe…` tree first for all four
modules. Measured against the ALPS release `5e415e059253…` that actually reproduces stock:

| module | `957dac` inputs vs. stock source | verdict |
|---|---|---|
| `clk-mt6878-mdpsys.ko` | `clk-mt6878-mdpsys.c` identical | either donor works |
| `mdp_drv_mt6878.ko` | all 13 compiled objects' sources identical (only the unrelated `mdp_mt6897.c` differs) | either donor works |
| `mtk-mml-mt6878.ko` | `mtk-mml-tp-mt6878.c` identical | either donor works |
| `mtk-mml.ko` | **18 of the 31 compiled objects' sources differ** | `957dac` is NOT the stock source |

The 18 differing files behind `mtk-mml.ko`: `mtk-mml-aal.c`, `mtk-mml-color.h`,
`mtk-mml-core.c`, `mtk-mml-core.h`, `mtk-mml-dle-adaptor.c`, `mtk-mml-driver.c`,
`mtk-mml-driver.h`, `mtk-mml-drm-adaptor.c`, `mtk-mml-drm-adaptor.h`, `mtk-mml-fg.c`,
`mtk-mml-hdr.c`, `mtk-mml-pq-core.c`, `mtk-mml-pq-core.h`, `mtk-mml-rdma.c`,
`mtk-mml-rrot.c`, `mtk-mml-rsz.c`, `mtk-mml-tdshp.c`, `mtk-mml-wrot.c`.
(`mtk-mml-mmp.[ch]` and `mtk-mml-tp-mt6989.c` also differ but are not compiled into the
shipped module.)

`957dac` is still required — for the vendor `Kconfig` and `mgk_64_k61_defconfig` — but not
as source. The patched local worktree `ca8b550b75e8` was not used at all.

## 2. "0 modules have existing published function/data evidence" — now superseded

`STATUS.md` and `stock-modules.tsv` carried `published_parity = UNKNOWN / no measured
target rebuild parity located` for all four modules. That is now replaced by a measured
result: all four rebuild byte-identically except their GNU build IDs, with complete
function/data/section/relocation/ABI ledgers.

## 3. Counting conventions in `stock-modules.tsv`

The preparation's per-module counts were re-measured. Matching exactly: functions
(3 / 644 / 695 / 5), imports (7 / 223 / 249 / 15), relocations (82 / 13 581 / 36 717 / 209),
`kcfi_abs_ids` (0 / 8 / 0 / 26). Two columns differ by counting convention, not by fact:

* `data_symbols` for `mtk-mml` was listed as 1000; the acceptance ledger records **996**
  distinct `(section, offset, name, size)` data objects. The difference is duplicate
  symbol entries that address the same object.
* `exports` for `mtk-mml` was listed as 32 (positional `__ksymtab` pairing). The
  authoritative count read through `__crc_<name>` inside `__kcrctab`/`__kcrctab_gpl` is
  **36** (31 GPL + 5 plain), and the ledger is asserted complete against the total
  `__kcrctab*` size. 36 is correct; 32 under-counts exported data objects.

## 4. "Keep generic CMDQ outside this component" — confirmed, with one nuance

Correct, and unchanged: `mtk-cmdq-drv-ext`, `cmdq-platform-mt6878` and `cmdq-sec-drv` are
not owned here. The nuance is that `cmdq_helper_inf.ko` is built **from a file inside the
MDP directory** (`drivers/misc/mediatek/mdp/cmdq_helper_inf.c`) yet is a separate module
with its own owner; this component deliberately builds it only in the provider-witness
scope, never ships it. Secure CMDQ is compiled out of `mdp_drv_mt6878`
(`CONFIG_MTK_MDP_MTEE_SUPPORT` unset ⇒ no `CMDQ_SECURE_PATH_SUPPORT`), so the GZ-TZ
boundary is not merely "kept separate" — it is absent from the shipped module.

## 5. "MDP/MML … RDMA, resizer, WROT, color/HDR/AAL/TDSHP and mutex/config blocks" — refined

Accurate, but the DT shows two *distinct* paths in the same island, which the preparation
did not separate: the **MML path** (mutex0, rdma0, hdr0, aal0, rsz0, tdshp0, wrot0, plus
the `dli0_sel`/`wrot0_sel` sub-components — component ids 1–10, `topology = "mt6878"`) and
the **legacy MDP path** (`/mdp`, `mdp_mutex0`, `mdp_rdma1`, `mdp_rsz1`, `mdp_wrot1`,
`mdp_color0`). They share the MDPSYS clock provider (12 gates) and the GCE, but use
different mailbox channels (16–19 vs 20–21) and different drivers. See
[hardware-contract.md](hardware-contract.md).

## 6. "mdp_drv … load_phase first-stage" — confirmed and extended

`mdp_drv_mt6878.ko` is at line 72 of `modules.load`; the other three are at 30, 73 and 74,
and all four also appear in `modules.load.recovery`. `cmdq_helper_inf.ko` immediately
precedes them (line 71) and the display stack follows (lines 78–81). Load *order* is
therefore established; **probe success is not**, and no runtime evidence of either driver
binding exists.

## 7. No firmware claim should be attached to this component

Neither module loads firmware. The `-fw` objects inside `mtk-mml.ko` are compiled
coefficient code, not a downloadable image. See [firmware-boundary.md](firmware-boundary.md).
