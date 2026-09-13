# `gz_tz_system.ko` — authoritative source-closure report

**Classification: `SOURCE_DELTA_RECONSTRUCTION_EXACT` · FROZEN FOR RE: YES**

**Verifier:** `kernel/scripts/phase4_gz_tz_system_verify.py` — **120/120 checks passed**

## 1. Stock oracle

| item | value |
|---|---|
| SHA256 | `4b29f9b401c43fe98373d17c0360340c0c58f2cc15e2dfbfd536a60bb9484e38` |
| size | 79,648 bytes |
| Build ID | `dcba5910d6fc9b3d5e71f9d172d49a68b3189b1a` |
| compiler | Android (10087095, +pgo, +bolt, +lto, −mlgo, r487747c) clang 17.0.2 |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| name / license | `gz_tz_system` / GPL v2 |
| description / author / srcversion / params / import-ns | **none** (matches vendor source exactly) |
| depends | `gz_ipc_mod,gz_trusty_mod` |
| aliases | `of:N*T*Cmediatek,trusty-tz`, `of:N*T*Cmediatek,trusty-tzC*` |
| placement | `vendor_dlkm`, `modules.load` index **149** (1-based) / 148 (0-based) of 195 |
| recovery | **not present** in any recovery load list |
| copies | **exactly one** repo-wide (471 `.ko` scanned) |
| frozen oracle | `workspace/phase4-gz-tz-system/oracle/gz_tz_system.stock.ko` |
| full record | `kernel/phase4-gz-tz-system-stock-oracle.txt` |

## 2. Source

| item | value |
|---|---|
| result | **`EXACT_SOURCE`** (one 45-line revision delta, §4) |
| tree | `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` |
| revision | `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f` — the **same pin** that closed `ffa_v10` and `tmem_ffa` |
| path | `drivers/misc/mediatek/geniezone/` |
| object list | `gz_tz_system-objs += tz_system.o mtee-kree/tz_mmap.o mtee-kree/kree_mem.o` (proven from the vendor Makefile, not assumed — `gz_main.c` belongs to a *different* module) |
| Kconfig | `CONFIG_MTK_GZ_TZ_SYSTEM` (tristate) = **m** |
| build target | `//lieppos/gz-tz-system:gz_tz_system` against `//common:kernel_aarch64` |
| local source | `/home/armol/kernel-work/gki-12901745-workspace/lieppos/gz-tz-system/` |

Identifier coverage: **61/61 stock functions and 27/27 stock exports** found in
this source; absent `MODULE_DESCRIPTION`/`MODULE_AUTHOR` match the stock
`.modinfo` exactly.

## 3. Config contract (all stock-derived)

| CONFIG | state | proof |
|---|---|---|
| `CONFIG_MTK_GZ_TZ_SYSTEM` | **m** | ships as `.ko`; Kconfig is tristate |
| `CONFIG_MTK_ENABLE_GENIEZONE` | **m** | its `gz-trusty/` subdir ships as the two `depends=` modules |
| `CONFIG_MTK_GZ_KREE` | **ON** | full KREE export surface present |
| `CONFIG_TEE` | **ON** | 5 WEAK `TEEC_*` stubs + 3 `[ERROR] TEEC_* failed` strings |
| `CONFIG_PM_SLEEP` | **ON** | imports `wakeup_source_register`, `__pm_stay_awake`, `__pm_relax` |
| `CONFIG_GZ_VPU_WITH_M4U` | **OFF** | zero `m4u` functions/objects/strings |
| `CONFIG_MTK_ENG_BUILD` | **OFF** | no `KREE_DEBUG` output strings at all |
| `debugFg` | **0** (source constant) | `TZ_GetErrorString` not exported |
| `-faddrsig` | **ON** | stock carries `.llvm_addrsig` |

Full reasoning: `kernel/phase4-gz-tz-system-config-contract.md`.
**No config predicate touches an exported prototype** — which is why the export
ABI was never at risk.

## 4. RED and the single delta

**RED-A** (donor unmodified, stock config): **BUILD FAILED**, 9 ×
`-Werror,-Wvisibility`. At the pinned revision the five `CONFIG_TEE` fallback
stubs are named snake_case and typed against `struct teec_context` /
`teec_session` / `teec_uuid` / `teec_operation` — **types defined nowhere in
that tree**. The `CONFIG_TEE` path simply cannot compile there.

**RED-B** (donor unmodified, `CONFIG_TEE` visibility off): BUILD_RC=0, and
already remarkably close —

| axis | RED-B result |
|---|---|
| shared functions | 56/56, 0 extra |
| byte-identical | **54/56** |
| imports / MODVERSIONs | **50/50 and 51/51 identical** |
| **export CRCs natural** | **27/27** |
| missing | the 5 `TEEC_*` stubs + 3 strings |

