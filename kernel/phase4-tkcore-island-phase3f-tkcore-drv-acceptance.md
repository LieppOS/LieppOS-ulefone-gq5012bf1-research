# Phase 3F — tkcore_drv final-provider acceptance

Result: **PASS_STATIC_FINAL_TKCORE_PROVIDER**

## Build

- Target: `//lieppos/tkcore-drv-phase3f:tkcore_drv_phase3f`
- Output SHA-256: `5f50f77b0d47b7839d78d86baed74a790cd52e0c0654809d685ac9dd712d13a9`
- RC / compiler warnings / compiler errors / modpost warnings / unresolved: **0 / 0 / 0 / 0 / 0**
- `depends=ffa_v10,tkcore`
- Stock tkcore witness: **0**
- Providers: exact GKI, `//lieppos/tkcore-island:tkcore`, `//lieppos/ffa-v10:ffa_v10`

Every implementation C file is a symlink to the frozen reconstruction. The declaration overlay is common-header-derived: genksyms sees the exact common member stream; compiler-only aliases expose the already-proven frozen layout names. The first unqualified common-header attempt changed two bodies and was rejected. Restoring compiler-only `tee_rpc_alloc` and version-array views produced the required exact behavior.

## Behavior preservation

Frozen accepted baseline: `workspace/phase4-tkcore-drv/build/tkcore_drv.stockabi.ko`.

- Function set: 50/50 equal
- Function sizes: 50/50 equal
- Function bytes: **50/50 identical**
- KCFI differences: **0**
- Relocations: **620/620 exactly equal**
- Direct calls: exactly equal
- Object set/sizes: equal; only `____versions` bytes change
- String set: equal except expected source-path string
- Import-name set: 66/66 equal
- srcversion/vermagic/depends: unchanged

Thus no behavior changed merely to naturalize provider provenance.

## Edges

All 11 tkcore import names were independently derived from the frozen ELF. Phase-3F consumer CRC equals the frozen provider CRC for all 11:

- `NATURAL_HISTORICAL_STOCK_CRC`: **4**
- `ISLAND_NATURAL_PROVIDER_ABI`: **7**
- `BLOCKED`: **0**
- stock tkcore witnesses: **0**

The seven intentional `__versions` changes are exactly `__tee_get`, `tee_core_alloc`, `tee_core_add`, `tee_core_del`, `tee_supp_cmd`, `tee_wait_queue_sleep`, and `tee_wait_queue_wakeup`.

## FF-A provenance

The only FF-A edges are `ffa_driver_register` (`0x0d53cde9`) and `ffa_driver_unregister` (`0x3c660e4c`). Both consumer CRCs equal the real source-built `ffa_v10` `Module.symvers`: **NATURAL**.

Runtime/device operations: **0**.
