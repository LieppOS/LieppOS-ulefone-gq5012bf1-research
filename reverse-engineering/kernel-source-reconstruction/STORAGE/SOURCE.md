# PRESERVE:STORAGE — where the source is

## Maintained source repository

**`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_storage_ulefone_gq5012bf1`**

* Branch `main`, commit **`e9b29f3086e5de26a71f3d6b87b25d1cf6ce61de`**.
* No remote configured; not pushed. Intended remote:
  `git@github.com:LieppOS/android_kernel_modules_storage_ulefone_gq5012bf1.git`.
* Redundant copy: `source/android_kernel_modules_storage_ulefone_gq5012bf1.bundle`
  (`git clone <bundle>`), with plain copies of `SOURCE-PINS.tsv` and `patches/`.

Pins + complete patches + scripts + reference hashes. No upstream tree, stock binary,
firmware, RPMB data or key.

## Exact revisions (verified by git tree id on every bootstrap)

| id | repository | commit | tree | licence |
|---|---|---|---|---|
| common | https://android.googlesource.com/kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` | GPL-2.0 |
| clang | https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86 | `7775eb113f960bc69a780b621d03a715914d4bca` | `clang-r487747c` = `8eb8e3afb00a52d48b29381d73daf352362231ad` | Apache-2.0 WITH LLVM-exception (tool only) |
| kdm | https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878 | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` | GPL-2.0 (Kconfig/defconfig only) |
| alps5e41 | same | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | GPL-2.0 (all compiled source) |
| GKI vmlinux.symvers | ci.android.com 12901745 `kernel_aarch64` | — | sha256 `61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548` (xz in repo) | — |

Provenance only (not fetched; the hunk text is in `patches/ack/`): NothingOSS
`android_kernel_6.1_nothing_mt6878` `d6343dbbb3eaeaf4a2a52d6ef6a30501a09ea464` (tree
`6141bbf8d70592f13a3f74458e8d5bdeeabb71d1`, branch `mt6878/Tetris/u`), whose
`drivers/ufs/core/ufshcd-priv.h` blob `91a665ca…` equals the regenerated overlay file.

## Source files compiled (all from alps5e41)

| module | sources | Kconfig in the vendor kout |
|---|---|---|
| ufs-mediatek-mod | `drivers/ufs/ufs-mediatek.c`, `-sysfs.c`, `-mimic.c`, `-btag.c`, `-rpmb.c`, `-ise-dummy.c` | `DEVICE_MODULES_SCSI_UFS_MEDIATEK=m`, `UFS_MEDIATEK_INTERNAL=y`, `MTK_BLOCK_IO_TRACER=m`, `RPMB=m` |
| ufs-mediatek-dbg | `drivers/ufs/ufs-mediatek-dbg.c` | `SCSI_UFS_MEDIATEK_DBG=m` |
| phy-mtk-ufs | `drivers/phy/mediatek/phy-mtk-ufs.c` | `DEVICE_MODULES_PHY_MTK_UFS=m` |
| rpmb | `drivers/char/rpmb/core.c` (no `cdev.c`: `RPMB_INTF_DEV` unset) | `RPMB=m` |
| rpmb-mtk | `drivers/char/rpmb/rpmb-mtk.c` | `RPMB=m`, Trustonic forced off for this object |
| mtk-mmc | `drivers/mmc/host/mtk-mmc.c` | `MMC_MTK_PRO=m` |
| mtk-mmc-dbg | `drivers/mmc/host/mtk-mmc-dbg.c` | `DEVICE_MODULES_MMC_DEBUG=m` |
| cqhci | `drivers/mmc/host/cqhci-core.c`, `cqhci-crypto.c` | `DEVICE_MODULES_MMC_CQHCI=m`, `MMC_CRYPTO=y` |
| mtk-wp | `drivers/mmc/host/mtk-wp.c` | `DEVICE_MODULES_MMC_MTK_WP=m` |
| blocktag | `drivers/misc/mediatek/blocktag/blocktag-{mictx,core,earaio,ufs,mmc}.c` | `MTK_BLOCK_IO_TRACER=m`; FUSE/PM/FSCMD tracers unset |
| *ufs-mediatek-mod-ise* (build-only) | as ufs-mediatek-mod, with `ufs-mediatek-ise.c` | — |

## Patches (complete)

| patch | unit | change | origin |
|---|---|---|---|
| `0001-ufs-mediatek-dbg-69-line-layout-padding…` | src/kdm | `ufs-mediatek-dbg.c` +69 comment/blank lines | historical, verbatim |
| `0002-rpmb-mtk-GQ5012BF1-TrustKernel-raw-frame-RPMB-ioctls` | src/kdm | `rpmb-mtk.c` +129/−6 | historical, verbatim |
| `0003-owned-storage-module-build-scope` | src/kdm | top `Kbuild` (five owned dirs), six directory `Kbuild` wrappers, `drivers/char/rpmb/gq5012bf1-board-config.h` | new |
| `0004-provider-abi-witness-scope` | src/prov | top `Kbuild` + seven wrappers (AEE, mrdump, irq-dbg, ise_lpm, pinctrl debug, iSE mailbox) | new |
| `ack/0001-ufshcd-h-mtk-debug-vops`, `ack/0002-ufshcd-priv-h-mtk-debug-vops` | src/ack | MTK ACK hunks on copies of the pinned GKI headers | historical, verbatim |

Result trees: `src/kdm` `b42353768078f1437b16a2067bf6ff37a918ce3a`,
`src/prov` `fab4a8c9213d2f11637628aa831eae43661b573e`,
`src/ack` `62468bc1…` → `61f09c46b5503dd2da487a6bc0bd097067ed77cc`.

## Device-specific differences from public source

1. `ufs-mediatek-dbg.c`: 69 unknown lines before `ufs_mtk_eh_abort` (count proven, text not).
2. `rpmb-mtk.c`: TrustKernel raw-frame ioctl ABI (reconstructed ODM patch; no public source).
3. Board configuration: Trustonic off for `rpmb-mtk`; UFS feature objects
   (`ufsfeature`/`ufshid`…) not linked into `ufs-mediatek-mod` although the shared defconfig
   enables them.
4. Toolchain headers: MTK's ACK `ufshcd.h`/`ufshcd-priv.h` line layout.

## Build

```sh
cd android_kernel_modules_storage_ulefone_gq5012bf1
scripts/bootstrap.sh ~/storage-ws
scripts/b1b2.sh ~/storage-ws <stock lib/modules dir>
```

Offline: `LIEPPOS_STORAGE_MIRROR=/home/armol/kernel-work/lieppos-gpu-pin-mirror` (identical pins).
