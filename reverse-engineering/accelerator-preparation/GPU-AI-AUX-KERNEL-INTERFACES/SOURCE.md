# Source of the three GQ5012BF1 GPUEB/VCP kernel modules

**All three shipped modules are built from unmodified public MediaTek ALPS source.** No C or
header file is patched. The only additions are 5 `Kbuild` build-scope wrappers.

| stock module | source files | source location (pin `alps5e41`) |
|---|---|---|
| `gpueb.ko` | `gpueb_init.o gpueb_ipi.o gpueb_logger.o gpueb_plat_service.o gpueb_reserved_mem.o gpueb_gpumpu.o gpueb_hwvoter_dbg.o gpueb_debug.o gpueb_timesync.o` | `drivers/gpu/mediatek/gpueb/` |
| `vcp.ko` | `vcp_helper.o vcp_excep.o vcp_irq.o vcp_logger.o vcp_l1c.o vcp_vcpctl.o vcp_feature_table.o vcp_awake.o vcp_hwvoter_dbg.o` | `drivers/misc/mediatek/vcp/rv/` |
| `vcp_status.ko` | `vcp_status.o` | `drivers/misc/mediatek/vcp/rv/` |

Object membership is the vendor `Makefile`'s own, unmodified, under the shipped vendor
config (`CONFIG_MTK_TINYSYS_VCP_SUPPORT=m`; `CONFIG_MTK_TINYSYS_VCP_DEBUG_SUPPORT` unset;
the `gpueb` Makefile lists `obj-m += gpueb.o` unconditionally).

## Pins

| id | repository | commit | role |
|---|---|---|---|
| `alps5e41` | `github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` | `5e415e059253ce0d2e61c97108e5f5785d71f06f` (tree `9c61acc3cb0d…`) | **exact GPUEB and VCP host source, headers, provider source** |
| `kdm` | same repository | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | vendor `Kconfig` + `mgk_64_k61_defconfig` only |
| `common` | `android.googlesource.com/kernel/common` | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | GKI build 12901745 headers/kbuild/modpost |
| `clang` | `prebuilts/clang/host/linux-x86` | `7775eb113f960bc69a780b621d03a715914d4bca`, `clang-r487747c` | Android clang 17.0.2 (10087095) |

## Maintained repository

`LieppOS custom ROM/android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1`
(local, never pushed; branch `main`) — immutable pins, both patches,
bootstrap/assemble/build/B1-B2/verify scripts, the source-derived external provider ABI and
the stock hash reference.

```sh
scripts/bootstrap.sh <ws>            # fetch + tree-id/sha256 verify every pin
scripts/b1b2.sh      <ws> <stockdir> # two independent builds + full acceptance
```

## Result

Each rebuilt module is byte-identical to its stock counterpart except the 20-byte GNU
build-ID descriptor. Measured on a clean checkout: see
[RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) and
[build-reproduction.md](build-reproduction.md).

**Firmware is not in scope.** `gpueb.img` (529 408 B,
`e8a1f8f70f51e0a7b390ecaff32afe573b83a5a851f9d93a497528616001df61`) and `vcp.img`
(1 492 000 B, `98e289424be7929ca40081ab7e4d6084ec35cd76eae91ea19cf501dfb6d09a5c`) remain
proprietary, unmodified and unanalysed; only the kernel-side host code is reconstructed.
