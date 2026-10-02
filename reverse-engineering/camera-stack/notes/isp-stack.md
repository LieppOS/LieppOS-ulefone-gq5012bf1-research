# MT6878 ISP stack (ISP7sp) — kernel and userspace split

## Kernel (vendor_dlkm unless noted; `../kernel-camera-modules.tsv`)

| block | module | donor dir (Nothing MT6878) | name coverage |
|---|---|---|---|
| sensor interface (seninf, 4 CSI ports, C/D-PHY) + RAW/YUV/MRAW/CAMSV camsys | `mtk-cam-isp7sp.ko` | `mtkcam/camsys/isp7sp/cam` (`mtk_cam-seninf-drv.c`, `mtk_cam-plat-mt6878.c`, `mtk_cam-meta-mt6878.h`) | 1019/1044 |
| CCD remoteproc + rpmsg (camsys co-processor channel) | `mtk_ccd_remoteproc.ko`, `ccd_rpmsg.ko` | `mtkcam/camsys/{remoteproc,rpmsg}` | 23/23, 28/28 |
| CCU (3A/AE co-processor) | `mtk_ccuv.ko` (+ vendor_boot `mtk_ccu_mssv`) | `mtkcam/ccusys` / `drivers/remoteproc` | 39/39 — firmware `ccu.img` proprietary |
| P2 imgsys (DIP/TRAW/LTRAW/WPE/OMC/ME/PQDIP) | `mtk_imgsys_v4l2`, `mtk_imgsys_isp7sp`, `mtk_imgsys_cmdq`, `mtk-ipesys-me` | `mtkcam/imgsys`, `…/platforms/isp7sp` | 167/170, 69/71, 157/160, 12/12 |
| HCP (host/co-processor shared memory, tuning buffers) | `mtk_hcp.ko` | `mtkcam/mtk-hcp` | 164/164 |
| FD / AIE | `mtk_aie.ko`, `mtk_aie_debug_7sp_2.ko` | `mtk-aie` | 113/113, 4/4 |
| DPE (depth) | `camera_dpe_isp7sp.ko` | `mtkcam/mtk-dpe/isp_7sp` | 94/94 |
| PDA (PDAF accelerator) | `pda_drv_mt6878.ko` | `cameraisp/pda` | 31/31 |
| VMM regulator/notifier (ISP vcore) | `mtk-vmm-isp71-regulator`, `mtk-vmm-notifier` | `drivers/regulator`, `misc/mediatek/vmm` | 13/18, 3/3 |
| clocks | vendor_boot `clk-mt6878-cam/img/ccu` | device_modules clk | — |
| SMI/IOMMU/MMDVFS/MMQOS/CMDQ | vendor_boot | device_modules | — |

"name coverage" = stock FUNC symbols whose identifiers exist in the donor
tree (triage, not parity). Only `imgsensor` and `dw9781c` were parity-built
in this pass.

DT topology (PROVEN): `seninf-top@1a00e000` with `seninf-csi-port-0..3`
(nvmem `rg_csi` efuse cells; port 0 `dphy-settle-delay-dt=0x11`; ports 1/2
`hs-trail-parameter=0x20`); `camisp@1a000000`, `cam-raw-a@1a030000`,
camsys clocks `camsys_{main,rawa,yuva,rawb,yuvb,mraw}_clk`,
`camera-camsys-ccu` → `ccu-rproc`; SMI power domains cam_vcore/main/ccu/
suba/subb; `mtk-composite-v4l2-2` ports 0..3 = main_af, main_af_cam1,
main_af_cam2, main_ois_cam1.

## Userspace ISP

* `libcam.halisp.v4l2`, `.imp.v4l2`, `.TopCtrlMgr`, `.SwTopCtrlMgr`,
  `.plugin`, `.utils`, `.TuningDataProvider(Factory)`,
  `libcam.isptuning.v4l2`, `libcam.tuningcachemgr`;
* P2: `libimgsys_{main,dip,wpe,pqdip,gce,tile,cmt,sensor,system,v4l2,
  utils,drvcommon}`, `libimgstream-drv/-custom`, `libmtkcam.featurepipe.p2g`;
* metadata/interpreter: `libmtkisp_metadata_v2/v3`,
  `libispinterpreter_mtkcam`, `libispfeature_mtkcam.v4l2`;
* AI-PQ: `libaispq`.

## Tuning boundary (PROVEN files, proprietary content)

* per sensor: `<s>_mipi_raw_tuning.so` (15–32 KB, IMX989 largest),
  `<s>_mipi_raw_IdxMgr.so` (all 10 520 B — generated index managers);
* SQLite: `tuning_DB/<s>/mt6878/ISP_param.db` (one-row `isp_all_Param`
  blob table, version 15227) + `ISP_mapping.db` (Anchor_ISO/Zoom/LV/CT …
  index tables); global `ParameterDB.db`, `top_control_data.db`,
  `sw_top_control_data.db`, `port_select.db`, ae/af/awb/flash/pd/tone/
  feature/pipeline sub-DBs;
* NVRAM defaults: `libcam.hal3a.v3.nvram.v4l2.so`, `libcustom_nvram.so`.

The SQLite containers are open (readable schema) but the parameter blobs
are MTK-proprietary binary structures; no schema/source exists locally.
