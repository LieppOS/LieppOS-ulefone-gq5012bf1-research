# Recommended next coherent unowned batch

After the staged batches (projected A361 / B1 / C10 / D32 / G54), the largest coherent unowned D family is
**MediaTek performance / power-HAL** (all KDM `drivers/misc/mediatek/performance*`, vendor_dlkm second stage):

- `mtk_perf_ioctl`, `mtk_perf_ioctl_magt`, `mtk_ioctl_powerhal`, `mtk_ioctl_touch_boost` (`performance/`)
- `mtk_fpsgo` (`performance/fpsgo_v3`; provider of 4 symbols to the mtk_mbraink certified here), `frs`,
  `load_track`, `powerhal_cpu_ctrl`, `touch_boost`, `uload_ind`
- `mtk_perf_common` (`perf_common`)
- Close neighbours by load order and subsystem: `cpuqos_v3`, `scheduler`, `task_turbo` (14 total)

Check before freezing:
- Exact identities and classes in the then-current audit.
- Which of `fpsgo.ko`, `hbt.ko`, `msync2_frd.ko` and `scheduler_ext.ko` belong to separate
  `kernel_modules:*_cus` source trees (different provenance; likely a separate batch).
- That the FPSGO witness already compiled here (exact CRC/KCFI for 4 exports) is only an ABI witness.

Smaller coherent follow-ups: `reboot-mode` + `syscon-reboot-mode` (in-tree `drivers/power/reset`, both partitions),
DMA-BUF heaps (`mtk_sec_heap`, `mtk_heap_debug`) and flashlight (`flashlight`, `mtk-composite`).
