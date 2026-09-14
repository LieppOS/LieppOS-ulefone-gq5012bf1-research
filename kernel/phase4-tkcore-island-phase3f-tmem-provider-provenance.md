# Phase 3F — tmem_ffa complete provider provenance

Module: `workspace/phase4-tkcore-island/acceptance/tmem_ffa/tmem_ffa.phase3f.ko`
SHA-256: `aabad7deb8041ac9c9a1ae172f6e015e22e6c75eb146ec77893dcca7a383f442`
`depends=gz_tz_system,tkcore,ffa_v10`

The Phase-3F build carries **no** `stock-provider.symvers`; the file does not exist in the package. All 77 `__versions` entries resolve with zero unresolved symbols and zero modpost warnings.

## Import decomposition (77 total)

| Provider | Edges | Natural | Mismatched |
|---|---:|---:|---:|
| exact GKI ab/12901745 (vmlinux) | 60 | 60 | 0 |
| tkcore (final Phase-3E) | 7 | **7** | 0 |
| ffa_v10 (real source-built) | 1 | **1** | 0 |
| gz_tz_system (real source-built) | 9 | **9** | 0 |
| **Total** | **77** | **77** | **0** |

## tkcore — 7 edges, all natural against the final provider

| Symbol | Consumer CRC | Phase-3E provider CRC |
|---|---|---|
| `TEEC_InitializeContext` | `0xf395354f` | `0xf395354f` |
| `TEEC_RegisterSharedMemory` | `0x6f70dc3e` | `0x6f70dc3e` |
| `TEEC_OpenSession` | `0x90aa6e1d` | `0x90aa6e1d` |
| `TEEC_InvokeCommand` | `0xdd7b8804` | `0xdd7b8804` |
| `TEEC_CloseSession` | `0x811d3eaf` | `0x811d3eaf` |
| `TEEC_ReleaseSharedMemory` | `0xee29e3f5` | `0xee29e3f5` |
| `TEEC_FinalizeContext` | `0xd203900b` | `0xd203900b` |

These are the only seven `__versions` entries that differ from the historical record. They are `ISLAND_NATURAL_PROVIDER_ABI`: the provider and consumer are compiled against one authoritative `trustkernel/tee_client_api.h`, so genksyms produces mutually agreeing values without any injection.

## ffa_v10 — 1 edge, NATURAL

`ffa_driver_register` = `0x0d53cde9`, equal to the real source-built `//lieppos/ffa-v10` `Module.symvers`.

## gz_tz_system — 9 edges, NATURAL

`KREE_AppendSecureMultichunkmem` `0x9a19c31a`, `KREE_CloseSession` `0x5878d629`, `KREE_ConfigSecureMultiChunkMemInfo` `0xbdb6a34b`, `KREE_CreateSession` `0x552d4efc`, `KREE_ION_AllocChunkmem` `0x3d5d5254`, `KREE_ION_UnreferenceChunkmem` `0x8dceb484`, `KREE_ION_ZallocChunkmem` `0x0175c8da`, `KREE_ReleaseSecureMultichunkmem` `0x44781e48`, `KREE_TeeServiceCall` `0xec19e146` — every value equal to the real source-built `//lieppos/gz-tz-system` `Module.symvers`.

This is a strict improvement over the historical `tmem_ffa` build, which recorded 16 edges (7 tkcore + 9 KREE) from stock provider ELFs. Phase 3F reduces that to **zero** stock-derived ABI records.
