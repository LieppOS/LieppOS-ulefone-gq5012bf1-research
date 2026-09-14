# Phase 3F — tmem_ffa final-provider acceptance

Result: **PASS_STATIC_FINAL_TKCORE_PROVIDER**

## Build

- Target: `//lieppos/tmem-ffa-phase3f:tmem_ffa_phase3f`
- SHA-256: `aabad7deb8041ac9c9a1ae172f6e015e22e6c75eb146ec77893dcca7a383f442`, size 151448
- RC / compiler warnings / compiler errors / modpost warnings / unresolved: **0 / 0 / 0 / 0 / 0**
- `depends=gz_tz_system,tkcore,ffa_v10`
- Stock tkcore witness: **0**; `stock-provider.symvers` absent from the package

All 84 `src/` and `inc/` entries are symlinks to the frozen pinned MediaTek donor (`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`). Their content hashes are recorded in `acceptance/tmem_ffa/source-hashes.txt`. Only two build-plumbing facts changed: the provider symvers set, and placing the common TrustKernel header ahead of the donor `inc/teec` copy so the single `#include "tee_client_api.h"` in `src/tee_impl/tee_ops.c` resolves to the island authority. **No driver C file was edited.**

## Behavior preservation

| Baseline | Functions | Byte-identical | KCFI diffs | Relocations | Objects changed |
|---|---:|---:|---:|---|---|
| stock oracle `tmem_ffa.stock.ko` | 141/141 | **141/141** | 0 | equal | `____versions`, `__UNIQUE_ID_vermagic333` |
| accepted `tmem_ffa.gzaccept.ko` | 141/141 | **141/141** | 0 | equal | `____versions` |
| accepted `tmem_ffa.rebuilt.ko` | 141/141 | **141/141** | 0 | equal | `____versions` |

The donor's **141/141 stock byte-identity is fully preserved**. Import-name set is 77/77 equal against every baseline. The vermagic object differs only versus stock because stock was built as `-g945dff7bc1bf` while this tree is exact GKI `-maybe-dirty`; that difference predates Phase 3F and is unrelated to provider provenance.

The only semantic delta in the whole module is the `____versions` table, carrying exactly the seven intended TEEC CRC provenance moves.

## Edges

Seven tkcore edges, independently derived from the frozen ELF and confirmed against the frozen provider:

- `NATURAL_HISTORICAL_STOCK_CRC`: **0**
- `ISLAND_NATURAL_PROVIDER_ABI`: **7**
- `BLOCKED`: **0**
- stock tkcore witnesses: **0**

Full provider provenance is in `kernel/phase4-tkcore-island-phase3f-tmem-provider-provenance.md`: 17 intermodule edges (7 tkcore + 1 ffa_v10 + 9 gz_tz_system) all natural, plus 60 exact-GKI edges.

Runtime/device operations: **0**.
