# Dependencies and ownership — APUSYS-NPU-KERNEL

**Owned modules:** `apu_top.ko`, `apusys.ko` only.

Stock direct `modinfo` dependencies are:

* `apu_top`: `aee_aed`;
* `apusys`: `apu_top,aee_aed,mtk_slbc,mtk_qos,mtk_peak_power_budget,mrdump,iommu_debug`.

The exact import/provider/CRC graph is in `dependency-edges.tsv`. Thirteen external vendor CRCs needed by the pair are regenerated from public 5e41 provider source and checked on every build. GKI CRCs come from official CI 12901745 metadata. The accepted build therefore does not depend on copied stock provider objects or fabricated symvers.

Ownership remains unchanged: shared AEE, IOMMU, QoS, SLBC, peak-power, mrdump, SSPM/SCMI and power providers stay with their canonical components. `sapu.ko` stays `GZ-TZ-SYSTEM`; `apu_aov.ko` is not in the stock module inventory. Signed `apusys.img` is retained firmware, not a kernel source target. Camera AIE/FD remains camera-owned.

Stock load order and cross-partition depmod reachability are recorded in `source-to-userspace-contract.md`. Transitive `modules.dep` edges do not silently expand this component.
