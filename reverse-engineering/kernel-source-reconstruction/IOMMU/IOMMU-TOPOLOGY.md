# Actual MT6878 controller/domain topology

Evidence: offline stock DTB/DTBO merge, saved live devicetree.tar, complete stock ELF,
unchanged compiled source and independently verified compiler field layouts. Machine
ledgers: evidence/hardware/{DT-IOMMU-CONTROLLERS,PLATFORM-CONTRACTS,IOVA-REGIONS,
DT-IOMMU-PORTS,DT-RESOURCE-REFERENCES}.tsv. No current device access.

| Controller | Compatible | Register range | Raw GIC specifier | Power provider/domain | Table |
|---|---|---|---|---|---:|
|/soc/iommu@1e802000|mediatek,mt6878-disp-iommu|0x1e802000+0x1000|0,278,4,0|/power-controller@1c001000 (mt6878-scpsys),7|0|
|/soc/iommu@19010000|mediatek,mt6878-apu-iommu0|0x19010000+0x1000|0,597,4,0|same provider,21|1|

Raw DT IRQ cells are not guessed Linux IRQ numbers. Source driver is mtk-iommu /
mtk_iommu.ko for both. Recorded module loading exists; per-node successful binding,
active interrupts, TTBR, DMA traffic and allocated runtime group IDs remain UNKNOWN.
Four auxiliary banks each are configured: MM0 banks1..4 at1e803000..1e806000 with
SPI indices279..282; APU0 banks1..4 at19011000..19014000 with598..601, each0x1000.
Their common-disp/common-apu-iommu0-bankN compatibles belong to **iommu_secure**, not
extra mtk_iommu-owned controller binaries. Bank IDs are not domain or table IDs.

## Compiled region policy (STOCK_BINARY_IMPLEMENTATION)

| Table/domain | Aperture start | Size | Type | Configured specifiers |
|---|---|---|---|---:|
|MM0/0|0x1000|0x3fffff000|NORMAL|103|
|MM0/1|0x106000000|0x02000000|NORMAL (LK-reserved)|0|
|MM0/2|0x108000000|0x04000000|PROTECTED (CCU0)|2|
|MM0/3|0x10c000000|0x04000000|PROTECTED (CCU1)|2|
|MM0/4|0x110000000|0x60000000|PROTECTED (video-up)|5|
|MM0/5|0x170000000|0x90000000|NORMAL (VDEC)|12|
|APU(table1)/0|0x1000|0x3fffff000|NORMAL (data)|1|
|APU(table1)/1|0x1000|0x1ffff000|SECURE|0|
|APU(table1)/2|0x40000000|0xc0000000|NORMAL (code)|8|
|APU(table1)/3|0x106000000|0x02000000|NORMAL (LK-reserved)|0|

Counts describe configured DT cells, not allocations or distinct running engines.
Normal regions contain nested reserved/protected apertures; source get_resv_regions
reserves strictly contained regions. A domain ID does not prove a separate page table:
source shares an existing iop/TTBR within its hardware list. No security/isolation claim
is made beyond the compiled policy/host secure interface. APUs use their separate list.

133 enabled specifiers across50 client nodes; all agree with earlier interconnect decode.
MM flags0x11c7310 select legacy domain IDs,34-bit IOVA/35-bit TTBR, secure host interfaces,
SKIP_CFG_PORT, SMI sub-common and same-subsystem policy. APU flags0x1443900 select
legacy domains,34-bit IOVA/35-bit TTBR, secure host interfaces, LINK_WITH_APU and
PM_OPS_SKIP. Invalidate selector0x2c, normal domain0, mau_count4. HAS_BCLK and
IOMMU_MAU_EN are absent: descriptor counts/names are not active clock/MAU evidence.

## Evidence labels

- **ENABLED_IN_STOCK_DT:** all133 configured cell relationships and their controller/region policy.
- **STOCK_BINARY_IMPLEMENTATION:** complete accepted host code/data, flags/ops/region descriptors.
- **PUBLIC_SOURCE_CAPABILITY:** other SoC match entries, SMMUv3/debug/test possibilities not instantiated.
- **PROVEN_RUNTIME:** the saved capture proves module loading only, not a particular active DMA route.
- **UNKNOWN:** successful controller/client attachment, actual mappings/group isolation, firmware responses,
  power/IRQ state or routes absent from positive evidence.

96 selected nodes:1387 shared/static properties identical against saved live DT and independently
checked by fdtget. Two live-only display properties (disp_plat_dbg_addr / disp_plat_dbg_size,
0 /0x2000000) remain separately recorded. They do not establish a mapped buffer or transfer.
