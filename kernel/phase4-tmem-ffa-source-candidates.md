# `tmem_ffa.ko` — source search and candidate classification

**Result: `EXACT_SOURCE` found on the first (local-identifier) pass.**

## 1. Search inputs taken from the stock ELF

| input | value |
|---|---|
| module name / description | `tmem_ffa`, "MediaTek Trusted Memory Driver" |
| unique function names | `tmem_core_alloc_chunk_internal`, `tmem_query_ffa_handle_to_pa`, `tmem_ffa_region_alloc/free`, `tmem_ffa_page_alloc/free`, `ssheap_alloc_non_contig`, `tmemperf_set_cpu_to_hfreq`, `peer_mgr_session_invoke_cmd_locked`, `create_reg_mgr_desc` |
| exported names | `trusted_mem_api_alloc`, `trusted_mem_page_based_alloc`, `trusted_mem_ffa_query_pa`, `ssmr_online/offline` |
| log-prefix strings | `[TMEM]`, `[TMEM] ssmr:`, `[TMEM] ssheap:`, `[TMEMPERF]` |
| region names | `TEE_SVP`, `TEE_WFD`, `MTEE_PROT`, `MTEE_SVP`, `MTEE_WFD`, `MTEE_TUI`, `MTEE_AP_MD_SHM`, `MTEE_AP_SCP_SHM`, `MTEE_SAPU_DATA_SHM`, `MTEE_SAPU_ENGINE_SHM` |
| provider symbols | 7× `TEEC_*`, 9× `KREE_*`, `ffa_driver_register` |
| feature strings | `page-based-v2-enabled`, `tee-mmap-by-page-enabled`, `TCORE_UT_TESTS_SUPPORT option is not enabled` |

## 2. Searched trees

Local-first, exact-identifier pass:

1. Pinned Nothing MT6878 `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`
   — the same revision that produced the already-closed `ffa_v10.ko`
   (`drivers/misc/mediatek/trusted_mem/ffa_v10/`). The parent directory
   `drivers/misc/mediatek/trusted_mem/` contains the whole trusted-memory
   subsystem, and its `Makefile` builds a second module from the same objects
   under `CONFIG_ARM_FFA_TRANSPORT`:

   ```make
   ifneq ($(filter y m,$(CONFIG_ARM_FFA_TRANSPORT)),)
   obj-m += tmem_ffa.o
   tmem_ffa-y += dev_mgr.o entry.o region_mgr.o ssmr_mgr.o peer_mgr.o proc.o \
                 ssheap_proc.o alloc_api.o ssmr/memory_ssmr.o ssheap/ssheap_lib.o
   ...
   ```

   That is literally the stock module name, description, object set and
   dependency triple.
2. Local `vendor-reference` trees (`MiCode-bsp-klee-w-oss`,
   `MiCode-dash-w-oss`, `MiCode-MTK-kernel-device-modules-chagall-2.0.31`) —
   no `trusted_mem` directory present; not needed once (1) matched exactly.
3. Pinned `kernel_modules@5f75a3b13e8135d45b4b0b70ec893345144f70df` — not
   required; the driver is a device_modules component.

Because the first pass produced a byte-exact rebuild, no further vendor trees
(MiCode, Motorola, OPPO/OnePlus/realme, Transsion, Sony) and no public web
search were needed, and no generic OP-TEE trusted-memory code was used.

## 3. Candidate classification

| candidate | classification |
|---|---|
| `nothing-mt6878 device_modules@957dac18 drivers/misc/mediatek/trusted_mem/` (+ the external vendor headers it includes: `geniezone/public/{kree,tz_cross,gz-trusty}`) | **`EXACT_SOURCE`** — 141/141 stock functions byte-identical after two proven deltas (§4) |
| the same directory at any other MediaTek 6.1 vendor drop | `EXACT_SOURCE_DIFFERENT_REVISION` (not needed) |
| `drivers/tee/teei/510/common/include/tee_client_api.h` (MicroTrust TEEC types) | `NO_USEFUL_SOURCE` for this device — its `TEEC_Context` is an 8-byte `struct file *`; the stock consumer proves 264 bytes |
| project-local TrustKernel header `lieppos/tkcore-recon/include/tk_tee_client_api.h` | **used** — the only TEEC type graph that reproduces stock code byte-for-byte |
| generic upstream OP-TEE / `drivers/tee` trusted memory | `NO_USEFUL_SOURCE` (no lineage evidence) |

## 4. Deltas required on top of the exact source

Both are stock-oracle-proven, behaviour-scoped and documented in
`kernel/phase4-tmem-ffa-RED.md`:

1. **TEE client header family** — the vendor build used TrustKernel's
   `tee_client_api.h`, not the teei/510 one shipped alongside the Nothing
   revision. Proof: `sizeof(TEE_GP_SESSION_DATA)` is `0x140` with
   `context@0x00`, `session@0x108`, `wsm@0x110`, `wsm_buffer@0x138` in stock
   code, which only the TrustKernel layout yields.
2. **`TEEC_InitializeContext(NULL, …)`** — stock emits `mov x0, xzr`
   immediately before the `TEEC_InitializeContext` relocation and contains no
   `.rodata` reference to `"08030000000000000000000000000000"`; the Nothing
   revision passes `SECMEM_TL_GP_UUID_STRING`.

Plus a per-file `__LINE__` provenance offset (`proc.c +1`, `tee_devices.c +1`,
`mtee_devices.c +3`, `tee_impl/tee_ops.c +5`) restored with comment padding —
no code, no behaviour.

## 5. Frozen verdict

`tmem_ffa.ko` source search: **`EXACT_SOURCE`**, pinned
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`,
`drivers/misc/mediatek/trusted_mem/`.
