# MT6878 GPUEB / VCP hardware contract

Source of truth: the merged device tree
`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` plus the reconstructed
driver source. **Nothing here was read from live hardware.**

## 1. GPUEB — `/soc/gpueb@13c00000` (`mediatek,gpueb`)

Eight named register windows:

| name | range |
|---|---|
| `gpueb_base` | `0x13c00000 + 0x40000` (GPUEB SRAM/core) |
| `gpueb_gpr_base` | `0x13c3fd1c + 0x64` (general-purpose registers) |
| `gpueb_reg_base` | `0x13c60000 + 0x2000` (control block) |
| `mbox0_base` | `0x13c3fd80 + 0x280` (one 160-slot mailbox, 4-byte slots) |
| `mbox0_set` / `mbox0_clr` / `mbox0_send` / `mbox0_recv` | `0x13c62004`, `0x13c62074`, `0x13c62000`, `0x13c62078` (4 B each) |

* **Interrupt:** one — `mbox0` = GIC **SPI 273** (`0x111`), level, active high.
* **Clocks:** none declared (the GPU power/clock path is owned by the GPU stack).
* **Properties:** `gpueb-support = 1`, `gpueb-logger-support = 0` (logger disabled on this
  board), `mbox-count = 1`, `mbox-size = 160`, `slot-size = 4`, `ts-mbox = 0`,
  `gpueb-diagnosis-mode = 0`.
* **11 IPI channels**, identical send/recv name tables:
  `IPI_ID_FAST_DVFS_EVENT`, `IPI_ID_GPUFREQ`, `IPI_ID_SLEEP`, `IPI_ID_TIMER`,
  `IPI_ID_FHCTL`, `IPI_ID_CCF`, `IPI_ID_GPUMPU`, `IPI_ID_FAST_DVFS`, `CH_IPIR_C_MET`,
  `CH_IPIS_C_MET`, `IPI_ID_BRISKET`. The `send-table` gives (id, mbox, slots) per channel
  — slot counts 4, 8, 3, 6, 9, 4, 6, 6, 1, 4, 3 — all on mailbox 0.
* **2 shared-memory regions:** `MEM_ID_GPUFREQ` (0x4000 = 16 KiB) and `MEM_ID_LOG`
  (0x180000 = 1.5 MiB).

The channel names map directly to the GPUEB's job: GPU frequency/DVFS, GPU sleep, CCF
clock handshakes, FHCTL PLL hopping, GPU-MPU protection and MET tracing.

## 2. VCP — `/soc/vcp@1ea00000` (`mediatek,vcp`, `status = "okay"` explicitly)

Thirty-one named register windows, including:

| name | range | role |
|---|---|---|
| `vcp_sram_base` | `0x1ea00000 + 0x40000` | 256 KiB VCP SRAM |
| `vcp_cfgreg` | `0x1ec24000 + 0x1000` | core config |
| `vcp_cfgreg_core0` / `vcp_cfgreg_core1` | `0x1ec30000`, `0x1ec40000` | per-core config |
| `vcp_intc_core0` | `0x1ec32000 + 0x1000` | interrupt controller |
| `vcp_pwr_ctl` | `0x1ec37000 + 0x1000` | power control |
| `vcp_bus_debug` / `vcp_bus_tracker` | `0x1ec51000`, `0x1ec52000` | bus debug (13 ports) |
| `vcp_l1creg` | `0x1ec60000 + 0x40000` | L1 cache control |
| `vcp_cfgreg_sec` / `vcp_cfgreg_mmu` | `0x1eca5000`, `0x1e820000` | secure cfg, MMU |
| `mbox0..mbox4` `_base/_set/_clr/_init` | `0x1ecfb000 … 0x1ecff10c`, `0x1eca5020…30` | **five** mailboxes |

* **Interrupts:** seven — `wdt` (SPI 200), `reserved` (201), `mbox0..mbox4`
  (SPI 202–206), all level/active-high.