Every discrepancy traced to one 45-line block. The delta was closed by
renaming those five weak fallbacks to the GlobalPlatform CamelCase API already
declared by the `tee_client_api.h` included under the same guard — and already
used by the call sites 60 lines below.

**The prototypes were pinned by evidence, not guessed.** clang's kCFI type id
hashes the full prototype *including struct tag names*; the five stock stubs
carry ids byte-identical to tkcore's real implementations:

| symbol | gz_tz_system WEAK stub | tkcore real impl |
|---|---|---|
| `TEEC_InitializeContext` | `0x124b473b` | `0x124b473b` |
| `TEEC_FinalizeContext` | `0xf4c49135` | `0xf4c49135` |
| `TEEC_OpenSession` | `0xde69c0a6` | `0xde69c0a6` |
| `TEEC_CloseSession` | `0x31bed4ef` | `0x31bed4ef` |
| `TEEC_InvokeCommand` | `0x593c5866` | `0x593c5866` |

Five independent 32-bit matches. Bodies were not touched. Full ledger:
`kernel/phase4-gz-tz-system-delta-ledger.tsv` (7 rows: 1 source rename,
5 config-visibility entries, 1 compiler flag).

## 5. Final parity

| axis | stock | rebuilt | result |
|---|---:|---:|---|
| functions | 61 | 61 | exact set, 0 missing, 0 extra |
| size-identical | — | 61 | **61/61** |
| **byte-identical** | — | 61 | **61/61** |
| KCFI type ids | 61 | 61 | **61/61 exact** |
| imports | 50 | 50 | **identical set** |
| MODVERSIONs | 51 | 51 | **identical, every CRC** |
| exports | 27 | 27 | **27/27 CRCs natural** |
| objects | 35 | 35 | 30 exact + 5 `.modinfo` offset-only |
| relocations | 1082 | 1082 | identical |
| strings | 106 | 106 | identical |
| sections | 48 | 48 | identical incl. `.llvm_addrsig` |
| module metadata | — | — | identical (name, license, depends, both aliases) |
| module size | 79,648 | 79,632 | **−16 B** |

Tables: `phase4-gz-tz-system-function-parity.tsv` (61 rows, all `EXACT`),
`phase4-gz-tz-system-object-parity.tsv`.

## 6. Provider provenance (never lumped together)

| class | count | symbols |
|---|---:|---|
| `GKI_NATURAL` | 43 | exact-GKI ab/12901745 kernel symbols |
| `GZ_IPC_STOCK_RUNTIME` | 5 | `tipc_k_connect`, `tipc_k_disconnect`, `tipc_k_read`, `tipc_k_write`, `port_lookup_tid` |
| `GZ_TRUSTY_STOCK_RUNTIME` | 2 | `trusty_std_call32`, `trusty_enqueue_nop` |

`kernel/phase4-gz-tz-system-provider-map.tsv` — all 50 rows, all `EXACT`.

`gz_ipc_mod` and `gz_trusty_mod` are **genuine stock runtime providers**, not
reconstructed modules; their 7 CRCs come from their own `__kcrctab`
(`stock-provider.provenance.json`). This is a declared, open boundary.

## 7. Exports and consumers

27 exports, all `EXPORT_SYMBOL`, **all CRC-natural**. All 471 stock modules
scanned: **5 direct consumers, 35 edges, 35/35 NATURAL, 0 broken.**

| consumer | symbols |
|---|---:|
| `gz_main_mod.ko` | 15 |
| `tmem_ffa.ko` | 9 |
| `cmdq-sec-drv.ko` | 5 |
| `sapu.ko` | 3 |
| `mtk-cam-isp7sp.ko` | 3 |

16 of 27 exports have a consumer; the other 11 are a legacy/test surface that
still reproduces naturally. See `kernel/phase4-gz-tz-system-consumer-abi.md`.

## 8. Behaviour contracts

| document | content |
|---|---|
| `phase4-gz-tz-system-kree-api.md` | all 27 exports: prototypes, CRCs, sizes, kCFI |
| `phase4-gz-tz-system-session-model.md` | 512-slot handle table, reserved sys-service handles, 7 mutexes, lifecycle, retry policy |
| `phase4-gz-tz-system-service-call.md` | `paramTypes` nibble packing, `MTEEC_PARAM`, marshalling, copy-back, reverse REE-service dispatch |
| `phase4-gz-tz-system-secure-memory-api.md` | all 6 tmem-facing memory APIs, units, ownership, error remapping |
| `phase4-gz-tz-system-transport.md` | TIPC-over-Trusty topology, ports, envelope, SMC boundary, threads, DT binding |
| `phase4-gz-tz-system-object-contract.md` | 35 objects, the single ops table, global state |
| `phase4-gz-tz-system-userspace-abi.md` | **proven NONE**, four independent negative proofs |

### Notable recovered facts

