# Hardware and runtime contract (static, read-only)

## Evidence sources

- **Device tree:** the stock merged DT, `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`.
- **Source:** pinned ALPS 5e415e05 (plus the irtx delta), limited to the files that were actually compiled
  (`evidence/source-inputs/`).
- **Runtime:** the saved load capture records all 11 frozen modules as loaded. No binding, probe, allocation or
  userspace use was captured, so all of that is **UNKNOWN**.
- **Not done:** no flash, IR, USB, efuse, TEE or regulator operation was performed.

## Device-tree contract

| Module | Driver match | Stock DT node and properties | Label |
|---|---|---|---|
| mtk_jpeg | `mediatek,mtk-jpgenc` (also mt2701/mt8173-jpgdec, jpgenc_c0_c1/_c1 in source) | `jpgenc@17030000`: reg 0x17030000+0x10000, SPI 0x1ef, clocks `jpgenc` + `mmdvfs_clk`, power-domain, `mediatek,larb`. **No jpgdec node**, so on GQ5012BF1 the stock DT gives only the JPEG **encoder** hardware | ENABLED_IN_STOCK_DT (encoder only) |
| mtk-mmdvfs-v3-start | `mediatek,mmdvfs-v3-start` | `mmdvfs-v3-start {}` (no properties) | ENABLED_IN_STOCK_DT |
| mtk-composite | `mediatek,mtk_composite_v4l2_1` | composite node with port/endpoint graph to the flashlight devices | ENABLED_IN_STOCK_DT |
| flashlight (retained D) | `mediatek,flashlight_core` | `flashlight-core`: `low-battery-level = <2>`, `battery-percent-level = <1>`, `battery-oc-level = <2>`. The DT sets an OC level although the stock binary has no OC callback (see BLOCKERS) | ENABLED_IN_STOCK_DT |
| mtk_sec_heap | `mediatek,dmaheap-mtk-sec-page` / `-sec-region` | page heaps `mtk_prot_page-uncached` (tmem type 0x0a), `mtk_sapu_page-uncached` (0x0e), `mtk_svp_page-uncached` (0x09, okay), `mtk_wfd_page-uncached` (0x0b, okay). Region heaps `mtk_prot_region` (0x01), `mtk_sapu_data_shm_region` (0x0c), `mtk_sapu_engine_shm_region` (0x0d), `mtk_svp_region` (0x00, okay), `mtk_wfd_region` (0x02, okay), each with an `-aligned` variant and an iommus phandle | ENABLED_IN_STOCK_DT |
| widevine_driver | `mediatek,drm_wv` | `drm-wv { status = "okay"; }` | ENABLED_IN_STOCK_DT |
| sapu | `mediatek,trusty-sapu`, `mediatek,apu-lock-rv-rpmsg` | `trusty-sapu`: `power-version = <1>`, `datamem-type = <2>`, `datamem-size = <0 0>`, iommus; `sapu-lock-rpmsg` (`mtk,rpmsg-name = "apu-lock-rv-rpmsg"`) | ENABLED_IN_STOCK_DT |
| mtk_irtx_pwm | `mediatek,irtx-pwm` | `irtx-pwm`: `pwm-ch = <0>`, `pwm-data-invert = <0>`, `pwm-supply = "mt6369_vio28"`, **`dma-mask-bit = <0x23>` (35-bit)**, consumed by the reconstructed OEM delta | ENABLED_IN_STOCK_DT |
| nvmem-mt635x-efuse | `mediatek,mt6363-efuse`, `mediatek,mt6373-efuse` (driver also lists 6359p/6368/6377) | `mt6363-efuse` (cell `mt6363_e_data` reg 0x5e+8) and a node named `mt6369-efuse` with compatible `mediatek,mt6373-efuse` (cell `mt6369-e-data@4a` reg 0x4a+0xa) | ENABLED_IN_STOCK_DT |
| mtk_heap_debug, tui-common | none | — | STOCK_BINARY_IMPLEMENTATION |

## Implementation facts (source, byte-identical objects)

- **mtk_jpeg** ("MediaTek JPEG codec driver"): a V4L2 mem2mem driver (`v4l2_device_register`,
  `video_register_device`). It bandwidth-votes through mtk-icc-core and frequency-votes through mtk-mmdvfs-v3. It
  is the JPEG engine only and says nothing about video codec or recording capability.
- **mtk-mmdvfs-v3-start**: a probe thread (`mmdvfs-v3_start`) waits for `mtk_is_mmdvfs_v3_debug_init_done()`, then
  calls `mtk_mmdvfs_enable_vcp(false, VCP_PWR_USR_MMDVFS_INIT)`. That releases the init-time VCP power vote, which
  makes it an initialisation-sequencing helper. Its tables and policy live in the certified mtk-mmdvfs-v3 and
  mtk-mmdvfs-debug.
- **mtk-composite** ("MTK V4L2 Composite Driver"): registers a media device and a V4L2 device that group the
  flashlight sub-devices. It is **not** USB.
- **mtk_irtx_pwm** ("MTK PWM IR Transmitter"):
  - is an rc-core device (`rc_allocate_device` / `rc_register_device`) in PWM memory mode, using mtk-pwm
    `pwm_set_spec_config` and a DMA-coherent waveform buffer;
  - powers on through `pwm-supply` (`mt6369_vio28`);
  - sets the DMA mask from `dma-mask-bit` before each TX allocation (OEM delta).
- **nvmem-mt635x-efuse**: `devm_nvmem_register` with `.read_only = true` and only a `.reg_read` callback, reading
  the PMIC efuse over the PMIC regmap. It is read-only by construction; no write path exists.
- **mtk_heap_debug**: procfs `/proc/dma_heap/{all_heaps,monitor,rss_pid,stats}` and `/proc/dma_heap/heaps/`. It
  hooks into mrdump (`mrdump_mini_add_extra_file`) and monitor_hang (`mtk_dmabuf_dump_for_hang`). It uses symbols
  from system_heap and mtk_sec_heap.

## Load order (providers first)

- **First stage:** mrdump 2, monitor_hang 5, mtk-icc-core 57, mtk-mmdvfs-v3 63, mtk-mmdvfs-debug 66, system_heap 72,
  mtk_bp_thl 85.
- **Second stage, providers:** gz_trusty_mod 258, gz_tz_system 260, mtk_low_battery_throttling 274, mtk_pbm 277,
  mtk-pwm 284, mtk_peak_power_budget 292, tmem_ffa 300.
- **Second stage, batch modules interleaved with providers:** mtk_irtx_pwm 285 (after mtk-pwm 284),
  mtk_sec_heap 303, nvmem-mt635x-efuse 306, mtk_jpeg 346, flashlight 367, mtk-composite 393, mtk_heap_debug 409,
  sapu 410, widevine_driver 425, mtk-mmdvfs-v3-start 429, tui-common 439.
