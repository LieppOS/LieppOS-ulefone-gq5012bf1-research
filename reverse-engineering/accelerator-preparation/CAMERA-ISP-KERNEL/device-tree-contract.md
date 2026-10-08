# Device-tree-to-driver contract — CAMERA-ISP-KERNEL

## Evidence operands

The selected stock base DT + overlay is preserved as
`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` in the research workspace.
The 35 relevant nodes and all their properties are decoded in [dt-nodes.tsv](dt-nodes.tsv).
[hardware-contract.md](hardware-contract.md) gives register and interrupt summaries;
[module-dt-match.tsv](module-dt-match.tsv) compares stock `of:` aliases with **all**
compatible strings in the merged DT, not just the camera subset.

## Configured driver chain

These are **static probe implementations**, not observed successful probes.

| board compatible(s) | owned implementation / probe | downstream interface |
|---|---|---|
| `mediatek,imgsensor` | `imgsensor`: `imgsensor_probe` | sensor V4L2 subdevice/control/frame-sync into SENINF |
| `mediatek,seninf-core`, `mediatek,seninf` | `mtk-cam-isp7sp`: `seninf_core_probe`, `seninf_probe` | CSI receiver and media-graph routing |
| `mediatek,mt6878-camisp`, `mediatek,camisp-larb` | `mtk-cam-isp7sp`: `mtk_cam_probe`, `mtk_cam_larb_probe` | media requests, engine orchestration and DMA/IOMMU resources |
| `mediatek,cam-raw`, `cam-rms`, `cam-yuv` | `mtk-cam-isp7sp`: `mtk_raw_probe`, `mtk_rms_probe`, `mtk_yuv_probe` | RAW/RMS/YUV processing and buffer queues |
| `mediatek,camsv`, `mediatek,mraw` | `mtk-cam-isp7sp`: `mtk_camsv_probe`, `mtk_mraw_probe` | CAMSV capture and MRAW metadata/statistics queues |
| `mediatek,hcp7sp` | `mtk_hcp`: `mtk_hcp_probe` | `/dev/mtk_hcp` registration and shared command/tuning buffers |
| `mediatek,imgsys-cmdq-7sp` | `mtk_imgsys_cmdq`: `mtk_imgsys_cmdq_probe` | CMDQ job submission |
| `mediatek,imgsys-isp7sp-mt6878` | `mtk_imgsys_isp7sp` platform tables + `mtk_imgsys_v4l2`: `mtk_imgsys_probe` | IMG_SYS V4L2 queues and P2 engine dispatch |
| `mediatek,ccd` | `mtk_ccd_remoteproc`: `ccd_probe` | `/dev/mtk_ccd`, remoteproc and `ccd_rpmsg` transport |
| `mediatek,ccu_rproc`, `mediatek,ccucammain` | `mtk_ccuv`: `mtk_ccu_probe`, `mtk_ccu_cam_main_probe` | CCU host memory/IPC, retained proprietary firmware |
| `mediatek,aie-isp7sp-2` | `mtk_aie`: `mtk_aie_probe` | AIE V4L2 jobs; debug helper module |
| `mediatek,camera-pda` | `pda_drv_mt6878`: `PDA_probe` | private PDA job/control interface |

The firmware/HAL consumers are retained proprietary camera services, not open algorithms.
All listed probe functions are accounted for in [function-parity.tsv](function-parity.tsv).

## Resource providers

The lossless provider ledger contains **283** resolved references:

* 166 `clocks`;
* 70 `iommus` (including exact provider port arguments);
* 15 `power-domains`;
* 22 `mboxes`;
* 10 regulator/supply references.

Each record retains the consumer path, property, provider path, compatible and arguments.
This proves what the board requests; it does not prove the supplier is loaded, the power
rail is electrically correct, or the IOMMU mapping is usable. Generic providers remain
external dependencies and are not silently reconstructed by this component.

## Absent or indirect bindings

`mtk-ipesys-me` has no board alias match. DPE's source matches `mediatek,dvp`/`dvs`/`dvgf`;
VMM regulator/notifier source matches `mediatek,ispdvfs`/`mediatek,vmm_notifier`. These
strings are absent. The board's `mediatek,vmm_spm_mt6878` node is **not** evidence that
those separate VMM drivers bind. C2PS, glue and transport helpers do not require a direct
hardware-compatible node. No live character/video node is inferred for an unbound driver.

## Runtime qualification

All 35 nodes are `okay` or implicitly enabled, but this closure performs no phone
interaction. Boot captures must still establish actual binding, deferred-probe status,
media/video node numbering, firmware readiness and stream/capture execution. Sensor
population and per-unit calibration remain with their existing owners.
