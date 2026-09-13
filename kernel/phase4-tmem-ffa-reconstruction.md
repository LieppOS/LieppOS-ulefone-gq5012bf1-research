# `tmem_ffa.ko` — authoritative source-closure report

**Classification: `DIRECT_SOURCE_MATCH` · `SOURCE_NOW` · FROZEN FOR RE: YES**

**Verifier:** `kernel/scripts/phase4_tmem_ffa_verify.py` — **76/76 checks passed**

## 1. Stock oracle

| item | value |
|---|---|
| SHA256 | `707e26674abbe7f9c695bb949d74fd5de04972d4bbb991cddc3a2ea9ab45f01b` |
| size | 151,456 bytes |
| Build ID | `8b25fc266c347dfd30da218cd041696a5e0471f7` |
| compiler | Android (10087095, +pgo, +bolt, +lto, -mlgo, r487747c) clang 17.0.2 |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| author / description / license | MediaTek Inc. / "MediaTek Trusted Memory Driver" / GPL v2 |
| depends | `gz_tz_system,tkcore,ffa_v10` |
| srcversion / params / aliases / import-ns | none |
| placement | `vendor_dlkm`, `modules.load` index **152** (1-based) / 151 (0-based) of 195 |
| recovery | not present in any recovery load list |
| duplicate copies | 2 in-repo copies, byte-identical |
| frozen oracle | `workspace/phase4-tmem-ffa/oracle/tmem_ffa.stock.ko` |
| full record | `kernel/phase4-tmem-ffa-stock-oracle.txt` |

## 2. Source

| item | value |
|---|---|
| result | **`EXACT_SOURCE`** on the first local-identifier pass |
| tree | `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` |
| revision | `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f` (same pin as the closed `ffa_v10`) |
| path | `drivers/misc/mediatek/trusted_mem/` (+ `geniezone/public/{kree,tz_cross,gz-trusty}` headers) |
| local source | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/tmem-ffa/{src,inc}` |
| build target | `//lieppos/tmem-ffa:tmem_ffa` against `//common:kernel_aarch64` |
| reports | `phase4-tmem-ffa-source-candidates.md`, `phase4-tmem-ffa-lineage.md` |

## 3. RED and deltas

RED was recorded with the **unmodified** donor
(`workspace/phase4-tmem-ffa/red/`): 141 shared functions, 139/141
size-identical, 136/141 byte-identical, **141/141 KCFI exact**, 76/76 imports,
77/77 MODVERSIONs, 2208/2208 relocations, 13/15 export CRCs.

Six stock-proven deltas closed the rest (full evidence in
`kernel/phase4-tmem-ffa-RED.md`): two config-visibility corrections
(`CONFIG_MTK_PROT_MEM_SSHEAP_V2` on, `CONFIG_MTK_MTEE_MULTI_CHUNK_SUPPORT`
off), the TrustKernel TEE-client header family, `TEEC_InitializeContext(NULL,…)`,
`__LINE__` provenance padding (comments only), and `-faddrsig`.

## 4. Final parity

| axis | stock | rebuilt | result |
|---|---:|---:|---|
| functions | 141 | 141 | exact set |
| size-identical | — | 141 | **141/141** |
| **byte-identical** | — | 141 | **141/141** |
| KCFI type ids | 141 | 141 | **141/141 exact** |
| imports | 76 | 76 | exact |
| MODVERSIONs | 77 | 77 | exact |
| exports | 15 | 15 | **15/15 CRCs natural and exact** |
| objects | 60 | 60 | exact (`.modinfo` length aside) |
| relocations | 2208 | 2208 | exact |
| strings | 292 | 292 | exact except `vermagic` |
| sections | 50 | 50 | exact |
| module metadata | — | — | identical, incl. `depends` |
| module size | 151,456 | 151,448 | −8 B (`vermagic` 2 B + `.llvm_addrsig` 8 B) |

`kernel/phase4-tmem-ffa-function-parity.tsv` — all 141 rows `EXACT`.

## 5. Provider provenance (never lumped together)

| class | count | symbols |
|---|---:|---|
| `GKI_NATURAL` | 59 | exact-GKI 12901745 kernel symbols |
| `FFA_V10_NATURAL` | 1 | `ffa_driver_register` `0x0d53cde9` — real source-built `//lieppos/ffa-v10` |
| `TKCORE_STOCK_RUNTIME` | 7 | the `TEEC_*` set below |
| `GZ_PROVIDER_STOCK_RUNTIME` | 9 | the `KREE_*` set below |

`kernel/phase4-tmem-ffa-provider-map.tsv` carries all 76 rows with call sites.

