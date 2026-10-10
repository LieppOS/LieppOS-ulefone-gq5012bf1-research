# Early boot and future controlled-test requirements

Authoritative hashed stock module lists, not old merged-loader numeric fields:
evidence/inventory/LOAD-ORDER.tsv. mtk_iommu is **normal65 / recovery63**.
Main dependency sequence: mtk-smi normal54/recovery52, mtk-smi-dbg55/53,
iommu_debug63/61, iommu_secure64/62, mtk_iommu65/63.
MMQoS common61/59 and platform62/60 are earlier configured voting components, not
owned IOMMU modinfo/symbol dependencies. No stock list is edited.
iommu_test is vendor_dlkm normal164, not first-stage or audit411 in this specific file.
Only mtk_iommu's eventual audit load_order71→65 is corrected; unrelated rows unchanged.

## Dependency kinds

- **Direct vendor ABI:** depends=iommu_secure,iommu_debug,mtk-smi-dbg (18 slots).
  This closure does not independently source-certify these modules.
- **Core ABI:**80 pinned GKI slots, including iommu core, ARM_V7S io-pgtable allocation,
  component framework, device links, IRQ/sysfs/OF, PM/genpd, SMC and clock helpers.
- **Hardware DT:** controller power domains are mt6878-scpsys7 (MM) and21 (APU),
  MM mediatek,larbs and supplier chain, APU mediatek,apu-power and eight bank nodes.
  Generic provider framework/probe ordering may defer; loaded is not successfully bound.
- **BOOT-CLOCK-CORE/PINCTRL/REGULATORS:** already certified foundations remain separate.
  No direct mtk_clk/pinctrl/regulator vendor symbol edges establish them as this target's
  new implementation. Clocks/regulators power the surrounding systems; HAS_BCLK is absent
  on selected descriptors, despite a DT name. No target reset or regulator supply property
  is invented. Power-domain driver source remains outside this closure.
- **STORAGE:** certified UFS/MMC/RPMB components are preserved; no controller/client DT
  relationship or direct target import establishes MediaTek M4U translation for storage.
- **SMI vs MMQoS:** component/PM interconnect binding and voting are not DMA translation.

## Future separately authorized Slot B gate — not executed

Before a controlled test: preserve rollback/verified-boot/signing policy, trusted stock DT
and load order; keep matching core ABI and every real provider, check depmod reachability,
verify clocks/genpd/SMI/APU links and bank devices, validate controller/client probing,
then perform bounded authorized DMA attach/map/unmap and translation checks only with
safe buffers and rollback arrangements. Verify TLB completion, secure-service responses,
IRQ/fault diagnostics, power/suspend/resume and cache synchronization under that separate
plan. No evidence here authorizes register writes, fault injection, storage DMA stress,
module loading, slot changes, reboot or firmware modification.
