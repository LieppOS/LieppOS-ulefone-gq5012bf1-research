# IOMMU, SMI and MMQoS: distinct contracts

Reuse: ../INTERCONNECT-EMI/evidence/hardware/ has166 compiled MMQoS nodes,24 logical
larbs,132 masters,97 configured bandwidth paths,133 IOMMU cells and22 private supplier
links. Its accepted source/ABI work is not rebuilt or modified. IOMMU's map-topology.py
independently resolves every133 cell to one of two controllers and a compiled region,
then joins the earlier decoded larb/port/MMQoS entries in SMI-MMQOS-JOIN.tsv.

- **IOMMU** allocates/attaches DMA domains via generic infrastructure, translates addresses,
  supplies region/TTBR policy and invalidates TLBs. GKI iommu-dma/io-pgtable handle IOVA/PTE
  allocation and generic synchronization; debug iova journals are separate bookkeeping.
- **SMI larbs/common/sub-common** provide memory-client interconnect, register/clock/PM
  paths and component binding. MM controller lists21 physical DT larbs, not MMQoS's24
  logical nodes. It traverses the last larb's supplier chain through sub-common to common;
  runtime device links connect SMI common and IOMMU. APU uses mediatek,apu-power instead,
  linked to /soc/apusys-rv@190e1000. These links are not direct imported module symbols.
- **MMQoS/private ICC** supplies bandwidth votes/routes, not address translation. Its IDs
  carry node type; they cannot be used unmodified as IOMMU full table/domain/larb/port IDs.
  Low larb/port joins are diagnostic correspondences, not proof of active DMA or votes.

MM SKIP_CFG_PORT means this driver's local port-enable/bank-bit routine does not execute
those writes for MT6878. Do not assume a complete port-setup story solely from SMI binding
or generic source. APU's virtual42 ports and CMDQ41 ports without a compiled bandwidth
leaf remain valid IOMMU DT links; they do not require invented MMQoS nodes.

A literal null mediatek,smi-supply exists at /smi-larb11@15230000; typed evidence records
NULL_PHANDLE / UNKNOWN supplier. This is not a decoded route or reason to manufacture a
provider. Other configured supplier links and controller's last-larb traversal are separate.

## Real completed-component ABI

Seven stock import slots into **separate iommu_debug**:
- APUSYS-NPU-KERNEL/apusys: mtk_iommu_update_pm_status;
- MDP/mdp_drv_mt6878, VCodec dec+enc, Camera mtk-cam-isp7sp / mtk_aie_debug_7sp_2 /
  mtk_imgsys_v4l2: mtk_iommu_register_fault_callback (six occurrences).

Source-generated CRC/licence and callee KCFI agree with each stock boundary; available
consumer KCFI IDs and actual relocation targets agree. See ACCELERATOR-IOMMU-BOUNDARIES.tsv.
These completed modules are not rebuilt and their sources/statuses are unchanged. GPU-AI
auxiliary/Mali have no invented direct owned-target import; the owned mtk_iommu's two
exports have zero direct stock reverse import slots. Generic iommu_ops dispatch is distinct.

The18 owned imports into iommu_debug(10), iommu_secure(6), mtk-smi-dbg(2) are regenerated
from real objects. No source-class promotion for those providers. Power-domain/clock/PM
compatibility is distinct from callback ABI, address mappings and vote semantics. Runtime
page tables, DMA cache behavior, device links and stream/vote/fault activity remain deferred.
