# Phase 4 — `tkcore.ko` source-provenance search (RED)

**Classification: `NO_PUBLIC_SOURCE_FOUND` — structural donor only.**

Target: TrustKernel TKCore TEE driver shipped as
`vendor-ramdisks/platform:lib/modules/tkcore.ko` on Ulefone Armor 29 Pro
Thermal (`GQ5012BF1`, MT6878/MT6878T), `TrustKernel TKCore TEEC v1.0`,
`version 6:1.1-k6.6`, `srcversion 604D4583E310DBFAC768366`.

## 1. Build-path fingerprints recovered from the binary

`.rodata.str` carries the vendor build paths (these are the file names to look
for in any leaked/GPL vendor tree):

```
../kernel_device_modules-6.1/drivers/tee/tkcore/core/tee_context.c
../kernel_device_modules-6.1/drivers/tee/tkcore/core/tee_session.c
../kernel_device_modules-6.1/drivers/tee/tkcore/core/tee_procfs.c
../kernel_device_modules-6.1/drivers/tee/tkcore/core/tee_kernel_api.c
../kernel_device_modules-6.1/drivers/tee/tkcore/core/tee_core.c
../kernel_device_modules-6.1/drivers/tee/tkcore/core/tee_shm.c
```

Compiler: `Android (10087095, +pgo, +bolt, +lto, -mlgo, based on r487747c)
clang version 17.0.2` — i.e. the same toolchain as the exact GKI workspace.

## 2. Searches performed (all negative for tkcore itself)

| Where | Query | Result |
|---|---|---|
| grep.app (index healthy — see control below) | `tee_core_uuid2ptr` | **0 hits** |
| grep.app | `tee_spi_cfg_padsel` | **0 hits** |
| grep.app | `nsdrv_feature_flags` | **0 hits** |
| Sourcegraph public (`fork:yes archived:yes`) | `tee_clkmgr_register`, `tkcore_admin`, `TEEC_SharedMemory memRefs` | 0 results |
| Web search (multi-provider) | `"drivers/tee/tkcore"`, `"TrustKernel TKCore TEEC v1.0"`, `"tkcore" "tee_kernel_api.c"`, `"returnOrigun"` typo string, `"tee_core_alloc_uuid"` | only OP-TEE / mainline `drivers/tee` material; no TrustKernel driver source |
| searchcode.com API | `tee_core_uuid2ptr`, `tee_spi_cfg_padsel`, `tee_clkmgr_register` | API returns HTTP 404 (service endpoint gone) |
| Local vendor corpora | `nothing-mt6878/device_modules`, `MiCode-MTK-kernel-device-modules-chagall-2.0.31`, all extracted GQ5012BF1 partitions, GKI workspace | no `drivers/tee/tkcore`; only MobiCore (`gud/500/510/600`) and MicroTrust TEEI (`teei/510`) TEE stacks, which are *different* vendors, not TKCore |
| Ulefone GPL publishing | `github.com/ulefoneofficial` | no Armor 29 Pro / GQ5012BF1 / MT6878 kernel release |

Control queries proving the index was working:
`tee_wait_queue_private`, `tee_shm_pool_p2v`, `tee_core_alloc` → 3 hits each,
all in `OP-TEE/optee_linuxdriver`; `TEEC_AllocateSharedMemory` → 30 hits across
OP-TEE/NuttX. So the zero-hit results above are real absences, not lookup
failures.

## 3. Structural donor (accepted as donor only)

`https://github.com/OP-TEE/optee_linuxdriver` @
`3a43adc1730efa06bcd96e72b3a2c11ccd0091a4` (2016-05-10, "deprecated"),
GPL-2.0, cloned to `workspace/phase4-tkcore/source/optee_linuxdriver`.

Evidence that TKCore is a TrustKernel fork of this tree:

* 68 of the stock module's 122 defined text symbols share donor names
  (`tee_context_create`, `tee_session_create_and_open`, `tee_shm_alloc_io`,
  `tee_supp_cmd`, `tee_core_add/del/alloc/free`, `tee_wait_queue_*`, the
  `TEEC_*` kernel API, …).
* The donor's `struct tee_wait_queue_private { struct mutex mu; struct
  list_head db; }` reproduces the stock CRC `0x03c4c343` **exactly** — donor
  member names survive verbatim in TKCore.
* The donor's GlobalPlatform value types reproduce `TEEC_CloseSession`,
  `TEEC_InvokeCommand` and `TEEC_ReleaseSharedMemory` CRCs exactly.

Evidence that it is **not** an identity match (so it cannot be used as "the
source"):

* Donor `struct tee` prototypes give `tee_core_add 0x05670103` vs stock
  `0x74f0ee2b` (and three more mismatches) — TrustKernel reworked `struct tee`
  (312 bytes, no inline `struct miscdevice`, a runtime list of three misc
  devices, extra fields).
* TKCore adds whole subsystems absent from the donor: `/proc/tkcore` log
  daemon with an IRQ + kthread (`logd`), the secure-SPI proxy
  (`tee_spi_transfer*`, `tee_spi_cfg_padsel`), the secure clock manager
  (`tee_clkmgr_*`), cached-SHM mapping helpers, UUID/IDR handle indirection
  (`tee_core_alloc_uuid`/`tee_core_uuid2ptr`), `nsdrv_feature_flags`, CPU
  affinity helpers, and three char devices (`tkcore_admin`, `tkcore_client`,
  `tkcore_fp`) instead of the donor's single misc device.
* Donor is ARMv7-era, pre-DMA-BUF-namespace, pre-KCFI; stock imports namespace
  `DMA_BUF` and is built for 6.1/arm64 with KCFI.

MicroTrust TEEI (`drivers/tee/teei/510`) and Trustonic MobiCore
(`drivers/tee/gud/*`) in the local vendor corpora are **API collisions only**
(they also expose `TEEC_*`); they share no TKCore-specific symbol and are not
donors.

## 4. RED verdict

* No public or local source for TrustKernel TKCore exists in reach.
* The donor supplies the GlobalPlatform type graph and a naming convention that
  provably survived into TKCore, which is what made 14/25 export CRCs
  regenerable — see `kernel/phase4-tkcore-provider-abi.md`.
* The donor does **not** supply TrustKernel's private `struct tee` /
  `struct tee_context` member names, which is what blocks the remaining 11.
* Therefore `tkcore` is **not** reconstructable today, and the stock binary
  remains the only runtime provider on this device.
