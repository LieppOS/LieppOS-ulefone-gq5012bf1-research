# GQ5012BF1 GenieZone transport provider stack closure

## Authoritative result

| Module | Classification | Frozen for RE |
|---|---|---|
| `gz_trusty_mod.ko` | **`DIRECT_SOURCE_MATCH`** | **YES** |
| `gz_ipc_mod.ko` | **`DIRECT_SOURCE_MATCH`** | **YES** |

Both modules come unchanged from pinned `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`, build cleanly against exact GKI ab/12901745, reproduce every export naturally, preserve all Linux-visible behavior, and satisfy every stock consumer.

## Closed stack

```text
BEFORE
  gz_trusty_mod [stock runtime] ─► gz_ipc_mod [stock runtime]
                                    │
                                    ▼
                         gz_tz_system [source/frozen]
                                    │
                                    ▼
                            tmem_ffa [source/frozen]

AFTER
  gz_trusty_mod [source/frozen] ─► gz_ipc_mod [source/frozen]
                                    │
                                    ▼
                         gz_tz_system [source/frozen]
                                    │
                                    ▼
                            tmem_ffa [source/frozen]
```

`tkcore` remains an independent stock TrustKernel boundary. `gz_main_mod` remains outside this closure and was not started.

## Quantitative closure

- provider functions: Trusty 33/33 bytes/KCFI; IPC 43/43 bytes/KCFI
- provider natural exports: Trusty 14/14; IPC 15/15
- provider imports/MODVERSIONs: Trusty 59/59 + 60/60; IPC 81/81 + 82/82
- provider relocations: 553/553 + 1003/1003
- all-stock consumer scan: 40/40 edges, 0 broken
- `gz_tz_system` witness removal: 7/7 edges natural
- `gz_tz_system` behavior: 61/61 bytes/KCFI, 50/50 imports, 51/51 MODVERSIONs, 27/27 exports, 1082/1082 relocations, 106/106 strings
- build hygiene: RC 0, compiler warnings 0, modpost warnings 0, unresolved symbols 0

Provider provenance changed exactly from:

```text
43 GKI_NATURAL + 5 GZ_IPC_STOCK_RUNTIME + 2 GZ_TRUSTY_STOCK_RUNTIME
```

to:

```text
43 GKI_NATURAL + 5 GZ_IPC_NATURAL + 2 GZ_TRUSTY_NATURAL
```

## Final build

Target:

`//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport`

The exact vendor directory layout is deliberate and reproduces stock `__FILE__` strings. Both modules are emitted together, so the IPC→Trusty edges resolve in the same real source-built `Module.symvers`. No witness or CRC manipulation is present.

## Residuals

Only build provenance remains: stock versus local vermagic/Build ID and eight non-runtime `.llvm_addrsig` references per module. Each rebuilt file is 8 bytes smaller. Function code, KCFI, runtime objects, imports, MODVERSIONs, natural exports, relocation records, strings, metadata fields, and consumers are closed.

## Fail-closed verification

- `phase4_gz_trusty_mod_verify.py`: **239/239**
- `phase4_gz_ipc_mod_verify.py`: **269/269**
- `phase4_gz_transport_stack_verify.py`: **738/738**

**GENIEZONE TRANSPORT PROVIDER CLOSURE: PASS**
