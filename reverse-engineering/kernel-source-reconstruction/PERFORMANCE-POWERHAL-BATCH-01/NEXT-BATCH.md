# Remaining Category D after this batch (projected 18) and recommended next work

| Group | Modules | Source | Note |
|---|---|---|---|
| **Media / security / platform tail (KDM)** — recommended next | flashlight, mtk-composite, mtk_jpeg, mtk-mmdvfs-v3-start, mtk_sec_heap, mtk_heap_debug, widevine_driver, tui-common, sapu, mtk_irtx_pwm, nvmem-mt635x-efuse (11) | ALPS `drivers/misc/mediatek/{flashlight,mmdvfs,widevine_drm,apusys/sapu,irtx}`, `drivers/dma-buf/heaps`, `drivers/media/platform/mtk-jpeg`, `drivers/input/touchscreen`, `drivers/nvmem` | All single vendor_dlkm occurrences, except mtk-mmdvfs-v3-start, which is in both partitions. Same engine (KDM, likely no BTF). Check each for `.BTF` and OEM deltas: flashlight and tui-common are ODM-adjacent. |
| In-tree reboot pair | reboot-mode, syscon-reboot-mode | GKI-tree `drivers/power/reset` | vendor_boot + vendor_dlkm (2 occurrences each). Likely the native/split-BTF stage of the boot-dependencies engine. |
| Nothing `kernel_modules/*_cus` | hbt, scheduler_ext (pure source); fpsgo, msync2_frd (link `*_shipped` prebuilt objects) | Nothing kernel_modules 5f75a3b | Needs a second external-module root. fpsgo/msync2_frd need an explicit project decision: shipped MediaTek objects cannot be certified as source. |
| Mali diagnostic | mali_dmabuf_test_mt6878_r44 | Mali r44p1 `dma_buf_test_exporter` | GPU repo family. |

Before freezing, check the then-current canonical audit and the Codex G-SOURCE-RECOVERY-BATCH-01 manifest for ownership changes.
