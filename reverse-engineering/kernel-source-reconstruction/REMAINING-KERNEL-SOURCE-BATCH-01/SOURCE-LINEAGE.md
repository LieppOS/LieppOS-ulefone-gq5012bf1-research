# Source lineage

Maintained source: `../android_kernel_modules_remaining_ulefone_gq5012bf1` @
`7e07384a96580bef13ff3f075355c20b4305a4da` (tree `deefae462128702f4bb1b29e3c82f2e061db96f5`).
The repository preserves the proven build-engine history and owns only the five frozen identities.

## Immutable inputs

| Input | Commit / identity | Role |
|---|---|---|
| GKI kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, tree `710eb859…` | reboot-mode sources, headers, Kbuild/modpost |
| MediaTek ACK | `c364c39ae8d83dfb5d72802a7718b756c238b07e`, tree `fb0bf391…` | source-built OEM split-BTF vmlinux only |
| Nothing device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f`, tree `05f9c65d…` | stock vendor Kconfig/defconfig |
| Nothing kernel_modules | `580d08eac018657a993e56b1806407e41a3b9545`, tree `f6045263…` | `sched_cus` and Mali r44p1 DMA-BUF exporter |
| MiCode MTK_kernel_modules | `a875701d71d29cfac0a9456c1e9c223d44f53d68` (`bsp-rothko-u-oss`) | complete GPL `hbt_driver` |
| clang | `7775eb113f960bc69a780b621d03a715914d4bca` | clang r487747c / LLVM 17.0.2 |
| kernel-build-tools | `e905be252a53d20c52bd9e59df3ff8fdd46b9eab` | pahole 1.23 |
| GKI symvers | build 12901745, sha256 `61933b61…c548` | core export CRCs |

## Per target

### reboot-mode and syscon-reboot-mode

- Compiled source paths: `drivers/power/reset/reboot-mode.c`, `drivers/power/reset/syscon-reboot-mode.c`, and
  `include/linux/reboot-mode.h`.
- Those files and `drivers/power/reset/Makefile` are blob-identical in GKI 6b18f0b5 and MTK ACK c364c39a:
  `b4076b10`, `e0772c9f`, `4a2abb38`, `0a39424f` respectively.
- The prepared vendor config naturally has `CONFIG_REBOOT_MODE=m`, `CONFIG_SYSCON_REBOOT_MODE=m`,
  `CONFIG_MFD_SYSCON=y`, `CONFIG_DEBUG_INFO_BTF=y` and `CONFIG_DEBUG_INFO_BTF_MODULES=y`.
- The modules carry `intree=Y`, `scmversion=g945dff7bc1bf` and complete split BTF. No source delta is applied.

### hbt

Nothing's `hbt_driver_cus/hbt_driver/*` entries are symlinks to a separate unpublished-at-that-location
`../../hbt_driver`; its local `hbt_driver_cus/src/hbt.c` is a 79-line ABI-v1 fallback stub. It cannot produce stock:
it has only `/dev/hbt`, while stock contains `hbt_device2`, string `vhbt`, `filldir64`, `iterate_dir` and
`vfs_llseek`.

Public MiCode has four complete revisions. The Android-U blob `caccc39e…` at commit `a875701d…` is exact. The
complete four-file source is carried verbatim under `source/hbt_driver/`; `UPSTREAM.tsv` pins blobs:

- `Kbuild` `ce319b7c…`
- `Makefile` `231822ea…`
- `src/hbt.c` `caccc39e…`
- `src/hbt.h` `a30e9707…`

The later W revision was not used. No disassembly-derived source was written.

### scheduler_ext

The exact source is Nothing `sched_cus/src/sched_main.c` (`0e48a0a3…`) plus `sched_ko.h` at 580d08ea. It is a
separate two-function external module—not the already certified `scheduler.ko`. Its only behavior is an init that
returns 0 and an empty exit. It identifies as `MODULE_LICENSE("Proprietary")`; this fact is preserved.

The public `sched_cus/Kbuild` also declares `cpuqos_ext` and `eas_ext`, which can link proprietary
`*_o_shipped` objects. Scope routing contains only `scheduler_ext-y += src/sched_main.o`; none of those objects is
copied or linked.

### mali_dmabuf_test_mt6878_r44

Exact source: Nothing kernel_modules 580d08ea,
`gpu/gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/dma_buf_test_exporter/dma-buf-test-exporter.c`
(blob `21ccafcf…`). The source path and `MTK_PLATFORM_VERSION=mt6878` produce the stock module name and stock embedded
`__FILE__` string. This is the ARM DMA-BUF **test exporter**, not `mali_kbase`, GPU firmware or runtime GPU source.
The existing GPU maintained repo uses the same pin; its runtime modules remain separately owned.

## Scope routing

Generated Kbuild/Makefile fragments only select existing source units. They do not change target C/H text. The
assembled EXT and GPU trees are pinned as `73247748…` and `122f1987…`. No stock module, BTF section, instruction,
data, CRC, srcversion, signature or shipped object is a source input.
