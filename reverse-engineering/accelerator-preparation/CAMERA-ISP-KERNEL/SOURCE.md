# CAMERA-ISP-KERNEL — maintained source

**Repository:** `LieppOS custom ROM/android_kernel_modules_camera_isp_ulefone_gq5012bf1`
(local, branch `main`, HEAD `96d223a3139ab59107fab180d31634d6c5c651ad`, no remote,
**never pushed**). A complete-history bundle is preserved at
`source/android_kernel_modules_camera_isp_ulefone_gq5012bf1.bundle` (SHA-256
`7de783c3f1b86fbc19c461c74e043131b7f847859d9162d165176adf0bf12087`).

It is an immutable **source recipe**: public pins + patches + build and verification
scripts. No stock binary, firmware blob or vendor userspace artifact is stored in it.

```
scripts/bootstrap.sh    <ws>              fetch and verify every pinned input
scripts/assemble.sh     <ws>              extract both source trees, apply patches, assert tree ids
scripts/make-kout.sh    <ws>              gki_defconfig + mgk_64_k61_defconfig, modules_prepare
scripts/derive-provider-crcs.sh <ws>      regenerate the external provider ABI from public source
scripts/build.sh        <ws> [tag]        build all nineteen modules (one modpost scope per package)
scripts/b1b2.sh         <ws> [stock dir]  two clean builds + full stock verification
scripts/archive-pins.sh <ws> <mirror>     offline mirror of every public input
```

## Pins

| id | upstream | commit | subtree | tree |
|---|---|---|---|---|
| `common` | `https://android.googlesource.com/kernel/common` | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `.` | `710eb859513863cda0204995a411d5795ad3fe92` |
| `clang` | `https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86` | `7775eb113f960bc69a780b621d03a715914d4bca` | `clang-r487747c` | `8eb8e3afb00a52d48b29381d73daf352362231ad` |
| `kdm` | `https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `.` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` |
| `kmod` | `https://github.com/NothingOSS/android_kernel_modules_nothing_mt6878` | `5f75a3b13e8135d45b4b0b70ec893345144f70df` | `mtkcam` | `ae4272e46819a936abd2f64fe3db68b25f6e1a3e` |

plus GKI build **12901745** `vmlinux.symvers`
(sha256 `61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548`; an xz copy is
kept in the repo so the build works with ci.android.com unreachable).

Assembled (patched) trees, asserted on every build:
`mtkcam = 4b75fc209a4b8a608aec9dc5b86d29fa095646fe`,
`kdm = ceab410136a0542d16d3654bb73634cef09ff1f8`.

## Patches

| file | files touched | content |
|---|---|---|
| `0001-mtkcam-gq5012bf1-camera-isp-reconstruction.patch` | 29 | camsys / imgsys / hcp / ipesys-me / aie / dpe / ccusys / sched deltas, stock source line placement, and the `LIEPPOS_ONLY` build-scope selector |
| `0002-imgsensor-gq5012bf1-reconstruction.patch` | 553 | the GQ5012BF1 `imgsensor` package: nine sensor sub-drivers with stock-derived mode tables, frame-sync, adaptor and the Ulefone YFT hooks |
| `0003-kdm-gq5012bf1-camera-headers-and-build-scope.patch` | 3 | `kd_imgsensor.h` GQ5012BF1 sensor IDs, `cam_cal_format.h` 24-byte part-number ABI, `LIEPPOS_ONLY` selector |

`pda_drv_mt6878.ko`, `mtk-vmm-isp71-regulator.ko` and `mtk-vmm-notifier.ko` are built from
**unmodified** NothingOSS source and are byte-identical to stock apart from the build ID.

## Build facts that matter for parity

* `clang-r487747c` (the stock `.comment` section matches exactly);
* `UTS_RELEASE "6.1.115-android14-11-g945dff7bc1bf"` (stock `vermagic`);
* `KCFLAGS=-faddrsig` — stock carries `.llvm_addrsig`, plain `make` drops it;
* `module_scmversion=` — the stock tree was not a git checkout;
* one modpost scope per MTK package, whose extra symbols are the external provider
  symvers plus **only** the sibling packages that the stock `depends=` names (this is
  what makes `mtk-cam-isp7sp` record `mtk_ccu_mssv`, not the in-tree `mtk_ccuv`);
* the kernel output tree is a pure **output mirror**: kbuild writes `../vendor/...`
  objects and resolves the `.c` prerequisites through `VPATH`, exactly the shape recorded
  in the stock per-object `.cmd` files. With the sources reachable from `<kout>/..`
  instead, clang numbers private globals differently and four modules stop matching;
* `imgsensor` keeps MediaTek's own package recipe
  (`CONFIG_MTK_V4L2_IMGSENSOR=m`, `-DCONFIG_MTK_AEE_FEATURE=1 -DCONFIG_MTK_AEE_AED_MODULE=1`,
  sensor list in the stock link order).

## Licence and provenance

GPL-2.0, inherited from the MediaTek/Linux sources; `LICENSE.md` in the repository.
Every byte of the recipe is either public upstream source, a patch derived from
measurements against the shipped modules, or a build script written for this work.
