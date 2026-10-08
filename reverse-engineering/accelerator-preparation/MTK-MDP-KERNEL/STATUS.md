# MTK-MDP-KERNEL status — DONE

**DONE (class A).** All four owned modules — `mdp_drv_mt6878.ko`, `mtk-mml.ko`,
`mtk-mml-mt6878.ko`, `clk-mt6878-mdpsys.ko` — rebuild from **unmodified public MediaTek
ALPS source** (`5e415e059253`) and are identical to the shipped stock binaries except each
module's 20-byte GNU build-ID descriptor.

Closed axes, measured on a clean checkout: 1 347 functions, 1 171 data objects, 195
sections (layout and content), 50 589 relocations (raw **and** semantic), 494 import CRCs,
37 export CRCs with licence buckets, 34 KCFI type ids, 373 `.modinfo` records, `vermagic`,
`srcversion`, module strings, the external provider ABI (111/111 CRCs regenerated from
source) and B1 == B2 determinism including every intermediate `.o`.

* Report: [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md)
* Source recipe: [SOURCE.md](SOURCE.md) → `android_kernel_modules_mdp_ulefone_gq5012bf1`
* Rebuild procedure and transcripts: [build-reproduction.md](build-reproduction.md)
* ABI: [abi-parity.md](abi-parity.md) · Hardware: [hardware-contract.md](hardware-contract.md) · [dt-topology.tsv](dt-topology.tsv)
* Firmware/ownership: [firmware-boundary.md](firmware-boundary.md)
* Userspace: [source-to-userspace-contract.md](source-to-userspace-contract.md)
* Corrections: [stale-claims.md](stale-claims.md)

**Retained boundaries.** MML/MDP picture-quality algorithms and tuning data stay in
proprietary vendor userspace (`vendor.mediatek.hardware.mmlpq`, `pq_aidl-impl.so`,
`libaispq.so`). CMDQ/GCE, `cmdq_helper_inf`, secure CMDQ, SMI, IOMMU, MMQoS/ICC, SLBC,
MMDVFS, mmprofile, AEE, TinySys SCMI, `mtk_sync`, `system_heap` and `clk-common` keep
their own owners; only their export ABI was verified here. `mediatek-drm` and `mtk_dpc`
are consumers, not dependencies of ownership.

**Not established.** Nothing was executed on hardware: no probe, CMDQ submission, tile
pass, DMA/IOMMU translation, interrupt (SPI 868), timeout/recovery or power transition.
Runtime acceptance items are listed in
[source-to-userspace-contract.md](source-to-userspace-contract.md) §4 and require separate
authorisation.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