### tkcore edges (7, exact stock CRCs)

`TEEC_InitializeContext 0x89b94f9a`, `TEEC_RegisterSharedMemory 0xa7bb0a46`,
`TEEC_OpenSession 0xe821e2a3`, `TEEC_FinalizeContext 0x7b3bc43f`,
`TEEC_InvokeCommand 0x202b681e`, `TEEC_CloseSession 0xcb193c37`,
`TEEC_ReleaseSharedMemory 0xc4d15e1c` — **3 NATURAL / 4 PROVIDER_ABI_BLOCKED**
in tkcore's own 14/11 split.

### gz_tz_system edges (9, exact stock CRCs)

`KREE_CreateSession 0x552d4efc`, `KREE_CloseSession 0x5878d629`,
`KREE_TeeServiceCall 0xec19e146`, `KREE_ION_AllocChunkmem 0x3d5d5254`,
`KREE_ION_ZallocChunkmem 0x0175c8da`, `KREE_ION_UnreferenceChunkmem 0x8dceb484`,
`KREE_AppendSecureMultichunkmem 0x9a19c31a`,
`KREE_ReleaseSecureMultichunkmem 0x44781e48`,
`KREE_ConfigSecureMultiChunkMemInfo 0xbdb6a34b`.

Both provider records are machine extractions of the stock providers' own
`__kcrctab` (`stock-provider.symvers` + `.provenance.json`). No CRC injection,
no fake symvers, no `__versions` editing, no ELF patching, no
`KBUILD_MODPOST_WARN`.

## 6. Exports and consumers

15 exports, all CRC-natural. Stock consumers (411 modules scanned):
`mtk_sec_heap.ko` (11 symbols), `gz_main_mod.ko` (2), `mali_kbase_mt6878_r44.ko`
(1). Because every export CRC regenerates exactly, the source-built module is
drop-in for all of them. See `kernel/phase4-tmem-ffa-consumer-abi.md`.

## 7. Behaviour contracts

| document | content |
|---|---|
| `phase4-tmem-ffa-architecture.md` | trusted-memory subsystem, regions, sessions, locking, lifecycle, PM, DT |
| `phase4-tmem-ffa-teec-call-flow.md` | exact TEEC sequences, UUID, command IDs, paramTypes, cleanup ordering |
| `phase4-tmem-ffa-trustkernel-type-evidence.md` | TEEC object sizes/offsets/ownership, what is unknowable |
| `phase4-tmem-ffa-tkcore-consumer-abi.md` | per-symbol tkcore edge report with call sites and error paths |
| `phase4-tmem-ffa-ffa-contract.md` | FF-A driver, partition UUIDs, share/reclaim, handle→PA |
| `phase4-tmem-ffa-gz-contract.md` | KREE symbols, session model, grant/reclaim, provider boundary |
| `phase4-tmem-ffa-object-contract.md` | ops tables, globals, identifier tables, DT dependencies |
| `phase4-tmem-ffa-kcfi-prototypes.tsv` | 23 prototypes with stock KCFI ids |

## 8. Build result

| item | value |
|---|---|
| target | `//lieppos/tmem-ffa:tmem_ffa` |
| BUILD_RC | 0 |
| compiler warnings | 0 (`-Werror` vendor flag active) |
| modpost warnings | 0 |
| unresolved symbols | 0 (all 76 imports resolved) |
| rebuilt SHA256 | see `workspace/phase4-tmem-ffa/build/tmem_ffa.rebuilt.ko` |

## 9. Residual / boundary

- Build-provenance residuals only: `vermagic` git-describe string and the
  `.llvm_addrsig` table encoding (8 bytes total). No functional residual.
- The content of the stock lines behind the `__LINE__` padding is unknown and
  deliberately not invented.
- `tkcore` remains a **stock runtime provider** (`NOT RECONSTRUCTED`), and
  `gz_tz_system` remains a stock runtime provider **outside this task's scope**.
  Both dependencies are explicitly identified and their exact consumer CRCs are
  preserved, which is what permits `FROZEN FOR RE: YES` for `tmem_ffa` itself.
- Nothing was loaded, unloaded, flashed, rebooted or invoked in the secure
  world. Analysis was fully static.

## 10. Verdict

`tmem_ffa.ko` is **behaviourally and ABI closed**: every function is
byte-identical to stock, every import and MODVERSION matches, and every export
CRC is regenerated naturally from MediaTek's own source.

**`DIRECT_SOURCE_MATCH` / `SOURCE_NOW` / FROZEN FOR RE: YES**
