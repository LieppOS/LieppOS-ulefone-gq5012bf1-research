# microSD (MSDC1) kernel stack: exact reconstruction

## Modules (A = stock vendor_ramdisk, B = isolated rebuild, debug-stripped; B1==B2)

| module | functions | data | imports (CRC) | exports / CRCs | relocs | KCFI | sections | runtime role |
|---|---|---|---|---|---|---|---|---|
| `mtk-mmc.ko` | **59/59** | 71/71 | 117/117 | 0 | 897/897 | 59/59 | 44/44 except build-id | ACTIVE: MSDC1 SD host (`mediatek,mt6878-mmc`) |
| `mtk-mmc-dbg.ko` | **26/26** | 33/33 | 38/38 | 5/5 / 4 | 722/722 | 26/26 | 50/50 except build-id | ACTIVE: MSDC command history, `mmc_dbg_register` |
| `cqhci.ko` | **23/23** | 21/21 | 40/40 | 5/5 / 5 | 320/320 | 23/23 | 38/38 except build-id | LOADED, UNUSED: only MSDC0/eMMC has `supports-cqe`, and it is disabled |
| `mtk-wp.ko` | **4/4** | 24/24 | 15/15 | 0 | 108/108 | 4/4 | 39/39 except build-id | LOADED, INERT: `wp_boot1`/`wp_boot2`/`wp_user` are not set anywhere in the stock artifacts (empty vendor_boot bootconfig, no `modules.options`, absent from live `/chosen/bootargs`), so `wp_policy_init` returns 0. eMMC-only (`mmcblk0boot*`) |

The source for all four is MTK ALPS `5e415e059253` (`drivers/mmc/host/`), **unmodified**, built with the MTK KDM `CONFIG_MMC_MTK_PRO=m`, `CONFIG_DEVICE_MODULES_MMC_CQHCI=m` (+ `CONFIG_MMC_CRYPTO=y` → `cqhci-crypto.o`), `CONFIG_DEVICE_MODULES_MMC_DEBUG=m` and `CONFIG_DEVICE_MODULES_MMC_MTK_WP=m`. GKI `CONFIG_MMC=y`/`MMC_BLOCK=y` provide the core and block layer. `mtk-sd.o` (upstream-style) and `CONFIG_MMC_AUTOK` are **not** shipped.

Dependencies (from import provenance): `mtk-mmc` uses `cqhci`, `mtk-mmc-dbg`, `rpmb-mtk` (`mmc_rpmb_register`), `blocktag` (`mmc_mtk_biolog_*`) and `pinctrl-mtk-common-v2_debug` (`gpio_dump_regs_range`).

The board deltas are in DT only (card-detect polarity and VMCH variant): [`dt-contract.md`](dt-contract.md), [`../yft-storage-deltas.md`](../yft-storage-deltas.md). Protocol and lifecycle are in [`protocol.md`](protocol.md).
