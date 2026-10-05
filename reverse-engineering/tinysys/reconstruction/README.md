# Reconstruction: exact rebuild recipe (no source changes)

## Sources

All sources are **unmodified MTK ALPS mt6878 `5e415e059253`** (NothingOSS history, pristine `git archive`). The exact files are in `exact-source/` with SHA-256s in `exact-source/SHA256SUMS`.

| file | git blob | sha256 (prefix) | last change in NothingOSS `nt6878.git` |
|---|---|---|---|
| `drivers/rpmsg/mtk_rpmsg_mbox.c` | `82ec9c50d3` | `557089af…` | `862ee5892ae4` 2020-06-04 "TinySys: Common MBOX/IPI revise" |
| `drivers/soc/mediatek/mtk_tinysys_ipi.c` | `1acca98c7c` | `6e2dafc6…` | `a5b60cb0092c` 2023-05-31 "[ALPS07693493] scp: chre: Return fake signal" |
| `include/linux/rpmsg/mtk_rpmsg.h` | `2e21c19cb1` | `0d480bb0…` | `7e1932aa3e6a` 2020-05-05 |
| `include/linux/soc/mediatek/mtk_tinysys_ipi.h` | `2205ab98d8` | `7d361b56…` | `a5b60cb0092c` |
| `include/linux/soc/mediatek/mtk-mbox.h` | `80ade10970` | `bcf03fa5…` | (MTK-MBOX scope) |

The MiCode `MTK_kernel_device_modules` mirror has later variants of both `.c` files on several branches. Each was built in the same harness and **rejected**; see `../kernel/parity/lineage-and-whole-file.txt`. No patch is needed: **DIRECT_SOURCE_MATCH**.

## Build

- **Kernel:** exact GKI 12901745 (`common/`, `O=lieppos/nfc/kout`), clang `r487747c`, `LLVM=1 LLVM_IAS=1`.
- **Harness:** `scripts/sb.sh` does an isolated `M=` build of one module from the full KDM tree, with:
  - `KCFLAGS=-faddrsig -fmacro-prefix-map=<tree>/=../kernel_device_modules-6.1/`. The second flag reproduces the stock `__FILE__` strings `../kernel_device_modules-6.1/drivers/...`; with it, `.rodata.str1.1` and `__bug_table` are exact.
  - `LINUXINCLUDE := -I<tree>/include $(LINUXINCLUDE)`. The vendor `include/linux/rpmsg/mtk_rpmsg.h` must win over GKI's same-named, same-guard header, which lacks `mtk_rpmsg_endpoint/_channel_info/_operations/_device`. This is the only reason earlier out-of-tree builds failed.
  - `KBUILD_EXTRA_SYMBOLS = stock-all.symvers` (CRCs of every shipped vendor export).
  - `llvm-strip --strip-debug` of the output. Stock modules carry no DWARF.
- **Commands:**
  - `scripts/build-all.sh B1`, which runs
  - `sb.sh trees/5e41 mtk_rpmsg_mbox drivers/rpmsg mtk_rpmsg_mbox.o B1` and
  - `sb.sh trees/5e41 mtk_tinysys_ipi drivers/soc/mediatek mtk_tinysys_ipi.o B1`.
- **Workspace:** `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/`. The tree `trees/5e41` is on branch `tinysys`, which is base commit `2ae742f` with **no commits on top**. The harness writes only git-ignored files: a generated `Kbuild`, objects and logs.

## Result

Stock and rebuilt modules are equal byte-for-byte after the 20-byte `.note.gnu.build-id` descriptor is transplanted. A clean second build (B2) is file-identical to B1.