* **Clocks:** `mmup-sel`, `mmup-clk`, `mmup-26m`; `power-domains = <&power-controller 20>`;
  `fmeter-ck = 7`, `fmeter-type = 2`.
* **Topology:** `core-nums = 1`, `twohart = 1`, `core-0 = "enable"` — one core, two harts.
* **Memory:** `vcp-sram-size = 0x40000` (256 KiB), `vcp-dram-size = 0x800000` (8 MiB),
  `memorydump = {0x40000, 0x20000, 0x3f00, 0x400, 0x160000}`,
  `vcp-secure-dump = 1` with size `0x200000` at offset `0x600000`.
* **IOMMU:** `iommus = <&iommu 0x40522>`; `dma-ranges` spans the full 1:1 window;
  `mediatek,smi` links the SMI larb. Four dedicated VCP IOMMU nodes exist as separate
  platform devices matched by `vcp.ko`'s secondary of_match entries:
  `vcp-iommu-vdec@1ec24000` (`mediatek,vcp-io-vdec`),
  `vcp-iommu-venc@1ec30000` (`mediatek,vcp-io-venc`),
  `vcp-iommu-work@1ec32000` (`mediatek,vcp-io-work`),
  `vcp-iommu-sec@1ec37000` (`mediatek,vcp-io-sec`). The source also matches
  `mediatek,vcp-io-ube-lat` and `mediatek,vcp-io-ube-core`, which **have no node on this
  board**. `vcp_get_io_device()` is exactly how the VCodec driver obtains these per-use
  DMA devices.
* **Channels:** `mbox-count = 5`; the `send-table`/`recv-table` hold 42 and 68 u32 entries
  respectively (the preparation's "28 configured channel IDs").
* `vcp-ee-enable = 4`, `vcp-hwvoter = 1`, `vcp-mem-tbl` enumerates the per-feature
  reserved-memory block sizes.

The VCP feature table compiled into `vcp.ko` (`vcp_feature_table.c`) starts
`RTOS_FEATURE_ID`, `VDEC_FEATURE_ID`, `VENC_FEATURE_ID`, … each with a frequency vote, an
enable refcount and `sys_id = VCPSYS_CORE0` — this is the object the VCodec modules
manipulate through `vcp_register_feature` / `vcp_deregister_feature`.

## 3. Evidence classes

1. **PROVEN ACTIVE ON DEVICE** — nothing. No register was read and no firmware handshake
   was observed in this offline pass.
2. **ENABLED IN STOCK DEVICE TREE** — `/soc/gpueb@13c00000` (implicitly okay,
   `gpueb-support = 1`) and `/soc/vcp@1ea00000` (explicit `status = "okay"`,
   `vcp-support = 1`) plus the four VCP IOMMU nodes, with the register, IRQ, clock,
   power-domain, mailbox and channel tables above.
3. **PRESENT IN STOCK BINARY** — all three modules are byte-identical to the rebuild and
   are listed in the shipped `modules.load`: `vcp_status.ko` at line 166 of the **vendor
   ramdisk** list, `gpueb.ko` at line 37 and `vcp.ko` at line 77 of the **vendor_dlkm**
   list. Firmware `gpueb.img` and `vcp.img` are present in the stock firmware set.
4. **REFERENCE-SOURCE CAPABILITY (compiled out or unused here)** — GPUEB logger is
   disabled by DT (`gpueb-logger-support = 0`); `CONFIG_MTK_TINYSYS_VCP_DEBUG_SUPPORT` is
   unset so `/dev/vcp` carries **no** file operations in the shipped build; the
   `vcp-io-ube-lat` / `vcp-io-ube-core` match entries have no DT node; GPUEB `IPI_TEST`
   proc entry is compiled out.
5. **UNVERIFIED** — whether either driver probes, whether firmware boots, actual IPI
   latency/ordering, watchdog and exception behaviour, real DVFS/sleep transitions, and
   every timing property.
