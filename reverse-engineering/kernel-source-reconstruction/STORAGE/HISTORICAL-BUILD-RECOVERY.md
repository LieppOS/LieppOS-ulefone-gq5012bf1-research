# Historical build recovery

## What existed

| item | location | state on 2026-10-09 |
|---|---|---|
| research | `reverse-engineering/storage/` (inventory, per-module parity, DT, RPMB, patches) | intact, unchanged |
| DONE packs | `../../../Reverse Engineer - DONE/UFS-RPMB-KERNEL`, `.../MICROSD-KERNEL` | intact, unchanged |
| build scripts | `reverse-engineering/storage/scripts/{build-all,sb,rb,rfd}.sh` | reference absolute paths in the GKI workspace |
| build tree | `~/kernel-work/gki-12901745-workspace/lieppos/storage/trees/5e41` | git history `2ae742f` (pristine ALPS 5e41) → `650fef1` (0001) → `f751270` (0002); `sb.sh`-generated `Kbuild` files and `Kbuild.orig` in place |
| config inputs | `.../lieppos/storage/cfg/{mtk-ack/, gq5012bf1-no-trustonic.h, stock-all.ise.symvers}`, `.../lieppos/storage/stock-all.symvers` | present |
| kout | `.../lieppos/nfc/kout` (shared with other projects) | `.config` modified on 2026-10-07 |

## Why the historical result was exact

All ten preserved `*.stripped.ko` from 2026-10-05 00:55 in `trees/5e41` were re-normalized
(build ID zeroed) and compared with stock: **10/10 identical**. The historical proof
(`kernel/parity/full-module-proof.txt`: all sections equal except `.note.gnu.build-id`, B1 == B2)
is therefore genuine. The specific reasons for exactness, now each reproduced from source:

1. ALPS `5e415e059253` is the right vendor baseline for nine modules (unmodified source) and,
   with patch 0002, for `rpmb-mtk`.
2. `ufs-mediatek-dbg`: 69 additional source lines precede `ufs_mtk_eh_abort`; the stock
   `ufs_mtk_aee_warning` `__LINE__` immediates are 136/160/189 vs 67/91/120. Patch 0001 adds 69
   lines (text unrecoverable, count proven).
3. UFS modules: MTK's ACK adds `check_bus_status`/`dbg_dump` (under the off
   `CONFIG_MTK_UFS_DEBUG_BUILD`) to `struct ufs_hba_variant_ops` and helpers to
   `ufshcd-priv.h`; only line numbers move (stock `__bug_table` 1338/1328 vs 1333/1323).
4. `rpmb-mtk`: TrustKernel raw-frame ioctls 10–14, netlink off, multi-block constants, and
   `CONFIG_TRUSTONIC_TEE_SUPPORT` unset for this board (patch 0002 + board header).
5. `rpmb-mtk` `depends=ufs-mediatek-mod-ise,rpmb`.

## Hidden inputs found and their replacement

| hidden input | evidence | why it disqualifies A/B | replacement in the maintained recipe | proof of equivalence |
|---|---|---|---|---|
| mutable kout `lieppos/nfc/kout` | `.config` sha256 now `3e489f17…`, lacking every vendor `CONFIG_MTK_*`, `CONFIG_RPMB`, `CONFIG_TRUSTONIC*`; mtime 2026-10-07, two days after the storage build, while the historical note says that kout "sets Trustonic =m" | the config used on 2026-10-05 cannot be recovered from the tree | `make-kout.sh`: `gki_defconfig` + KDM 957dac `mgk_64_k61_defconfig`, `.config` sha256 `8f9d1d29…` asserted | all ten exact with it |
| `stock-all.symvers` (KBUILD_EXTRA_SYMBOLS) | `sb.sh` default `XSYMVERS` | provider CRCs copied from stock binaries | patch 0004 witness tree: genksyms CRCs from ALPS AEE, mrdump, irq-dbg, pinctrl debug sources; intra-group exports resolved in one modpost run | `derive-provider-crcs.sh`: 5/5 equal the stock `__versions` CRCs, each unique |
| `cfg/stock-all.ise.symvers` | `build-all.sh` case for `rpmb-mtk` | hand-edited attribution of one export | `drivers/ufs/vendor/Kbuild` builds both vendor variants, as the vendor Makefile does; modpost's symbol hash returns the most recently added exporter (`ufs-mediatek-mod-ise`) | `rpmb-mtk` exact incl. `depends=`; `ufs-mediatek-mod` stays exact although its objects now carry `KBUILD_MODNAME="ufs_mediatek_mod:ufs_mediatek_mod_ise"`, as in a natural vendor build |
| `cfg/mtk-ack/` headers | copied files | no provenance chain | `src/ack` = pinned GKI `include/ufs/ufshcd.h`, `drivers/ufs/core/ufshcd-priv.h` + `patches/ack/` | the regenerated files equal the historical overlay byte-for-byte; `ufshcd-priv.h` result = MTK ACK blob `91a665ca` (NothingOSS `android_kernel_6.1_nothing_mt6878` d6343dbbb3ea, and every other mt6878 branch head) |
| `cfg/gq5012bf1-no-trustonic.h` via `XCCFLAGS` | untracked | not part of a source recipe | `drivers/char/rpmb/gq5012bf1-board-config.h`, force-included by `CFLAGS_rpmb-mtk.o` in patch 0003 | identical directive text |
| `sb.sh` rewriting `$M/Kbuild` in place, with `Kbuild.orig` copies | per-run tree mutation | source tree differs from any commit | committed `Kbuild` wrappers (patch 0003), tree id `b4235376…` verified | — |
| per-module `M=` invocations | 10 separate modpost runs, each with stock symvers | — | one `M=<tree>` run rooted at the vendor tree, like the vendor Kleaf build | identical module bytes |
| `KCFLAGS` without `-D__ANDROID_COMMON_KERNEL__` | historical `.cmd` | — | the recipe uses the GKI Kleaf flag (as BOOT-CLOCK-CORE) | no compiled source or included header references the macro; output identical |

The historical scripts and configuration are left untouched as evidence. During the
independent run the historical storage directory was moved out of the way.

## Cross-checks of the MTK ACK header

`include/ufs/ufshcd.h` at NothingOSS `d6343dbbb3ea` (Tetris/u) lacks GKI's later
`suspend_on_no_request` field; the 6.1.124/6.1.162 branch heads differ elsewhere. No public
blob equals the stock layout, which is pinned GKI `6b18f0b574ab` **plus** the MTK debug-vops
hunk. That composite is what the stock line numbers require, and it is what `src/ack` builds
(`81cf58bb…`).
