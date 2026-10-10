# Device-tree IOMMU port contracts

Complete per-client/per-cell ledger: evidence/hardware/DT-IOMMU-PORTS.tsv, both static
and saved live operands. Each row includes node path/compatible/status, source specifier
index, exact provider, full ID, table/domain/larb/port, source-proven aperture/type,
register/IRQ/power-domain property cells, stock OF-alias driver candidates and explicit
runtime UNKNOWN. Related supplier phandles are resolved only using typed property arities.
Client pseudonodes may have no register or IRQ; ABSENT is not a guessed inherited resource.
OF alias candidates are not successful-probe evidence; some compiled OF tables lack
MODULE_DEVICE_TABLE aliases. Controller driver source match is established independently.

## One-cell encoding and selection

MTK_M4U_PORT_ID uses table[21:20], domain[19:16], larb[10:5], port[4:0].
The full cell survives fwspec; lower larb/port bits alone do not select the DMA domain.
Both providers declare #iommu-cells=1; DT table_id matches the compiled platform tab_id.
MT6878 GET_DOM_ID_LEGACY selects first fwspec's domain, bounds-checked against6 MM or4
APU regions. Actual iommu_group allocations, attachment success and TTBR values remain
unknown. APU virtual larb42/port0,1 are valid translation specifiers without a MMQoS leaf.

| Configured client family | Positive translation evidence |
|---|---|
|Camera RAW/YUV/CAMSV/MRAW/PDA/AIE/image/CCD|MM table0, predominantly domain0; explicit larb/ports in ledger|
|CCU0/CCU1|MM table0 domains2/3, larb30 ports0/1 and2/3|
|VDEC|MM table0 domain5, larb4 ports0..11|
|VENC/JPEG|MM table0 domain0, larb7 multiple explicit ports|
|Display|MM table0 domain0, larbs0/1; precise overlay/postmask/WDMA cells|
|MDP/MML|MM table0 domain0, larb2 including RDMA/WROT/config clients|
|GCE CMDQ|MM table0 domain0, larb41 ports0/1|
|VCP and four IOMMU pseudo-clients|MM table0 domain4, larb41 port2|
|APUSYS/APUMMU/MDLA/code/logging/SAPU clients|APU table1 domain2, virtual larb42 port1 (eight cells)|
|APU memory data client|APU table1 domain0, virtual larb42 port0 (one cell)|
|Heap region pseudo-clients|their exact explicit controller/cell; no allocated-buffer proof|

The machine ledger, not this family summary, is authoritative for duplicate ports,
client counts and resource ranges. Multiple clients or pseudo-clients reuse cells; this
is not a count of simultaneously executing engines.133 enabled cells/50 client nodes.

## Negative/non-claims

Mali GPU-local MMU reconstruction does not prove a MediaTek M4U link. No positive GPU
node iommus property in these operands establishes that route. Likewise USB, UFS/MMC,
connectivity/modem DMA routes must not be inferred from generic source possibilities,
module imports, absent properties or MMQoS/EMI entries. Existing GPU/APU/media research
is reused, never overwritten. Table/domain/bank identities are distinct responsibilities.

No active DMA map, translation fault, transfer, calibration or physical resource access
was performed. Static/live correspondence establishes configured contracts only.
