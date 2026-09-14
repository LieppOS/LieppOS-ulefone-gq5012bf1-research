# Phase 3F — deployment-unit classification

Classification: **B. TRUSTKERNEL_SOURCE_ABI_ISLAND**

Option A (`TKCORE_DROP_IN_PROVIDER`) is **rejected by measurement**: 14 of the 19 stock consumer edges disagree with the Phase-3E provider's naturally generated CRCs, so two of the three original stock consumer binaries would be refused by the module loader.

## Modules that must move together

These three must be deployed as **one unit**, because the rebuilt consumers are the only binaries that agree with the final provider's ABI:

| Module | Reason | Phase-3F artifact |
|---|---|---|
| `tkcore.ko` | the final provider itself | `acceptance/provider/tkcore.phase3e.ko` |
| `tkcore_drv.ko` | 7 of its 11 tkcore edges are category-B | `acceptance/tkcore_drv/tkcore_drv.phase3f.ko` |
| `tmem_ffa.ko` | all 7 of its tkcore edges are category-B | `acceptance/tmem_ffa/tmem_ffa.phase3f.ko` |

## Modules that may remain stock (as far as tkcore ABI is concerned)

| Module | Reason |
|---|---|
| `microarray_fp_tee.ko` | its single tkcore edge `tee_spi_transfer` is `NATURAL_HISTORICAL_STOCK_CRC` (`0x184ce7da`), so the stock binary still agrees |
| `ffa_v10.ko` | not a tkcore consumer; already source-closed and natural |
| `gz_tz_system.ko` | not a tkcore consumer; already source-closed and natural |
| `fingerprint.ko`, `spi-mt65xx.ko` | not tkcore consumers |
| `teeperf.ko` | not a tkcore consumer |

A Phase-3F-built `microarray_fp_tee.ko` exists and is byte-identical in every function to the frozen reconstruction, so it may be shipped with the island or left stock; either choice is ABI-valid.

## Consequences to respect in any later runtime phase

1. The three-module unit must be replaced **atomically**. Mixing a rebuilt `tkcore.ko` with a stock `tkcore_drv.ko` (or vice versa) will fail to load.
2. Existing load order already satisfies provider-before-consumer for the unit and is not modified by Phase 3F.
3. `tmem_ffa` additionally depends on `gz_tz_system` and `ffa_v10`; those stay stock-compatible because their edges were already natural, so they are **not** part of the moving unit.

This is a **static** deployment conclusion only. Nothing was packaged, flashed or loaded.
