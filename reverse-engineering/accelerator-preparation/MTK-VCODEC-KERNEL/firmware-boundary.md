# Firmware boundary — MTK-VCODEC-KERNEL

## What is reconstructed and what is not

| Layer | State |
|---|---|
| Normal-world kernel drivers (the five owned modules) | **Reconstructed from public source, byte-identical to stock** (build ID aside). Licensed GPL-2.0 per upstream headers. |
| VCP firmware image `firmware/vcp.img` (1 492 000 bytes, sha256 `98e289424be7929ca40081ab7e4d6084ec35cd76eae91ea19cf501dfb6d09a5c`) | **Proprietary, signed, retained unmodified.** Not open source, not reconstructed, not modified, not redistributed in any repository. |
| VCP-side codec algorithms (bitstream parsing, rate control, scheduling inside the co-processor) | **Proprietary**, out of scope. |
| VCP host/boot/status drivers (`vcp.ko`, `vcp_status.ko`) | Owned by `GPU-AI-AUX-KERNEL-INTERFACES`, **not** absorbed here; only their export ABI is verified. |
| TinySys IPI transport (`mtk_tinysys_ipi.ko`) | Owned by `MTK-TINYSYS-IPI`; export ABI verified only. |

## Kernel-visible firmware interface (from the now-exact source)

* **Boot dependency.** The codec drivers do not load firmware themselves. They register as VCP
  features and wait for the VCP host: `vcp_register_feature(VDEC_FEATURE_ID)` /
  `vcp_register_feature(VENC_FEATURE_ID)`, `vcp_deregister_feature(...)`, `is_vcp_ready()`,
  `get_vcp_generation()`, `vcp_A_register_notify()` for VCP ready/stop notifications. A
  signed scatter image is **not** loaded through `request_firmware` by these modules.
* **Transport.** `mtk_ipi_register()` / `mtk_ipi_send()` on `vcp_ipidev`, decoder channel
  `IPI_OUT_VDEC_1` (id 0) / `IPI_IN_VDEC_1` (id 1), encoder channel `IPI_OUT_VENC_0` (id 16)
  / `IPI_IN_VENC_0` (id 17). Messages are the `vdec_ap_ipi_*` / `venc_ap_ipi_*` structures in
  `vdec_ipi_msg.h` / `venc_ipi_msg.h`; both directions carry an instance handle plus a
  message id, and acknowledgements are matched to the originating instance.
* **Shared memory.** `vcp_get_reserve_mem_phys/virt/size(VDEC_MEM_ID | VENC_MEM_ID)`. The
  per-instance VSI is addressed as `reserve_mem_virt + (vcu_inst_addr & 0x0FFFFFFF) -
  (reserve_mem_phys & 0x0FFFFFFF)`; translation-fault info lives at the fixed
  `VDEC_TF_INFO_OFFSET` / `VENC_TF_INFO_OFFSET` inside the same region. DMA buffers reach VCP
  through the `mediatek,vcp-io-vdec` / `vcp-io-venc` IOMMU devices (`vcp_get_io_device()`).
* **Completion.** Synchronous sends poll for the acknowledgement with a bounded wait; the
  spin phase is bounded by `VCP_SYNC_TIMEOUT_MS` and the overall wait by `IPI_TIMEOUT_MS`
  (5 000 ms, or 10 000 ms on ENG builds and when `mtk_vcodec_dbg`/`mtk_v4l2_dbg_level` is
  set); encoder first-`set_param` uses a 60 000 ms budget; send-side back-pressure uses
  `IPI_SEND_TIMEOUT_MS` (1 000 ms) with a 10 µs polling interval.
* **Failure and recovery.** Timeouts dump instance state, request SMI hang detection
  (`mtk_smi_dbg_hang_detect`, `mtk_smi_dbg_dump_for_venc/_vdec`), EMI debug
  (`mtk_emidbg_dump`) and may `trigger_vcp_halt()`. VCP stop/ready notifications drive
  instance abort and re-initialisation; `get_vcp_generation()` invalidates stale instances
  across a VCP restart.
* **Compatibility.** The message layouts and feature/memory ids are compile-time constants
  shared with the firmware image; they are **not** negotiated at runtime. A firmware image
  from a different release is therefore not interchangeable, and this work does not change
  that.

## Hard rules observed

* No firmware was modified, re-signed, extracted into source form or redistributed.
* No proprietary blob is present in `android_kernel_modules_vcodec_ulefone_gq5012bf1`.
* Nothing above is a claim that firmware behaviour is known: only the **kernel side** of the
  contract is reconstructed. All firmware-internal behaviour remains **UNKNOWN**.
