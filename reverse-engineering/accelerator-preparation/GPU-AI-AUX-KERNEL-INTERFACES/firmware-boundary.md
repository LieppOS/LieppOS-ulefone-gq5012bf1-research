# Firmware boundary and dependency ownership — GPU-AI-AUX-KERNEL-INTERFACES

## 1. What is reconstructed and what is not

Reconstructed: the **normal-world kernel host** for two auxiliary processors — the code
that maps registers, claims reserved memory, sets up mailboxes and IPI channels, counts
feature/power votes, handles interrupts, collects logs and coredumps, and drives
suspend/reset/recovery.

**Not** reconstructed, not modified, not analysed:

| firmware | bytes | sha256 | owner |
|---|---:|---|---|
| `firmware/gpueb.img` | 529 408 | `e8a1f8f70f51e0a7b390ecaff32afe573b83a5a851f9d93a497528616001df61` | retained proprietary |
| `firmware/vcp.img` | 1 492 000 | `98e289424be7929ca40081ab7e4d6084ec35cd76eae91ea19cf501dfb6d09a5c` | retained proprietary |

Neither image was opened, disassembled, rebuilt or replaced. Recovering the kernel
transport does **not** recover the firmware: the on-core RTOS, the per-channel remote
handlers, the signing and the secure boot chain remain unknown by design. Neither module
uses `request_firmware` — the images are placed by the boot chain, and the host drivers
only release the core and exchange messages.

## 2. The kernel-visible firmware interface (and only that)

* **Transport** — both processors use the MediaTek TinySys IPI stack: `mtk-mbox` provides
  the raw mailbox (`mtk_mbox_probe`, `mtk_mbox_write`, `mtk_smem_init`) and
  `mtk_tinysys_ipi` the channel layer (`mtk_ipi_device_register`, `mtk_ipi_register`,
  `mtk_ipi_send`, `mtk_ipi_send_compl`, `ipi_monitor_dump`). Both transport modules are
  **already DONE under MTK-MBOX / MTK-TINYSYS-IPI**; this component is a client and
  rebuilds neither.
* **GPUEB** — 1 mailbox, 160 slots of 4 bytes, 11 named channels (DVFS, GPUFREQ, SLEEP,
  TIMER, FHCTL, CCF, GPUMPU, FAST_DVFS, MET ×2, BRISKET), 2 shared-memory regions
  (GPUFREQ 16 KiB, LOG 1.5 MiB), one mailbox interrupt (SPI 273).
* **VCP** — 5 mailboxes, 7 interrupts (`wdt` + `mbox0..4`), 256 KiB SRAM + 8 MiB DRAM
  window, a secure dump region (2 MiB at offset 6 MiB) and a feature table whose entries
  (`RTOS`, `VDEC`, `VENC`, …) carry a frequency vote and an enable refcount.
* **Error/recovery path** — `vcp.ko` reports through `aed_common_exception_api` (AEE) and
  registers a coredump file via `mrdump_mini_add_extra_file`; it dumps GIC state through
  `mt_irq_dump_status`, SMI state through `mtk_smi_dbg_dump_for_mminfra`, and takes a
  device-APC power callback (`register_devapc_power_callback`). `gpueb.ko` exposes
  `gpueb_dump_status` and `gpueb_trigger_wdt`.

Message *payload semantics* beyond the channel/slot geometry declared in DT and the host
structures are **not** claimed: the remote handlers live in firmware.

## 3. Dependency ownership (nothing transferred here)

| dependency | used for | retained owner |
|---|---|---|
| `mtk_tinysys_ipi` | IPI channel registration and send | MTK-TINYSYS-IPI (DONE) |
| `mtk-mbox` | raw mailbox + shared memory init | MTK-MBOX (DONE) |
| `clk-common` | `mt_get_fmeter_freq`, mminfra hardware-voter power control | clock-common owner |
| `aee_aed`, `mrdump` | exception reporting and coredump attachment | AEE owner |
| `irq-dbg` | GIC status dump on VCP fault | SDA/irq-dbg owner |
| `mtk-smi-dbg` | SMI/MMINFRA dump on VCP fault | SMI owner |
| `system_heap` | dma-buf naming (`import_ns=DMA_BUF`) | DMA-BUF heaps owner |
| `device-apc-common` | power callback registration | DEVAPC owner |

## 4. Relationship to the other reconstructed accelerators

This component is the **provider** side of edges the already-DONE components depend on
(67 edges, all CRC-matching — see [cross-component-abi.tsv](cross-component-abi.tsv)):

* **MTK-VCODEC-KERNEL (DONE)** — `mtk-vcodec-dec-v1` and `mtk-vcodec-enc-v1` import 13 and
  12 VCP symbols respectively, and `mtk-vcu` imports `vcp_get_io_device`. The VCodec
  closure correctly left "VCP host/status" to another owner; that owner is this component,
  and the symbols now rebuild with the exact CRCs VCodec records. Load order follows:
  `vcp_status` (ramdisk) → `vcp` (vendor_dlkm line 77) → the codec modules.
* **MALI-GPU-KERNEL (DONE)** — `mtk_gpufreq_wrapper`, `ged`, `fhctl` and `met_gpueb_api`
  import 15 GPUEB symbols. GPUEB is the microcontroller that executes GPU DVFS; the Mali
  KMD itself imports none of these directly.
* **APUSYS-NPU-KERNEL (DONE)** — **no symbol, header or DT relationship.** APU uses its own
  RPMsg/remoteproc path, not TinySys IPI. No APU interaction is claimed.
* **MTK-MDP-KERNEL (DONE)** — no direct edge. MDP reaches VCP power indirectly through
  `mtk-mmdvfs-v3` / CMDQ, which are separate owners and themselves import `vcp_status`.
* **SENSOR-HUB-KERNEL / AUDIO-DSP-KERNEL** — SCP and ADSP hosts are closed elsewhere and
  were not duplicated; MCUPM and SSPM remain outside this finite assignment.

No DONE component was rebuilt, re-owned or modified by this work.

## 5. Ownership correction recorded

The preparation listed the raw modinfo dependency sets as *references, not targets*. That
holds: all 16 external providers resolved to existing owners, and the only new ownership
asserted here is over `gpueb.ko`, `vcp.ko` and `vcp_status.ko` themselves.
