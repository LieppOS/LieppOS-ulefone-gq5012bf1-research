# CAMERA-ISP-KERNEL — PARTIAL preparation

**Purpose:** Camera ISP kernel normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL CHILD. Separate ISP/PDA/VMM normal-world kernel work from CAMERA-HAL-ISP's proprietary HAL/3A/tuning boundary. Preserve 16 existing function/data proof pairs and sensor-TU DONE closures; PDA/VMM and whole-module ABI/KCFI/relocation/B1-B2 acceptance remain unclosed.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/CAMERA-ISP-KERNEL/`. Workspace pack: `Reverse Engineer - PARTIAL/CAMERA-ISP-KERNEL/`.

**Exclusive primary kernel modules (19):** `mtk_hcp.ko`, `mtk-ipesys-me.ko`, `mtk_imgsys_cmdq.ko`, `mtk_imgsys_v4l2.ko`, `mtk_imgsys_isp7sp.ko`, `ccd_rpmsg.ko`, `mtk_ccd_remoteproc.ko`, `mtk_ccuv.ko`, `mtk-cam-isp7sp.ko`, `mtk_aie.ko`, `mtk_aie_debug_7sp_2.ko`, `camera_dpe_isp7sp.ko`, `pda_drv_mt6878.ko`, `mtk-vmm-isp71-regulator.ko`, `mtk-vmm-notifier.ko`, `imgsensor-glue.ko`, `imgsensor.ko`, `c2ps_perf_ioctl.ko`, `mtk_c2ps.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

CAMERA-HAL-ISP stays PARTIAL for proprietary CameraProvider/HAL, 3A, tuning, calibration interpretation and CCU/ISP firmware algorithms. The child owns the explicit 19-module ledger only. Keep all parent historical evidence and source material where it is; its references become historical/cross-links, not a second primary owner. CAMERA-EEPROMS/VCMS/OIS/flash/LDO and closed sensor TUs are dependencies, never restarted.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
