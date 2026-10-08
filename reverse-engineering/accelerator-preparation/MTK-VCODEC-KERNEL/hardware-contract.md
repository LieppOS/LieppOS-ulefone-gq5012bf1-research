# Hardware contract — MTK-VCODEC-KERNEL

Evidence tiers are kept strictly apart. Nothing in this file was observed on a running device.

## PROVEN HARDWARE (stock merged device tree, `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb`)

| Node | compatible | registers (parent-bus) | interrupt cells | clocks | power domain | IOMMU |
|---|---|---|---|---|---|---|
| `/soc/vdec@16000000` | `mediatek,mt6878-vcodec-dec` | `VDEC_BASE 0x16000000+0x1000`, `VDEC_SYS 0x1602f000+0x1000`, `VDEC_VLD 0x16020000+0x1000`, `VDEC_MC 0x16021000+0x1000`, `VDEC_MV 0x16023000+0x1000`, `VDEC_MISC 0x16025000+0x4000` | `GIC_SPI 0x1e8 level` | `CORE_MT_CG_VDEC0` from `/syscon@1602f000` | `/power-controller@1c001000` arg `0x13` | `/soc/iommu@1e802000` ports `0x50080‥0x5008b`, LARB phandle `0x76` |
| `/soc/venc@17000000` | `mediatek,mt6878-vcodec-enc` | `VENC_SYS 0x17020000+0x6000`, `VENC_C1_SYS 0x17820000+0x20000` | `GIC_SPI 0x1ee level` | `MT_CG_VENC0` from `/syscon@17000000`, `mmdvfs_clk` from `/mmdvfs-clk` | `/power-controller@1c001000` arg `0x9` | `/soc/iommu@1e802000` ports `0xe0‥0xee`, LARB phandle `0x77` |
| `/syscon@1602f000` | `mediatek,mt6878-vdecsys` | `0x1602f000+0x1000` | — | `#clock-cells=1` | — | — |
| `/syscon@17000000` | `mediatek,mt6878-vencsys` | `0x17000000+0x1000` | — | `#clock-cells=1` | — | — |
| `/soc/vcp-iommu-vdec@1ec24000` | `mediatek,vcp-io-vdec` | `0x1ec24000+0x1000` | — | — | — | IOMMU port `0x40522`, `vcp-support=2` |
| `/soc/vcp-iommu-venc@1ec30000` | `mediatek,vcp-io-venc` | `0x1ec30000+0x1000` | — | — | — | IOMMU port `0x40522`, `vcp-support=3` |

Also declared on both codec nodes: `mmqos-supply` to `/interconnect` with two LARB paths each
(`path_larb4/5` for the decoder, `path_larb7/8` for the encoder), `operating-points-v2`,
`bandwidth-table`, `throughput-min/normal-max/op-rate-thresh`, `dma-ranges` covering 34-bit,
`mediatek,platform = "platform:mt6878"`. The encoder additionally declares
`mmdvfs-dvfsrc-vcore-supply` → `/soc/dvfsrc@1c00f000/dvfsrc-vcore`, `need-smi-monitor`, a
`config-table` and a `throughput-table`.

Addresses are parent-bus addresses; `ranges` translation must be checked before calling them
CPU-physical. Interrupt numbers are DT cells, not observed Linux IRQ numbers.

The JPEG codec, MDP and display blocks are separate hardware with separate owners and are not
part of this component.

## STOCK BINARY IMPLEMENTATION (reconstructed byte-identically; source now authoritative)

* `mtk-vcodec-dec-v1` matches `mediatek,mt6878-vcodec-dec`; `mtk-vcodec-enc-v1` matches
  `mediatek,mt6878-vcodec-enc`; `clk-mt6878-vcodec` matches both
  `mediatek,mt6878-vdecsys` and `mediatek,mt6878-vencsys` and registers its gates through
  `mtk_clk_simple_probe` (`clk-common`).
* Decoder and encoder register V4L2 M2M video devices named `mtk-vcodec-dec` /
  `mtk-vcodec-enc` (`video_register_device(..., VFL_TYPE_VIDEO, -1)`), with videobuf2
  DMA-contig queues and `v4l2_m2m` scheduling.
* Interrupts are claimed with `devm_request_irq` in `mtk_vcodec_intr.c` (separate decoder,
  LAT-decoder, line-count and encoder/C1-encoder handlers exported from
  `mtk-vcodec-common`).
* Power/clock handling is in `mtk_vcodec_dec_pm.c` / `mtk_vcodec_enc_pm.c` plus the
  platform-V1 policy objects `v1/mtk_vcodec_dec_pm_plat.o`, `v1/mtk_vcodec_enc_pm_plat.o`,
  `v1/vcodec_dvfs.o` (`CONFIG_VIDEO_MEDIATEK_VCODEC_V1=y`; the V2 policy objects exist in the
  tree but are **not** part of the shipped modules).
* Memory: DMA-BUF import/attach, `mtk_dma_sync_sg_range`, IOMMU fault callback registration
  through `iommu_debug`, SLBC/SLC cache allocation in `mtk_vcodec_dec_slc.c`, MMQoS/ICC
  bandwidth setting via `mtk_icc_set_bw`.

## CONFIGURED BUT UNVERIFIED

* Every value above is a static declaration. Successful probe, clock/power enable, interrupt
  servicing, IOMMU mapping, DVFS/bandwidth transitions and throughput are **not** evidenced.
* `mtk-vcu.ko` is shipped and loaded (line 78 of `modules.load`) and does export 14 symbols
  consumed by the codec drivers, but **no node in the stock merged DTB matches any of its 12
  OF aliases** (`mediatek,mt8173-vcu`, `mediatek-vcu`, `mediatek,vcu-io-venc`, …). On this
  board the codec drivers' firmware path is the VCP/TinySys one
  (`CONFIG_MTK_TINYSYS_VCP_SUPPORT=m`, `vdec-mmdvfs-in-vcp`, `vcp-io-vdec/venc` nodes), so
  whether the VCU platform driver ever probes here is **UNKNOWN** and must not be assumed.

## UPSTREAM REFERENCE ONLY

The decoder/encoder match tables carry compatibles for MT8173/MT2712/MT6771/MT6885/MT6873/
MT6853/MT6983/MT6879/MT6895/MT6855/MT6985/MT6886/MT8195/MT6835/MT6897/MT6989 and the V2 DVFS
policy. None of these corresponds to GQ5012BF1 hardware.

## UNKNOWN

Register field semantics (no register-level documentation was recovered), electrical
enablement, real decode/encode capability, concurrency limits, thermal behaviour and
secure/protected path behaviour.

**Recovering these drivers does not add silicon capability.** No new codec, resolution,
frame-rate, hardware engine or interface is unlocked by this work.
