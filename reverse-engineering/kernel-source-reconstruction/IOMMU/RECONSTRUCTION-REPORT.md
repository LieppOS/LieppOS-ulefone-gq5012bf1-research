# GQ5012BF1 / MT6878 IOMMU source reconstruction

## Scope and result

**mtk_iommu.ko only; complete stock acceptance, zero unexplained behavior-bearing differences.**
The current queue authorizes CANDIDATE:device_modules:drivers/iommu (one D identity).
The original four-name IOMMU inventory is not a single source/ownership project:
iommu_debug, iommu_secure, iommu_test belong to drivers/misc/mediatek/iommu.
All four are COVERED-GENERIC / N/A, not a registered PARTIAL component. No taxonomy
promotion. The three helper modules stay D; real debug/secure provider objects are
compiled for ABI witnesses, not delivered/certified modules. A coordinated later
misc-IOMMU closure is justified by shared headers and real consumer ABI, not by
silently broadening this assignment. The queue's subsequent CMDQ priority is preserved.

Maintained repository: android_kernel_modules_iommu_ulefone_gq5012bf1.
Accepted commit: **110251e6d0983ea4a8a0a9fadd104aeaacb229b9**.
Full immutable pins, content/tree identities and exact stock identities are retained.
One Kbuild-only target-scope patch; **no C/header behavior patch** or ELF byte replacement.

| Module | Function symbols exact | Data objects exact | Imports / exports | KCFI absolute IDs | Relocations | Residual |
|---|---:|---:|---:|---:|---:|---|
| mtk_iommu.ko |48/48|88/88|98/2|2/2|1220/1220|20-byte GNU build ID only|

The full107408-byte packaged ELF differs at only0xea50..0xea63. Raw offsets and both
IDs/hashes are preserved before normalization. Section layout, symbol/string tables,
all function instructions/ordering, branch/call relocations, initialized data/BSS layout,
platform/region/ops tables, CRC/licence and module metadata are exact. No compiler-only
or semantic-equivalence exception. There is no stock srcversion record or appended
signature; neither is invented. Stock vermagic is reproduced verbatim.

Independent committed fresh clone, immutable PUBLIC input mirror, development tree
unavailable: complete B1/B2 regeneration matched raw/stripped modules, both target objects,
three provider objects, symvers/witnesses/config/source trees. Stock acceptance separately
passes. **14/14 ELF verifier mutations pass.** Bundle and checksums preserve the recipe.

## Actual implementation

See IMPLEMENTATION-CONTRACT.md. Only DMA domains are accepted. GKI ARM_V7S io-pgtable
handles PTE allocation/map/unmap; generic IOMMU-DMA allocates IOVAs. This module supplies
attachment, DT decode, group/aperture policy, TLB/IRQ/probe/PM/secure-host integration.
It is not a generic SMMUv3 implementation, a GPU-local MMU, secure firmware, or proof of
independent page tables for every domain. Platform flags select behavior precisely.

## Actual board contracts

Two configured controllers: MM0@1e802000 / APU0@19010000, with four auxiliary banks each.
**133 enabled DT specifiers /50 clients** decode to table0 domains0/2/3/4/5 and table1
(domains0/2). Ten compiled MT6878 region entries and both platform descriptor layouts,
scalar defaults and relocation pointers are independently checked against compiler-expanded
source. MMQoS's prior133 specifiers match exactly; translation is not bandwidth voting.

96 selected nodes /1387 shared/static properties have zero byte differences against
saved live DT and1387 independent fdtget checks. Two live-only display debug properties
are retained explicitly, not discarded or interpreted as active DMA. Linux-added `name`
is descriptive unflattening metadata. Null SMI supply at larb11 remains a null supplier,
not an invented route. See typed ledgers and STALE-CLAIMS.md.

Mali's GPU-local MMU does not establish this driver as its translator. GPU/USB/storage/
connectivity require positive bindings; absence of a DT iommus property is not a runtime
exclusion. APU logical42 ports do resolve this IOMMU despite lacking MMQoS leaf nodes.

## ABI, boot and limits

18 external CRC/licence/KCFI boundaries regenerate from three real provider objects;
80 core slots are hash-bound GKI12901745 interfaces. Two GPL exports have **zero direct
stock reverse import slots**. GKI dispatch and device attachment are not negated by that.
Seven completed accelerator imports into separate iommu_debug are independently checked;
no completed component is modified or reopened. See ABI-PARITY and SMI-MMQOS-DEPENDENCIES.

Target stock loading is normal65 / recovery63, not audit71. Only its eventual audit
metadata is corrected; stock lists and the other three modules' audit rows remain intact.
Source certification does not certify provider whole bodies, successful controller probing,
IOVA/DMA traffic, page-table isolation, IRQ recovery, power cycles or secure firmware.
No ADB, hardware operations, module installation, faults, reboot/flash/slot change or push.
