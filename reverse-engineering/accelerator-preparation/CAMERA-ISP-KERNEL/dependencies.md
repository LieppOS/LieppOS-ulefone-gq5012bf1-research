# Dependencies and singleton ownership — CAMERA-ISP-KERNEL

**Owned and closed here:** exactly the nineteen modules in
[module-ownership.tsv](module-ownership.tsv). Dependencies are references, never implicit
additional ownership.

## External prerequisites

* exact GKI/KMI baseline (`6.1.115-android14-11-g945dff7bc1bf`);
* CMDQ, IOMMU/SMI/MMQoS, memory heaps, clocks, regulators and VCP/tinysys providers;
* camera sensor/EEPROM/VCM/OIS/flash/LDO components under their existing DONE owners;
* retained CCU/CCD firmware and proprietary CameraProvider/HAL userspace.

The complete resolved stock symbol graph remains in
[../dependency-edges.tsv](../dependency-edges.tsv). Build acceptance regenerates 97 vendor
provider CRCs from public source and explicitly retains ten non-public stock-provider export
CRCs; see [abi-parity.md](abi-parity.md).

## Cycles and historical dependency names

Camera packages have legitimate internal cycles and package-level modpost coupling. The
reproducible build uses package scopes and the stock sibling symvers set, then verifies the
assembled nineteen-module graph.

`modules.dep` is transitive, and `.modinfo depends=` can preserve historical names. In
particular, stock names `mtk_ccu`/`mtk_ccu_mssv` do not correspond to files in the device's
457-module universe; matching exports/CRCs are supplied by `mtk_ccuv.ko`. Do not invent
provider modules or treat a dependency string as stronger than the resolved symbol graph.

## Boundary

`CAMERA-HAL-ISP` remains PARTIAL for HAL/3A/tuning/calibration and firmware algorithms.
This child is DONE for its normal-world kernel scope without taking ownership of those
artifacts or of already-closed camera peripherals.
