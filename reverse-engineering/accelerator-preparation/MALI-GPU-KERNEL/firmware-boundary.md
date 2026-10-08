# Firmware boundary — MALI-GPU-KERNEL

| firmware | identity | location | loader (in scope, identical to stock) | out of scope |
|---|---|---|---|---|
| Mali CSF MCU firmware | `mali_csffw.bin`, 290 816 B, sha256 `81bef7649fc3c056fae347c4511dd9d2f80f081dc07ac6c4ad9c8fbb7c302f56`; header magic `0xC3F13A6E`, header version 0.3 (bytes `6e3a f1c3 0300 0000`) | `vendor/firmware/mali_csffw.bin` | kbase `csf/mali_kbase_csf_firmware.c`. `request_firmware("mali_csffw.bin")`, overridable with module param `fw_name`. It validates magic and version, parses the entry table into MCU memory sections, boots the MCU, then drives the global/CSG/CS interfaces (`CS_GET_GLB_IFACE`, doorbells, ping, halt, reload on reset). Firmware log is exposed via `mtk_fwlog_enable_mask`. | the firmware's own code and algorithm (retained binary) |
| GPUEB firmware | GPU embedded MCU (DVFS, fast-DVFS, power sequencing) | `gpueb_a/_b` partitions (`partition-consumers.tsv`), loaded by the bootloader / `gpueb.ko` | the kernel-facing IPI protocol: `IPI_ID_GPUFREQ` (`struct gpufreq_ipi_data`, cmds 0–18), `IPI_ID_FAST_DVFS`, the sysram/shared-memory layout, and `gpueb_get_gpr_addr`. The `gpueb.ko` host client belongs to GPU-AI-AUX-KERNEL-INTERFACES. | GPUEB image, its signature and its algorithms |
| Protected-mode entry | GPUEB GPR `0xd1c`/id 6, GMPU table 4 MiB, protected reserve 2 MiB (DT) | — | prot_alloc maps and allocates from the reserve; kbase protected-mode entry via `PROTECTED_PATCH`; secure dma-buf handles via mtk_sec_heap/tmem_ffa | TEE/GenieZone (TKCORE-DRV, TMEM-FFA, GZ scopes) |

**Verification boundary:** the kernel does not check signatures on `mali_csffw.bin`; it
validates the header only. Authenticity is enforced by the dm-verity/AVB integrity of
`vendor`. Nothing was altered or bypassed.

**Reset and recovery:**
* `kbase_csf_reset_gpu` and the firmware reload path (`firmware_reload_needed`), the
  watchdog and progress timeouts (`progress_timeout`, `fw_timeout`, `reset_timeout`
  sysfs), and MTK qinspect recovery are all identical to stock.
* The CSF firmware is reloaded from the same file on reset.
