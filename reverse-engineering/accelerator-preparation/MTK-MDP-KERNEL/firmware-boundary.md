# Firmware and dependency ownership — MTK-MDP-KERNEL

## 1. No firmware is owned, loaded or reconstructed here

Neither MDP nor MML loads a firmware image. There is no `request_firmware`, no reserved
firmware memory region and no image in `/vendor/firmware` attributable to these four
modules. The "`-fw`" objects inside `mtk-mml.ko` (`mtk-mml-rsz-fw.o`,
`mtk-mml-pq-birsz-fw.o`, `mtk-mml-fg-fw.o`) are **C coefficient/table code compiled into
the module**, not downloadable firmware; they are byte-identical to stock like everything
else.

## 2. Coprocessor messaging that does exist

| path | mechanism | owner |
|---|---|---|
| MML → SSPM/TinySys | `mtk-mml-scmi.o`: `get_scmi_tinysys_info()`, then `scmi_tinysys_common_set(ph, feature_id, 3, uid, 0,0,0)` where `feature_id` is read from the SCMI device's `scmi-mminfra` property and `uid = 1` (MML; `0` is reserved for MDP). Used to tag MMINFRA users. | `tinysys-scmi` (TINYSYS / SCMI owner) |
| MDP → VCP | `mdp_common.c` calls `cmdq_vcp_enable()` and `mtk_mmdvfs_enable_vcp(true/false, VCP_PWR_USR_MDP)`; `cmdq_helper_ext.c` places read-back slots in the VCP-shared buffer (`cmdq_get_vcp_buf`, `vcp_iova_base`). | CMDQ (`mtk-cmdq-drv-ext`) and `mtk-mmdvfs-v3`; the VCP firmware itself is the VCODEC/VCP owner's and stays proprietary |
| both → GCE | CMDQ packets executed by the GCE hardware queue engine | `mtk-cmdq-drv-ext`, `cmdq-platform-mt6878`, `cmdq_helper_inf` |

So the only firmware interaction is *indirect*: MDP asks CMDQ/MMDVFS to power and use VCP
shared memory, and MML sends one SCMI "set user id" message to TinySys. No message format
of a proprietary processor was reverse engineered, and no firmware blob was touched.

## 3. Dependency ownership (none transferred to this component)

| dependency | what MDP/MML uses it for | retained owner |
|---|---|---|
| `mtk-cmdq-drv-ext`, `cmdq-platform-mt6878` | packet build/execute, thread control, event wait/clear, VCP buffers (78 exports) | CMDQ/GCE owner |
| `cmdq_helper_inf` | legacy MDP callback registration, client table, first-error dump (8 exports) | shared CMDQ helper owner (own module, loaded just before `mdp_drv`) |
| `cmdq-sec-drv` | **not used** — secure path compiled out | GZ-TZ-SYSTEM |
| `mtk_sync` | MML output fences / timeline (3 exports) | DRM/sync owner |
| `system_heap` | dma-buf naming/allocation (`mtk_dma_buf_set_name`) | DMA-BUF heaps owner |
| `iommu_debug` | `mtk_iommu_register_fault_callback` | IOMMU owner |
| `mtk-icc-core` | `of_mtk_icc_get`, `mtk_icc_set_bw` — SMI/DRAM bandwidth | MMQoS/ICC owner |
| `mtk-smi-dbg` | `mtk_smi_dbg_dump_for_mml`, `mtk_smi_dbg_hang_detect` | SMI owner |
| `mtk-mmdvfs-v3` | `mtk_mmdvfs_enable_vcp`, `mmdvfs_clk` handle | MMDVFS owner |
| `mtk_slbc` | `slbc_request/release/power_on/power_off` — SLB cache for MML paths | SLBC owner |
| `mmprofile` | tracing events | MMP owner |
| `aee_aed` | exception/warning reporting | AEE owner |
| `tinysys-scmi` | SCMI handle (above) | TinySys owner |
| `clk-common` | `mtk_clk_simple_probe`, `mtk_clk_gate_ops_setclr` for the MDPSYS gates | MediaTek clock-common owner |
| `mediatek-drm` | *consumer*, not provider: calls `mml_drm_*` | MEDIATEK-DRM (already DONE) |
| `mtk_dpc` | *consumer*: depends on `mdp_drv_mt6878.ko` and registers via `mdp_dpc_register` / `mml_dpc_register` | display power-control owner |

Only the **export ABI** of each provider was verified (111/111 CRCs regenerated from
public source — see [abi-parity.md](abi-parity.md)). No provider module was rebuilt,
shipped, re-owned or modified by this component.

## 4. Relationship to the other reconstructed accelerators

* **MTK-VCODEC-KERNEL (DONE)** — no symbol, header or object is shared. The only common
  ground is infrastructural: both are CMDQ/SMI/IOMMU/MMQoS clients, and MDP's VCP power
  calls go through the same `mtk-mmdvfs-v3`/VCP plumbing the codec uses. A decoded video
  frame reaching MML is a dma-buf hand-off at the Android layer, not a kernel ABI edge.
* **MALI-GPU-KERNEL (DONE)** — no shared symbol. GPU-produced surfaces reach MML as
  dma-buf handles through the display/HWC path.
* **APUSYS-NPU-KERNEL (DONE)** — no shared symbol. The MML DT does carry a GCE event
  `event-apu-start` (0x29e), i.e. a *command-queue* rendezvous point, not a kernel API.
* **CAMERA-ISP-KERNEL (PARTIAL)** — distinct hardware (IMGSYS), distinct registers; no
  shared symbol. ISP output reaches MML as dma-buf.

No ownership was moved in either direction.

## 5. Proprietary, deliberately untouched

MML/MDP picture-quality algorithms and tuning data in vendor userspace
(`vendor.mediatek.hardware.mmlpq`, `pq_aidl-impl.so`, `libaispq.so`, and the
`mediatek,mml-tuning-*` consumers for HDR/AAL/TDSHP), plus all signed coprocessor
firmware. None of it is required for, or affected by, the kernel-level parity proved here.