- `KREE_SESSION_HANDLE` is an `int32_t` **index**, not a pointer: `0…511`
  index a 512-slot table; `512+TEE_ID_*` are reserved system-service handles.
- Table sizes independently prove `TEE_ID_END == 2` (Trusty + Nebula):
  `4096/512 = 8`, `16/8 = 2`, `8/4 = 2`.
- **Correction to the task brief:** `KREE_ION_AllocChunkmem` and
  `KREE_ION_ZallocChunkmem` take **five** arguments, not four — there is a
  `KREE_SHAREDMEM_HANDLE chm_handle` in second position. Confirmed by the
  vendor header, the C definition, and the shared kCFI id `0x1845c8fb`.
- The 5 `TEEC_*` weak stubs are what the GenieZone→TEE bridge commands bind
  to on this device (gz_tz_system does not link tkcore), so
  `REE_SERVICE_CMD_TEE_*` requests are accepted and **silently no-op'd**.
  That is the shipped behaviour and is now reproduced byte-identically.
- Two defects present in the stock binary, recorded not fixed:
  `_setSessionHandle` returns `-1` on table exhaustion **without unlocking
  `fd_mutex`**; `tz_system_remove` tears nothing down.

## 9. `tmem_ffa` acceptance

`tmem_ffa` was rebuilt with its 9 `KREE_*` witness lines **deleted**, forcing
resolution through the real source-built provider.

| axis | result |
|---|---|
| **9/9 KREE provider CRCs** | **NATURAL** |
| tmem_ffa functions | 141/141 **byte-identical** to stock |
| tmem_ffa KCFI | 141/141 exact |
| tmem_ffa imports / MODVERSIONs | 76/76, 77/77 identical |
| tmem_ffa exports | 15/15 natural |
| behaviour changed? | **No** — only `.note.gnu.build-id` differs vs the frozen baseline |

Provider provenance **before → after**:

| class | before | after |
|---|---:|---:|
| `GKI_NATURAL` | 59 | 59 |
| `FFA_V10_NATURAL` | 1 | 1 |
| `GZ_PROVIDER_STOCK_RUNTIME` | **9** | **0** |
| `GZ_TZ_SYSTEM_NATURAL` | **0** | **9** |
| `TKCORE_STOCK_RUNTIME` | 7 | 7 |

Detail: `kernel/phase4-gz-tz-system-tmem-ffa-acceptance.md`.
`tmem_ffa`'s reconstruction status is **not** reopened.

## 10. Build result

| item | value |
|---|---|
| target | `//lieppos/gz-tz-system:gz_tz_system` |
| BUILD_RC | **0** |
| compiler warnings | **0** |
| modpost warnings | **0** |
| unresolved symbols | **0** (all 50 imports resolved) |
| `KBUILD_MODPOST_WARN` | not used |
| CRC injection / copied `__versions` / ELF patch / fake providers | **none** |
| rebuilt SHA256 | see `workspace/phase4-gz-tz-system/build/gz_tz_system.rebuilt.ko` |

## 11. Residuals

**16 bytes, both pure build provenance, zero functional impact:**

1. `vermagic` git-describe string — `-g945dff7bc1bf` (vendor CI) vs
   `-maybe-dirty` (local). 2 bytes, cascading into 5 `.modinfo` object offsets.
2. `.llvm_addrsig` table encoding — the section is present and correct;
   only its internal encoding differs by 14 bytes.

No functional residual. No unexplained Linux-visible behaviour.

## 12. Boundaries and scope

- `gz_ipc_mod` and `gz_trusty_mod` remain **stock runtime providers**, now
  explicitly declared with exact CRCs. Not reconstructed; not claimed to be.
- `gz_main_mod`, `tkcore`, GenieZone hypervisor/secure-world, TA code and SMC
  semantics are **out of scope** and were not started.
- Static/offline only: nothing loaded, no GenieZone invocation, no
  `KREE_CreateSession`/`KREE_TeeServiceCall` on hardware, no secure-memory
  allocation, no TA invocation, no RPMB, no flash, no reboot, no slot change,
  no sysfs write, no DT/DTBO change, no bind/unbind, no hardware access.

## 13. Verdict

`gz_tz_system.ko` is **behaviourally and ABI closed**: all 61 functions are
byte-identical to stock, all 50 imports and 51 MODVERSIONs match, all 27
export CRCs regenerate naturally from MediaTek's own source, all 35 stock
consumer edges stay natural, and the 9 `tmem_ffa` KREE edges are upgraded from
stock-runtime witnesses to real source-built provider edges.

`SOURCE_DELTA_RECONSTRUCTION_EXACT` is used rather than `DIRECT_SOURCE_MATCH`
because closure required one evidence-backed **source** change (the five weak
stubs), not merely build/config/header selection. The label is chosen to avoid
overstating the result.

**FROZEN FOR RE: YES**
