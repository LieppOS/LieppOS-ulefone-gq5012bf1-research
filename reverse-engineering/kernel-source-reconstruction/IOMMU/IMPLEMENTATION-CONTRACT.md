# Stock implementation and capability boundaries

Authoritative source: unchanged ALPS5e415e059253ce0d2e61c97108e5f5785d71f06f,
drivers/iommu/mtk_iommu.c / mtk_iommu.h; full accepted bodies: FUNCTION-PARITY.tsv.
Line locations refer to that immutable C blob. `STOCK_BINARY_IMPLEMENTATION` means
compiled code/data, not measured execution. Inlined source helpers are not invented
extra stock functions; the ledger contains all48 actual function symbols, including aliases.

## Registration, domains, attachment and translation

- Probe2683..3059 obtains OF match data, allocates driver state and aligned fault-protect
  memory, ioremaps resource0 and obtains bank/IRQ resources. It registers debug PM ops
  once, discovers MM larbs and SMI common or the APU power consumer, enables runtime PM,
  adds device links, publishes drvdata, adds IOMMU sysfs and registers iommu_ops.
  It links its hardware list, binds MM larb components and registers power/debug notifiers.
  Allocation/resource errors propagate; missing larb devices defer probe. Partial registration
  unwinds list/core/sysfs/device-link/PM state. Remove3060 tears registration back down.
- domain_alloc1630 accepts **IOMMU_DOMAIN_DMA only**; no general unmanaged/identity-domain
  feature is established. get_domain_id1453 uses legacy domain bits of first fwspec on
  MT6878 and bounds-checks against selected platform region count. Nonlegacy dma-range
  fitting exists for other platform flags, not the selected MT6878 descriptors.
- domain_finalise1561 delegates to alloc_io_pgtable_ops(ARM_V7S). Page-size bitmap is
  4K/64K/1M/16M; MT6878 input width34, output width35, MediaTek TTBR extension enabled.
  Quirks include ARM_NS, NO_PERMS and ARM_MTK_EXT. Do not claim generic per-PTE R/W
  permission isolation from this driver. Geometry is a forced region aperture.
  Existing hardware-list domains reuse iop/config/TTBR: multiple domain/group IDs do
  **not** automatically prove independently isolated page tables. MM/APU use distinct lists.
- device_group1956 allocates/refcounts groups by region ID on first hardware-list data.
  probe_device1918 requires matching iommu_ops and all the client's ports in one larb.
  release_device1946 frees fwspec. of_xlate1998 requires exactly one cell, obtains provider
  drvdata and appends the full encoded ID; table/domain/larb/port are not one undivided index.
- attach1674 validates state/fwspec, serializes per table, finalizes domain and resumes
  hardware before initialization. It publishes m4u_dom before IRQ enable, writes TTBR,
  invokes port-config and DMA setup, then releases PM/mutex. Failures propagate/unlock.
  detach1755 disables port configuration. **MM MT6878 SKIP_CFG_PORT makes that local
  per-port MMU-enable/bank routine a no-op**; do not assert these writes occurred.
- map1768/unmap1814/iova_to_phys1903 dispatch into io-pgtable ops. Mapping retries ENOMEM
  at most8 times under its atomic flag, choosing delay/context appropriately; other errors
  invoke diagnostics. Unmap updates gather and logs zero progress. Generic GKI iommu-dma,
  not a new allocator implemented here, manages IOVA allocations and ordinary DMA cache sync.
  iova journal calls in debug provider are diagnostics, not proof of a successful DMA transfer.

## TLB invalidation and synchronization

flush1023 / range_sync1092 use a spinlock and platform hardware list, guard powered-off
instances, select invalidators at0x2c, program all/range commands at0x20 and start/end
at0x24/0x28. Encoded high address bits are preserved. Atomic completion polling reads
CPE_DONE0x12c (10us interval/1000us timeout). Timeout diagnostics remain literal stock
behavior; only the platform-dependent nonsync path requests a full-flush fallback.
flush_iotlb_all1833 / iotlb_sync1840 / sync_map1873 supply generic core callbacks;
empty/inverted or wrapping ranges are rejected/logged. Secure-host synchronization and
debug journals occur separately from TLB invalidation. No hardware polling was executed.

## Faults, protection and error recovery

hw_init2079 programs control/AXI/throttle/protection/interrupt policy, requests interrupts
and initializes normal/secure banks as selected. The aligned protection buffer is a fault
landing address, not a recovered secure firmware image. isr1342 reads fault status, table
base, VA/PA and access/layer information; reconstructs high bits; with the selected DEBUG
config it calls report_custom_iommu_fault and dumps IOVA. The generic report_iommu_fault
fallback is a different conditional branch, not the stock active compile choice.
ISR handles secure-bank paths, clears interrupt status, flushes TLB and records storms.
Repeated faults meeting the2-count time-window policy disable IRQs for10 seconds and
schedule timer restart/debug reset (942..985). This is code evidence, not demonstrated
fault recovery or permission to trigger a test. mau_count4 is descriptor data; the MT6878
flags do **not** set IOMMU_MAU_EN, so compiled MAU helpers do not establish active monitoring.

## PM, clocks and resets

runtime_suspend3078 backs up initialized MM registers and secure banks, skipping register
reads before domain initialization; resume3126 restores registers/TTBR, secure banks and
flushes TLB. MM genpd notifier tracks power; APU PM status can be updated by the separate
exported debug interface. APU **PM_OPS_SKIP** returns early on suspend and uses a TLB flush
on resume rather than MM's register-backup policy. Device links express APU/SMI lifetime
and runtime-PM relationships. MT6878 has no HAS_BCLK flag despite MM DT clock-names=bclk;
no clocks property is supplied there. No reset-controller property/API proves a target
reset path. Other-platform clock branches are compiled capabilities, not MT6878 operations.

## Secure-world interfaces: host contract only

IOMMU_SEC_EN is set in both MT6878 descriptors. Host SMC IDs0xbb00ffa2 through0xbb00ffa7 implement
share/unshare, mode query, protected-region registration, address-query and invalidation
contracts (661..829). iommu_secure supplies bank init/IRQ enable/backup/restore/fault dump and AO-debug switch:
all six are actual imported ABI slots, not guessed APIs from an inactive header branch. `hypmmu_type2_en`, secure-bank behavior, returned addresses and successful secure
permission enforcement remain **UNKNOWN** at runtime. No ATF/TEE/hypervisor algorithms,
firmware internals or calibration are reconstructed by exact host-module parity.
