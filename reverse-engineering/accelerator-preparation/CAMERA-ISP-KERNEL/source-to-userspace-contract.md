# Source-to-userspace contract — CAMERA-ISP-KERNEL

This document separates what the reconstructed normal-world kernel exposes from what is
still supplied by the proprietary camera userspace stack.

## Kernel-facing topology

| kernel area | principal modules | observable contract |
|---|---|---|
| sensor ingress | `imgsensor.ko`, `imgsensor-glue.ko`, `mtk-cam-isp7sp.ko` | V4L2 subdevices/media graph, sensor controls, SENINF/CSI routing, frame-sync and RAW/CAMSV/MRAW queues |
| capture pipeline | `mtk-cam-isp7sp.ko` | V4L2 video/meta queue lifecycle, media requests, formats, buffers, fences and events |
| P2 / IMG_SYS | `mtk_hcp.ko`, `mtk_imgsys_v4l2.ko`, `mtk_imgsys_cmdq.ko`, `mtk_imgsys_isp7sp.ko`, `mtk-ipesys-me.ko` | V4L2 nodes, HCP command/tuning buffers, CMDQ submission and DIP/TRAW/WPE/ME/PQDIP dispatch |
| coprocessors | `mtk_ccd_remoteproc.ko`, `ccd_rpmsg.ko`, `mtk_ccuv.ko` | remoteproc/RPMsg, CCU memory and message transport |
| accelerators | `mtk_aie.ko`, `mtk_aie_debug_7sp_2.ko`, `camera_dpe_isp7sp.ko`, `pda_drv_mt6878.ko` | V4L2/private ioctl surfaces for face/AI, depth and phase-detection jobs |
| power/performance | `mtk-vmm-isp71-regulator.ko`, `mtk-vmm-notifier.ko`, `c2ps_perf_ioctl.ko`, `mtk_c2ps.ko` | voltage/notifier and camera scheduling/uclamp requests |

The exact implementation behind these interfaces is accepted by the function/data/ABI/
relocation evidence. The API inventory is supported by
[abi-source-witnesses.tsv](abi-source-witnesses.tsv); source locations there are donor
lineage, while the new module parity proves that the assembled source corresponds to the
stock modules.

## Device-node qualification

The source registers V4L2 video/meta devices for camsys, IMG_SYS, AIE and DPE and character
devices for HCP/CCD/private controls. Dynamic `/dev/videoN` numbering is assigned at probe
and cannot be recovered from source or DT alone. DPE, IPESYS-ME, VMM and C2PS have no
matching board-compatible node in the merged GQ5012BF1 DT; some are helper/child or
programmatically registered modules, while DPE/IPESYS-ME may simply remain unbound on this
board. Do not invent a live `/dev` path without a boot capture.

## Userspace side

[userspace-consumers.tsv](userspace-consumers.tsv) inventories the proprietary consumers:
`android.hardware.camera.provider`, cameraserver/camerahalserver and MediaTek camera
services (AOV, ATMS, BG service, CCAP, ISP HAL, postproc and UI event), plus their vendor
libraries. Their presence proves packaging, not successful use of every kernel endpoint.
CameraProvider/HAL policy, 3A/tuning, calibration interpretation and stream configuration
remain owned by `CAMERA-HAL-ISP` and are not reconstructed here.

## Buffer and control semantics established statically

The accepted source contains the stock media-request/VB2 lifecycle, DMA/IOMMU mappings,
HCP shared/tuning buffer handling, CMDQ packet submission, poll/fence paths, job recovery,
remoteproc/RPMsg transport, and private ioctl handlers. Exact UAPI layouts are preserved
because all module code/data, exported ABI, KCFI and relocation targets are accepted.
This is **static implementation equivalence**, not an execution result.

## Required on-device acceptance

1. load all expected modules with no unknown symbols, KCFI trap or probe deferral loop;
2. capture `dmesg`, `/sys/kernel/debug/devices_deferred`, media topology and `/dev` nodes;
3. enumerate all four camera IDs and verify sensor ID, EEPROM/VCM/OIS/flash ownership;
4. boot CCD/CCU firmware and confirm RPMsg endpoints and clean stop/restart;
5. open CameraProvider, configure preview/still/video and exercise front/rear switching;
6. stream RAW/CAMSV/MRAW and IMG_SYS paths with DMA/IOMMU/CMDQ fault monitoring;
7. exercise AIE, PDA and any board-bound DPE path; validate timeout/recovery/close races;
8. verify suspend/resume, repeated open/close, thermal/performance and camera kill paths;
9. compare capture quality, metadata, 3A convergence and calibration against stock.

Until those tests run, probe, streaming, image quality, performance and firmware execution
remain **NOT TESTED**, not inferred from `status = "okay"` or byte-level module parity.
