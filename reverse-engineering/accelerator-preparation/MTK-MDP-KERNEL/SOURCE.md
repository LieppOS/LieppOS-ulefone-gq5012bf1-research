# Source of the four GQ5012BF1 MDP/MML kernel modules

**All four shipped modules are built from unmodified public MediaTek ALPS source.** No C or
header file is patched. The only additions are 9 `Kbuild` build-scope wrappers.

| stock module | source files | source location (pin `alps5e41`) |
|---|---|---|
| `mdp_drv_mt6878.ko` | `mdp_mt6878.o mdp_driver.o mdp_ioctl_ex.o mdp_common.o cmdq_record.o cmdq_virtual.o cmdq_device.o mdp_event_common.o cmdq_subsys_common.o cmdq_helper_ext.o cmdq_mmp.o mdp_fence.o mdp_dpc.o` | `drivers/misc/mediatek/mdp/` |
| `mtk-mml.ko` | 31 objects: `mtk-mml-{monitor,driver,core,tile,pq-core,drm-adaptor,dle-adaptor,buf,sys}.o`, `tile_core.o`, `tile_mdp_func.o`, `DpTileScaler.o`, components `mtk-mml-{aal,color,fg,fg-fw,hdr,mutex,rdma,rsz,rsz-fw,pq-rdma,pq-birsz,pq-birsz-fw,tcc,tdshp,wrot,rrot,merge,c3d,dpc,scmi}.o` | `drivers/gpu/drm/mediatek/mml/` |
| `mtk-mml-mt6878.ko` | `mtk-mml-tp-mt6878.o` | `drivers/gpu/drm/mediatek/mml/` |
| `clk-mt6878-mdpsys.ko` | `clk-mt6878-mdpsys.o` | `drivers/clk/mediatek/` |

Object membership is the vendor `Makefile`'s own, unmodified, under the shipped vendor
config (`CONFIG_MTK_MDP=m`, `CONFIG_MTK_MML=m`, `CONFIG_COMMON_CLK_MT6878_MDPSYS=m`,
`CONFIG_MTK_MML_DEBUG` unset → no `mtk-mml-test.o` / `mtk-mml-mmp.o`,
`CONFIG_MTK_MML_LEGACY` unset, `CONFIG_MTK_MDP_MTEE_SUPPORT` unset → no
`CMDQ_SECURE_PATH_SUPPORT`).

## Pins

| id | repository | commit | role |
|---|---|---|---|
| `alps5e41` | `github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` | `5e415e059253ce0d2e61c97108e5f5785d71f06f` (tree `9c61acc3cb0d…`) | **exact MDP/MML/clock source, headers, provider source** |
| `kdm` | same repository | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | vendor `Kconfig` + `mgk_64_k61_defconfig` only |
| `common` | `android.googlesource.com/kernel/common` | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | GKI build 12901745 headers/kbuild/modpost |
| `clang` | `prebuilts/clang/host/linux-x86` | `7775eb113f960bc69a780b621d03a715914d4bca`, `clang-r487747c` | Android clang 17.0.2 (10087095) |

## Maintained repository

`LieppOS custom ROM/android_kernel_modules_mdp_ulefone_gq5012bf1` (local, never pushed) —
immutable pins, both patches, bootstrap/assemble/build/B1-B2/verify scripts, the
source-derived external provider ABI and the stock hash reference.

```sh
scripts/bootstrap.sh <ws>            # fetch + tree-id/sha256 verify every pin
scripts/b1b2.sh      <ws> <stockdir> # two independent builds + full acceptance
```

## Result

Each rebuilt module is byte-identical to its stock counterpart except the 20-byte GNU
build-ID descriptor. Measured on a clean checkout: see
[RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) and
[build-reproduction.md](build-reproduction.md).
