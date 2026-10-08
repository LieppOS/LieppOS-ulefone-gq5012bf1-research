# Build reproduction — MALI-GPU-KERNEL

## One command

```
scripts/build_b1_b2.sh          # W=/home/armol/kernel-work/accelerator-mali-gpu-kernel
```

Each of B1 and B2 runs the same steps:
1. Wipe `clean/`.
2. `git archive` the pinned reconstruction trees (kdm `2e0f942217c2`, gpu `ec7e11b4a4e9`)
   into it.
3. Make a fresh copy of the prepared vendor kout.
4. Build `kdm` (ged, hal, gpu_bm, gpufreq), then `gpu` (mali r44p1) against kdm's natural
   `Module.symvers` plus `symvers/stock-external-provider.symvers`.

**Result:** every `.ko`, stripped `.ko` and both `Module.symvers` are byte-identical
between B1 and B2 (`parity/b1b2/B{1,2}.SHA256SUMS`).

| module (stripped) | sha256 (B1 = B2) |
|---|---|
| mtk_gpu_hal | e048f0e954c8cbeb65dbdc34b220b4cbe2385e9c281aae51aedc6d0bd4acbd40 |
| mtk_gpu_qos | 773af84cfef1e6f5594cc8e322b779a95d7755b564b35cab4e801aa39d635f30 |
| mtk_gpufreq_wrapper | 18db732c455eeeb99b9c48d19ed1a9752210124cf5109ca1f07d3b6b4f2f29f8 |
| mtk_gpufreq_mt6878 | 6a5848494d945021e52969d4c9fb891af043e5eb850103131835b6222e3259e9 |
| ged | ca1fc12bedc6e8d424a5aed4be79aeedbf2f532d6aa7bbe113190c7642e5e962 |
| mali_mgm_mt6878_r44 | e2d9978391c7833f7a26850742fe7c3f04d24e1fa11b9336bbf65c0c2b1e6106 |
| mali_prot_alloc_mt6878_r44 | 860962dc7bcd6b3feb6e1ba785c7c573218f1d1ddc2f5e5f03dfb8f1df6ca609 |
| mali_kbase_mt6878_r44 | 7f72323ff14953b0d0086ced37a2c9bb44135255efab02e49761668280376d10 |

## Inputs

| input | value |
|---|---|
| compiler / linker | Android clang `r487747c` (17.0.2, 10087095), ld.lld, `LLVM=1 LLVM_IAS=1`. Stock `.comment` is the same string. |
| kernel source | GKI common `6b18f0b574ab` (CI 12901745). The tree was not modified for this build. |
| kernel config | `gki_defconfig` + kdm `mgk_64_k61_defconfig` with `KCONFIG_EXT_PREFIX` (camera-stack `make_vendor_kout.sh`, identical to `vendor-kernel.config`). LTO off for external modules (stock modules carry no LTO bitcode); KCFI on (`-fsanitize=kcfi`, from the GKI config). |
| release / vermagic | `include/config/kernel.release` = `6.1.115-android14-11-g945dff7bc1bf` (the stock vendor kernel's string) |
| KCFLAGS | `-D__ANDROID_COMMON_KERNEL__` (what GKI `build.config.common` adds to every Kleaf module build; r44p1 `version_compat_defs.h` needs it), `-faddrsig` (stock carries `.llvm_addrsig`; this host's clang default drops it), and `-fmacro-prefix-map` entries |
| `-fmacro-prefix-map` | Rewrites `__FILE__` to the stock spellings `../kernel_device_modules-6.1/…` and `../vendor/mediatek/kernel_modules/gpu/…`. The unnormalised `<common>/../../…` spelling must be mapped too, because headers reached via `-I$(srctree)/<rel>` arrive that way (this was the sole difference in `mtk_gpufreq_mt6878`'s `.rodata.str`). |
| gpu Kbuild options | `BUILD_RULE=OOT CONFIG_MALI_MEMORY_GROUP_MANAGER=y CONFIG_MALI_PROTECTED_MEMORY_ALLOCATOR=y CONFIG_DMA_SHARED_BUFFER_TEST_EXPORTER=y` (MTK `gpu/Makefile` defaults). The per-SoC feature set comes from the donor `midgard/Makefile` `mt6878` block. |
| post-processing | `llvm-strip --strip-debug` (vendor_dlkm install step). Stock vendor modules are **not signed**, so there is no signature axis. |
| provider ABI | owned providers come from the natural kdm build; the 39 external-provider CRCs come from `symvers/stock-external-provider.symvers`, extracted from the stock providers' own `__kcrctab` with `tools/phase4-extract-stock-provider-symvers.py`. Natural-CRC cross-check: `abi-kmi-parity.md`. |

## Build-plumbing changes (not source changes)

* `kdm/Kbuild`: only `obj-y += drivers/gpu/mediatek/`.
* `drivers/gpu/mediatek/Makefile`: no `gpueb/` (owned by GPU-AI-AUX-KERNEL-INTERFACES) and
  no `gpu_iommu/` (mt6989 only).

Neither change can alter an owned module's objects; they only skip other directories.

## Environment notes

* `kout` must sit where the relative `M=` resolves identically from `O=` and from common.
  `kb.sh` enforces this.
* `git update-index --assume-unchanged` is **not** used by this component. The GKI
  `common/build.config.common` in this workspace *is* marked assume-unchanged (with
  `-faddrsig` in KCFLAGS) by the earlier SYSTEM-DLKM work. That state is preserved
  untouched. It does not affect this build, because `make` never reads `build.config.*`
  and `kb.sh` passes KCFLAGS itself.
