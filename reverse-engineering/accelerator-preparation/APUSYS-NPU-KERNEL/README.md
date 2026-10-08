# APUSYS-NPU-KERNEL — DONE

**Scope:** the two normal-world GQ5012BF1 modules `apu_top.ko` and `apusys.ko`; proprietary firmware/algorithms and modules owned elsewhere are excluded.

Both modules are reconstructed from public source. A fresh independent checkout rebuilt them twice deterministically and matched every stock function, data object, import/export CRC, KCFI ID, relocation, section, symbol, string, and modinfo byte. Each raw installed ELF differs only in its 20-byte GNU build ID. There are zero unresolved compiled behavioral or ABI differences.

* [Source repository and build instructions](SOURCE.md)
* [Full parity result](parity-report.md)
* [Normal-world userspace/firmware contract and future runtime tests](source-to-userspace-contract.md)
* [Exact DT rows](dt-nodes.tsv) and [provider resolutions](dt-providers.tsv)
* [Stock module inventory](stock-modules.tsv), [imports](imports.tsv), [exports](exports.tsv)
* [Machine-readable reconstruction evidence](evidence/reconstruction/)
* [Corrections to preparation claims](stale-claims.md)

## Device result

The merged DT describes the MT6878 APU RV complex, APU top/power, APUMMU/IOMMU, one MDLA core, MVPU/EDMA and RPMsg/shared-memory channels. Stock loads `apu_top` immediately before `apusys`; `/dev/apusys` exposes handshake, dma-buf memory, graph command/fence, and utility ioctls to the APUware/NeuroPilot stack. This proves the exact shipped normal-world implementation and static reachability—not successful on-device firmware boot, NPU inference, performance or power behavior.

## Boundaries

`firmware/apusys.img` and proprietary APUware/NeuroPilot algorithms remain retained binaries. `sapu.ko` remains `GZ-TZ-SYSTEM`; `apu_aov.ko` is not shipped. Generic AEE, QoS, SLBC, peak-power, mrdump and IOMMU providers retain their canonical owners. No device was connected, module loaded, partition written, firmware modified or hardware command issued.
