# Complete stock ELF and ABI parity

Full ledgers: FUNCTION-PARITY.tsv, DATA-PARITY.tsv and evidence/acceptance/{sections,
relocations,abi}-parity.tsv. All48 function symbols/88 data symbols have identical section,
offset, size, ordering and bytes (BSS layout identical); every1220 raw/semantic relocation
matches. Complete-file comparison also covers ELF headers, branch/call targets, operations/
platform/region descriptors, symbol/string tables, section offsets/flags/alignment and padding.

98 import CRCs =80 public GKI12901745 core slots +18 real vendor provider slots.
External source definitions are compiled, not declarations or copied stock implementations.
Genksyms #SYMVER and actual ___ksymtab_gpl sections assert CRC and GPL licence category;
all18 real source callee KCFI prefix words match stock provider function entries.
Exact source signatures and command witnesses: evidence/acceptance/PROVIDER-ABI-WITNESSES.tsv.
Three verbatim compressed compiler .cmd records preserve inputs/provenance.

| Vendor producer | Required slots | Source |
|---|---:|---|
|iommu_debug|10|drivers/misc/mediatek/iommu/iommu_debug.c|
|iommu_secure|6|drivers/misc/mediatek/iommu/iommu_secure.c|
|mtk-smi-dbg|2|drivers/misc/mediatek/smi/mtk-smi-dbg.c|

Provider names retain actual producer filename spelling so modpost naturally reproduces
**depends=iommu_secure,iommu_debug,mtk-smi-dbg**. Their source classifications remain D;
exact required ABI does not certify every provider function/data or firmware.

Two owned exports: **mtee_iova_to_phys** (CRC0x97441009),
**mtk_iommu_dbg_hang_detect** (CRC0xcbfd72d6), both EXPORT_SYMBOL_GPL.
The authoritative dependency graph has **zero direct stock reverse import slots** into
these two exports. This is not no-consumer proof: generic GKI iommu_ops dispatch, DT
registration/attachment, function pointers and firmware host requests are different axes.
Seven actual completed accelerator imports into separate iommu_debug are checked in
ACCELERATOR-IOMMU-BOUNDARIES.tsv. All caller CRCs, observed relocations, callee KCFI words
and available absolute consumer IDs agree; no execution or provider promotion inferred.

Two absolute KCFI IDs and all in-function entry prefixes/traps match through code/ELF parity.
.modinfo description, GPL v2 licence, name and depends are exact. There are no OF alias
or srcversion records in this stock target. Lack of MODULE_DEVICE_TABLE aliases does not
remove the compiled OF match table. Stock vermagic is:
`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`.
No appended stock/rebuilt signature is present. Future enforcing boot signing is separate.

## Raw differences and permitted normalization

Stock SHA256:8398de841de67529967c09b144292faa88ca86685df110e05f46b4fb1d8b75c5.
Accepted clean build SHA256:3be70f137c3bebd77378d7020edb19a9f54fd91da4ecc211d78137c2ce14c094.
Both107408 bytes. All20 differences are within GNU note descriptor **0xea50+20**;
stock aa01e4f59dd28bff6a0895930fa9dc97045b9bec,
rebuild7984dd20ca3679589a51999abf1f1028d3ff7684.
Normalized SHA256:7f88162b28c3f45fdab0a38d29d12a7f2b9c24a40f35ccee46dde9a6b2dac4b0.
Parser asserts GNU owner, type3,20-byte descriptor and exact note extent. No other byte
normalization, compiler-only allowance, semantic exception or unresolved behavior.
llvm-strip --strip-debug is stock packaging, not a code/ABI patch.14 verifier mutations
check pristine/ID acceptance and instruction/data/CRC/metadata/relocation/string/symbol/
KCFI/signature corruption rejection. Every case passes on disposable copies.
