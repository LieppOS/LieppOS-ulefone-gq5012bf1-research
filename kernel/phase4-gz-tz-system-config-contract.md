# `gz_tz_system.ko` — stock build-config contract

Every entry is derived from the stock ELF, never from a "sensible default".
GenieZone has many options; only the ones that actually reach these three
translation units (`tz_system.c`, `mtee-kree/tz_mmap.c`, `mtee-kree/kree_mem.c`)
are in scope.

## 1. Module-selecting config

| CONFIG | state | evidence | effect |
|---|---|---|---|
| `CONFIG_MTK_GZ_TZ_SYSTEM` | **MODULE** | stock ships `gz_tz_system.ko` as a loadable module in `vendor_dlkm`; Kconfig type is `tristate` | selects `gz_tz_system-objs = tz_system.o mtee-kree/tz_mmap.o mtee-kree/kree_mem.o` |
| `CONFIG_MTK_ENABLE_GENIEZONE` | **MODULE** | the `gz-trusty/` subdirectory it selects ships as `gz_trusty_mod.ko` + `gz_ipc_mod.ko`, which are exactly this module's two `depends=` entries | provides `trusty_std_call32`, `trusty_enqueue_nop`, `tipc_k_*`, `port_lookup_tid` |
| `CONFIG_MTK_GZ_KREE` | **ON** | KREE API surface (all 27 exports) is present | enables the KREE client API |
| `CONFIG_HAVE_MTK_ENABLE_GENIEZONE` | **ON** | prerequisite of `MTK_ENABLE_GENIEZONE`, which is on | gating only |

## 2. Configs that change this module's code

### `CONFIG_TEE` — **ON**

Decisive, and the subject of the only source delta.

* Stock defines five **WEAK** functions that exist only inside
  `#if IS_ENABLED(CONFIG_TEE)`:
  `TEEC_InitializeContext` (8 B), `TEEC_FinalizeContext` (4 B),
  `TEEC_OpenSession` (8 B), `TEEC_CloseSession` (4 B),
  `TEEC_InvokeCommand` (8 B).
* Stock carries three format strings that exist only in the `CONFIG_TEE` case
  arms of `_GzServiceCall_body`:
  `[KREE][ERR][ERROR] TEEC_InitializeContext failed: %x`,
  `… TEEC_OpenSession failed: %x`, `… TEEC_InvokeCommand failed: %x`.
* With `CONFIG_TEE` off (RED-B) the module is missing exactly those 5
  functions and 3 strings, and `_GzServiceCall_body` / `_Gz_KreeServiceCall_body`
  shrink.

**ABI effect: none.** The weak stubs are not exported and do not appear in
`__versions`; all 27 export CRCs are identical with `CONFIG_TEE` on or off.
This is why RED-B could already reproduce 27/27 natural CRCs.

### `CONFIG_PM_SLEEP` — **ON**

* Stock imports `wakeup_source_register` `0x8be45c3b`, `__pm_stay_awake`
  `0xe186a5ce`, `__pm_relax` `0x1aa68695`.
* All three appear only inside `#if IS_ENABLED(CONFIG_PM_SLEEP)` blocks in
  `tz_system.c` (the `TeeServiceCall_wake_lock` declaration, the
  `KREE_TeeServiceCall` perf-boost path, and `tz_system_probe`).

**Effect:** adds the `struct wakeup_source *TeeServiceCall_wake_lock` global
and the wake-lock arms of the perf-boost helper. Does not alter any exported
prototype.

### `CONFIG_GZ_VPU_WITH_M4U` — **OFF**

* Stock contains **zero** occurrences of `m4u` in functions, objects or
  strings. `gz_do_m4u_map` / `gz_do_m4u_umap` are absent as both definitions
  and imports.
* Enabling it would inject calls into `_kree_mcm_Append`, `_kree_mcm_Release`
  and `KREE_ConfigSecureMultiChunkMemInfo` (4 sites in `kree_mem.c`).

