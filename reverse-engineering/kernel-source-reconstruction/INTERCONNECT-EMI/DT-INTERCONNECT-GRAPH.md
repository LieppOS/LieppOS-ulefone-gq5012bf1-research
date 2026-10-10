# GQ5012BF1 typed interconnect / IOMMU / SMI graph

Inputs are the existing selected stock merged DTB and saved live-devicetree archive;
SHA256 identities are in contract-validation.json. No phone connection or new capture.
The custom binary parser is crosschecked with551 independent fdtget operations;1152
selected source/controller/client properties match live exactly. No numeric scalar is
interpreted as a phandle merely because it happens to equal one.

## Two separate provider namespaces, same property name

| Provider | Handle | Cell rule | Interface | Node addressing |
|---|---|---|---|---|
| /interconnect, mediatek,mt6878-mmqos |0x60|#mtk-interconnect-cells1|of_mtk_icc_get / mtk_icc_set_bw|encoded IDs in166-record table|
| /soc/dvfsrc@1c00f000 |0x16|#interconnect-cells1|of_icc_get / icc_set_bw|onecell indices in38-entry EMI table|

Both use the DT **interconnects** property; private cells are not a separate
mtk-interconnects property. Every path has source/destination specifiers and a name.
97 paths resolve:87 private multimedia and10 Linux EMI. All are enabled in this board
DT; this is configuration, not proof of successful get/set or active votes.

/interconnect requests normal mmsys8→ddr0 and HRT mmsys26→hrt_ddr25 under names icc-bw
and icc-hrt-bw. It also supplies21 larbs and1 common through explicitly typed
mediatek,larbs-supply/commons-supply properties; they are device references, not voltage
regulator supplies. Clock mm, VMMRC/MMINFRA/DVFSRC physical ranges, required-opps and
SMI clock/power dependencies are preserved in DT-PROPERTIES/RESOURCE-REFERENCES.
VMMRC and DVFSRC physical base scalars are not phandles or live register readings.

## Client → IOMMU/SMI → MMQoS → EMI relationships

Complete paths: DT-INTERCONNECT-PATHS.tsv, with consumer compatible, provider, IDs,
node names, full node chain, larb/supplier, interface, status and evidence level.
IOMMU records preserve full raw arguments and independently decode table/domain/larb/
port fields using the public MTK_M4U layout. They are not interchangeable with EMI IDs.

- Display/OVL: larbs0/1 and virtual39, then respective common ports/common0.
- MDP/MML RDMA/WROT: larb2 master-port votes and MDP endpoint declarations.
- VDEC: logical larbs4/5; VENC/JPEG:7/8. Only4/7 have physical board suppliers.
- IMG/ISP: larb-level votes including9/15/22/28; camera RAW/YUV/MRAW/CAMSV use
  exact132-port-table matches across13/14/16/17/25/29/33/34; CCU uses30.
- Modem DPMAIF: Linux netsys index36→DDR0, not a fictitious multimedia larb route.
- CM-mgr/FPSGO/DVFSRC helpers use declared Linux debug/normal/HRT paths.
- GPU, APUSYS/NPU, storage and Wi-Fi/Bluetooth do not declare a board ICC property
  here. Their EMI table entries and possible programmatic requests remain
  STOCK_BINARY_IMPLEMENTATION / SOURCE_REFERENCE_ONLY, not proven board routes.

133 static IOMMU specifiers:112 exact MMQoS master-port/physical-larb matches;5 known
larb-only relationships with no compiled leaf;16 outside the MMQoS/board-SMI mapping.
Absence of a leaf does not invalidate a separately declared larb-level vote. APU's
separate IOMMU table/domain is not forced into the multimedia topology.

## Evidence levels and limits

**STOCK_BINARY_IMPLEMENTATION**: exact decoded tables and target code.
**ENABLED_IN_STOCK_DT**: resolved and enabled provider/consumer references.
**SOURCE_REFERENCE_ONLY**: uninstantiated table/API capability or other-provider logic.
**PROVEN_RUNTIME**: requires actual probe/request evidence, not a load-list entry; no
active path or bandwidth request is assigned this level in this offline graph.
**UNKNOWN**: unresolved/nondeclared GPU/APU/storage route, actual channels/frequency,
current parameter state, successful binding or firmware execution.

Recorded module loading remains a separate audit fact. Matching saved live properties
is live-DT configuration evidence, not on-device exercising of the reconstructed code.
