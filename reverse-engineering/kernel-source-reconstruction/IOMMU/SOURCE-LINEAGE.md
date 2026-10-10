# Source lineage, authoritative scope and donor selection

Canonical audit before task: research05313ab,458 identities,128 certified /330 remaining.
Queue head is **drivers/iommu: mtk_iommu.ko only**. Original four-module IOMMU inventory
was a broad family list, not authorization to certify another source group. All four
stock identities are frozen in evidence/inventory/audit-baseline-four.tsv and stock-inventory.json.
No same-filename duplicate or multi-partition binary exists for these four identities.

| Module | Original class/owner | Actual source project | This task |
|---|---|---|---|
|mtk_iommu|D / COVERED-GENERIC|drivers/iommu|one owned source-certified target|
|iommu_debug|D / COVERED-GENERIC|drivers/misc/mediatek/iommu|real provider object only; D unchanged|
|iommu_secure|D / COVERED-GENERIC|drivers/misc/mediatek/iommu|real provider object only; D unchanged|
|iommu_test|D / COVERED-GENERIC|drivers/misc/mediatek/iommu|reference identity/source only; D unchanged|

The third project in the pre-task queue groups debug/secure/test. A later coordinated
closure is justified: common native Kbuild/config/header contracts, secure bank DT and
fault/PM callback APIs used by the main driver and seven accepted accelerator consumers.
It is not performed here. iommu_test's two-function stock ELF and only module_layout
import do not establish that dangerous fault/DMA tests are enabled or that it is removable.

Full per-file donor blob comparison: evidence/inventory/source-candidate-blobs.tsv.
Compiled source is proven public ALPS5e41, not automatically the newer957dac candidate.
Both commits are pinned and their actual file identities are preserved.957dac supplies
vendor Kconfig/defconfig only. Successful compilation or candidate-name correspondence
was never used as stock proof; full ELF acceptance selects the donor empirically.

Build/verifier lineage: accepted INTERCONNECT-EMI e03fc92, with target scope narrowed,
three real provider goals selected and explicit18 CRC/licence witnesses. Old regulator/
clock/storage/bootstrap logic remains immutable-input infrastructure, not reconstructed
again. The full-body verifier's original export parser is retained: __crc_name offsets
prove exact export CRC/licence, including data; positional function/export pairing is
not accepted. Research mapping machinery derives from existing offline FDT helpers,
then independently validates MT6878 platform/domain tables and all133 earlier specifiers.

No complete accelerator package is modified. No new workspace component/owner is invented;
source-audit group IOMMU is not a PARTIAL→DONE taxonomy promotion.