**Effect if wrongly enabled:** three exported secure-memory functions would
change size and gain an unresolved import. Guarded against.

### `CONFIG_MTK_ENG_BUILD` — **OFF**

* `CONFIG_MTK_ENG_BUILD` defines `DBG_KREE_SYS`, which promotes `KREE_DEBUG`
  from a no-op to `pr_info("[KREE]" …)`.
* Stock contains **no** `KREE_DEBUG`-only text at all (e.g. the distinctive
  `=====>` traces appear 0 times), while `KREE_INFO`/`KREE_ERR` strings are
  present — exactly the `#else` arm.

**Effect if wrongly enabled:** dozens of extra strings; nearly every function
would grow.

### `CONFIG_CHUNKMEM_INFO_ION` — **not a config here**

`TZCMD_MEM_CONFIG_CHUNKMEM_INFO_ION` is a *command constant*, not a Kconfig
predicate. Listed to close out the grep hit; it is unconditional.

## 3. Source-internal predicates (not Kconfig)

| predicate | value | evidence |
|---|---|---|
| `debugFg` | **0** (hardcoded in source) | stock does **not** export `TZ_GetErrorString`, which `#if debugFg` would export; and the header that block includes (`tz_cross/tz_error_strings.h`) does not exist at the pinned revision |
| `API_sharedMem` | **1** | `KREE_RegisterSharedmem` / `KREE_UnregisterSharedmem` exported |
| `API_secureMem` | **1** | `KREE_AllocSecuremem` … `KREE_UnreferenceSecuremem` exported |
| `API_chunkMem` | **1** | `KREE_ION_AllocChunkmem` … `KREE_QueryChunkmem_TEST` exported |
| `DYNAMIC_TIPC_LEN` | defined | hardcoded `#define` in `tz_system.c` |
| `DBG_KREE_SHM` | undefined | no `[KREE_MEM]` debug strings |
| `FIX_MEM_DATA_BUFFER`, `GP_PARAM_DEBUG` | undefined | no corresponding strings/functions |

## 4. Compiler / toolchain

| item | value | evidence |
|---|---|---|
| clang | Android r487747c, 17.0.2 (+pgo +bolt +lto −mlgo) | `.comment` in stock, identical to exact-GKI 12901745 toolchain |
| `-faddrsig` | **ON** | stock carries a `.llvm_addrsig` (`LLVM_ADDRSIG`) section |
| kCFI | ON | 61/61 functions carry stock-matching type ids |
| MODVERSIONS | ON | `__versions` present, `vermagic` says `modversions` |

## 5. Final config set used by the closure

```make
ccflags-y += -faddrsig
ccflags-y += -DCONFIG_MTK_GZ_TZ_SYSTEM_MODULE=1
ccflags-y += -DCONFIG_MTK_ENABLE_GENIEZONE=1
ccflags-y += -DCONFIG_MTK_GZ_KREE=1
ccflags-y += -DCONFIG_TEE=1
```

`CONFIG_PM_SLEEP` comes from the exact-GKI kernel config (already `y`).
`CONFIG_GZ_VPU_WITH_M4U` and `CONFIG_MTK_ENG_BUILD` are deliberately left
unset. This set reproduces 61/61 functions byte-identically.

## 6. genksyms sensitivity note

The task brief flagged that config-controlled KREE/secure-memory struct
layouts can move export CRCs. Verified empirically: **none of the five
relevant predicates touches an exported prototype or any struct reachable from
one.** `KREE_SESSION_HANDLE` (`int32_t`), `KREE_SECUREMEM_HANDLE` /
`KREE_SHAREDMEM_HANDLE` (`uint32_t`), `union MTEEC_PARAM` and
`KREE_SHAREDMEM_PARAM` are all unconditional. That is why 27/27 export CRCs
were already natural in RED-B, before any delta was applied.
