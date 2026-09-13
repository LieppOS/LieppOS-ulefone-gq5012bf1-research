# `tmem_ffa.ko` — source lineage and revision determination

## 1. Exact tree

| item | value |
|---|---|
| repository | `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` |
| commit | `957dac185efe46cbf6336b0fff9516d84c8cd78f` (`device_modules`, pinned) |
| path | `drivers/misc/mediatek/trusted_mem/` |
| external headers | `drivers/misc/mediatek/geniezone/public/{kree,tz_cross,gz-trusty}/` at the same commit |
| local copy | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tmem-ffa/src` (+ `inc/`) |
| Kconfig | `drivers/misc/mediatek/trusted_mem/Kconfig` (vendor), replicated as `-D` flags |
| Makefile | vendor `Makefile` + `Makefile.configs` (`tmem_ffa-y` object list) |
| Bazel target | `//lieppos/tmem-ffa:tmem_ffa` against `//common:kernel_aarch64` |

This is the **same revision and same parent directory** that already produced
the `DIRECT_SOURCE_MATCH` for `ffa_v10.ko`
(`drivers/misc/mediatek/trusted_mem/ffa_v10/`), so the two TEE modules share
one proven vendor lineage.

## 2. Config set proven from the stock ELF

| config | state | evidence |
|---|---|---|
| `CONFIG_MTK_TRUSTED_MEMORY_SUBSYSTEM` | on | module exists |
| `CONFIG_ARM_FFA_TRANSPORT` | on | `tmem_ffa` module name, `mtee_impl/tmem_ffa.o`, `ffa_driver_register` import |
| `CONFIG_MTK_ENABLE_GENIEZONE` | on | KREE headers gate; 9 `KREE_*` imports |
| `CONFIG_MTK_GZ_KREE` | on | `mtee_ops.o` + `mtee_invoke.o` present |
| `CONFIG_MTK_SECURE_MEM_SUPPORT` | on | `TEE_SVP`, `MTEE_SVP` device entries |
| `CONFIG_MTK_WFD_SMEM_SUPPORT` | on | `TEE_WFD`, `MTEE_WFD` |
| `CONFIG_MTK_PROT_MEM_SUPPORT` | on | `MTEE_PROT`, `MTEE_MCHUNKS_PROT` |
| `CONFIG_MTK_SEC_VIDEO_PATH_SUPPORT` | on | `SecureVideoPath` SSMR feature string |
| `CONFIG_ALLOC_TMEM_WITH_HIGH_FREQ` | on | `tmemperf.o`, `trusted_mem_enable/disable_high_freq` exports |
| `CONFIG_MTK_PROT_MEM_SSHEAP_V2` | on | `pmm_msg_list`/`pmm_page` members — proven by the `trusted_mem_api_alloc` (`0x65e5c101`) and `trusted_mem_api_unref` (`0x7be62965`) export CRCs, which only match with V2 |
| `CONFIG_MICROTRUST_TEE_SUPPORT` | on | selects `tee_impl/tee_ops.o` (the `TEEC_*` peer) |
| `CONFIG_MTK_MTEE_MULTI_CHUNK_SUPPORT` | **off** | stock has no `secmem_set_mchunks_region` symbol |
| `CONFIG_MTK_HAPP_MEM_SUPPORT`, `CONFIG_MTK_SDSP*` | off | no `MTEE_HAPP*` / `MTEE_SDSP*` device names |
| `CONFIG_TEST_MTK_TRUSTED_MEMORY` | off | `"TCORE_UT_TESTS_SUPPORT option is not enabled"`, no `tests/ut_*` symbols |
| `TCORE_PROFILING_SUPPORT`, `TCORE_MEMORY_LEAK_DETECTION_SUPPORT` | off | no `profiler.o` / `mld_helper.o` symbols |
| `-faddrsig` | on | stock carries `.llvm_addrsig` |

## 3. Stock-vs-source comparison

| axis | stock | source-built | verdict |
|---|---|---|---|
| function names | 141 | 141 | identical set |
| function sizes | — | — | 141/141 identical |
| function bytes | — | — | **141/141 byte-identical** |
| KCFI type ids | 141 | 141 | 141/141 exact |
| objects | 60 | 60 | identical (modulo `.modinfo` vermagic length) |
| kernel imports | 76 | 76 | identical |
| MODVERSIONs | 77 | 77 | identical |
| exports | 15 | 15 | identical names, classes **and CRCs** |
| relocations | 2208 | 2208 | identical |
| strings | 292 | 292 | identical except `vermagic` |
| module metadata | `MediaTek Inc.` / "MediaTek Trusted Memory Driver" / `GPL v2` / `depends=gz_tz_system,tkcore,ffa_v10` | same | identical |
| FF-A ids, TA UUID, command IDs, ops tables | — | — | identical (see contracts) |
| sections | 50 | 50 | identical set |

## 4. Verdict

**`DIRECT_SOURCE_MATCH`** — with the two proven deltas of
`kernel/phase4-tmem-ffa-RED.md` (TrustKernel TEE-client header family, and the
`TEEC_InitializeContext(NULL, …)` argument) plus `__LINE__` provenance
padding. Those deltas are *vendor-snapshot* deltas: the GQ5012BF1 build of
`trusted_mem` is the same code base as the pinned Nothing revision, integrated
against TrustKernel instead of MicroTrust, and a handful of lines longer in
four files.
