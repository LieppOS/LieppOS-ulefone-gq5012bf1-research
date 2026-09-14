# GQ5012BF1 tkcore island Phase 3A-R — final acceptance

## Result

**TKCORE ISLAND PHASE 3A-R: CORE + CONTEXT/SESSION STATIC PASS**

This closes the requested static scope only. It does not certify a replacement module or runtime readiness.

## Closed APIs

### Core/provider lifecycle

| API | KCFI | Call set | Acceptance |
|---|---|---|---|
| `tee_core_alloc` | exact | exact | `CFG_EQUIVALENT` |
| `tee_core_add` | exact | exact | `CFG_EQUIVALENT` |
| `tee_core_del` | exact | exact | `EXACT_BYTE` |
| `tee_core_free` | exact | exact | `EXACT_BYTE` |
| `__tee_get` | exact | exact | `CFG_EQUIVALENT`, exported |

### Opaque IDR handles

`tee_core_alloc_uuid`, `tee_core_uuid2ptr`, and `tee_core_free_uuid` are present, have exact KCFI, and are byte-identical to stock. Handles are positive IDR ids beginning at 1; no pointer-to-int conversion remains in the context/session API.

### TEEC context/session lifecycle

| API | Stock / island size | KCFI | Call set | Acceptance |
|---|---:|---|---|---|
| `TEEC_InitializeContext` | `240 / 216` | exact | exact | `CFG_EQUIVALENT` |
| `TEEC_FinalizeContext` | `164 / 176` | exact | exact | `CFG_EQUIVALENT` |
| `TEEC_OpenSession` | `412 / 412` | exact | exact | `SIZE_EXACT_SEMANTIC_EXACT` |
| `TEEC_CloseSession` | `96 / 96` | exact | exact | `EXACT_BYTE` |

Detailed contracts:

- `phase4-tkcore-context-contract.md`
- `phase4-tkcore-session-contract.md`
- `phase4-tkcore-idr-handle-contract.md`
- `phase4-tkcore-island-phase3a-r-core-acceptance.md`

## Static consumers

- Frozen `tmem_ffa`: **PASS_STATIC** for `InitializeContext → OpenSession → CloseSession → FinalizeContext`.
- Frozen `tkcore_drv`: **PASS_STATIC** for its natural `tee_core_alloc → tee_core_add → __tee_get` constructor and `tee_core_del` unwind/removal edges. `tee_core_free` is closed but not called by this frozen consumer.

No full three-consumer island acceptance build was performed. Shared-memory and invocation calls visible in `tmem_ffa` remain outside this phase.

## Final exact-GKI build

Targets:

```text
//lieppos/tkcore-island:tkcore
//lieppos/trustkernel-layout:tk_layout_probe
```

| Gate | Result |
|---|---:|
| `BUILD_RC` | `0` |
| compiler warnings | `0` |
| compiler errors | `0` |
| modpost warnings | `0` |
| unresolved symbols | `0` |
| static-assert failures | `0` |
| module `depends` | empty |

Final build log: `workspace/phase4-tkcore-island/phase3a-r/build/final-build.log`.

Final ELF:

- SHA-256: `9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b`
- Size: `164032` bytes
- Build ID: `4cf34b11fcc60e92c5a09b926f9f2d3b7c88a41e`
- `vermagic`: `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64`
- `srcversion`: `CD46AAA7D1DA68FC83CABEB`
- `depends`: empty

## Stock → Phase-3P → Phase-3A-R

| Metric | Stock | Phase-3P | Phase-3A-R |
|---|---:|---:|---:|
| ELF size | `221352` | `158896` | `164032` |
| stock-function coverage | `122/122` | `85/122` | `91/122` |
| stock functions missing | `0` | `37` | `31` |
| byte-identical stock functions | `122` | `27` | `33` |
| KCFI-exact shared functions | `122` | `77` | `83` |
| exports | `25` | `18` | `19` |
| undefined imports | `100` | `84` | `94` |
| defined objects | `54` | `46` | `50` |
| relocations | `3098` | `2246` | `2288` |
| `.text` | `0x9884` | `0x73c0` | `0x761c` |
| `.data` | `0x20c` | `0x208` | `0x298` |
| `.bss` | `0xa1` | `0x80` | `0x88` |
| `.rodata` | `0x6a3` | `0x4e8` | `0x5f8` |

No shared stock function, byte-identical function, or KCFI match regressed from Phase-3P. The six newly present stock functions are `__tee_get`, the three IDR helpers, `tee_supp_open`, and `tee_supp_release`. The supplicant open/release callbacks were included only because the stock core fops require them; general RPC command handling was not entered.

All new Phase-3A-R imports exist in stock. The two island imports not present in stock (`_dev_err`, `sg_nents`) predate this phase and are not new regressions. No export was fabricated. Six stock exports remain absent.

Machine-readable inventories:

- `phase4-tkcore-island-phase3a-r-functions.tsv`
- `phase4-tkcore-island-phase3a-r-kcfi-all.tsv`
- `phase4-tkcore-island-phase3a-r-imports.tsv`
- `phase4-tkcore-island-phase3a-r-exports.tsv`
- `phase4-tkcore-island-phase3a-r-objects.tsv`
- `phase4-tkcore-island-phase3a-r-relocations.tsv`
- `phase4-tkcore-island-phase3a-r-callgraph.tsv`
- `phase4-tkcore-island-phase3a-r-strings.tsv`
- `phase4-tkcore-island-phase3a-r-metadata.tsv`

## Forbidden techniques

No in-scope speculative success stub, fake provider, CRC injection, `__versions` edit, ELF patch, stock object inclusion, or `KBUILD_MODPOST_WARN` was used. Out-of-scope donor shared-memory/InvokeCommand bodies are not accepted by this report.

## Overall status

- Overall tkcore: **PARTIAL**
- Runtime readiness: **NOT RUNTIME READY**
- Runtime provider: **STOCK RUNTIME PROVIDER**
- Tkcore replacement ready: **NO**
- Stock tkcore runtime dependency: **STILL PRESENT**
- Next: **PHASE 3B SHARED-MEMORY RECONSTRUCTION**
