# GQ5012BF1 tkcore island Phase 3F — combined final acceptance

Classification: **`TKCORE_ISLAND_PHASE3F_FINAL_CONSUMER_ACCEPTANCE_PASS`**

Static/offline only. **Runtime validation: NOT PERFORMED.** Zero device operations.

## What this proves

The statically complete Phase-3E `tkcore` provider is consumed **from source** by all three real Linux consumers with **zero stock-tkcore ABI witness**. The stock `tkcore.ko` is no longer *statically* required by `tkcore_drv`, `tmem_ffa` or `microarray_fp_tee`.

It does **not** mean runtime-safe, secure-world-tested, KeyMint/Gatekeeper/FBE/fingerprint-tested, or ready to flash.

## Provider — unchanged

| Field | Value |
|---|---|
| SHA-256 before and after Phase 3F | `caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983` |
| Provider mutated by Phase 3F? | **NO** — rebuilt and re-hashed after all consumer builds |
| Stock function coverage | 122/122 |
| Missing / island-only | 0 / 0 |
| Exports | 25/25 |
| `depends` | empty |

## Consumer results

| Consumer | Build | Functions | Byte-identical vs baseline | KCFI diffs | Relocations | tkcore edges | Result |
|---|---|---:|---|---:|---|---:|---|
| `tkcore_drv` | RC 0, clean | 50 | **50/50** | 0 | equal | 11/11 | **PASS_STATIC_FINAL_TKCORE_PROVIDER** |
| `tmem_ffa` | RC 0, clean | 141 | **141/141** (also vs stock oracle) | 0 | equal | 7/7 | **PASS_STATIC_FINAL_TKCORE_PROVIDER** |
| `microarray_fp_tee` | RC 0, clean | 27 | **27/27** | 0 | equal | 1/1 | **PASS_STATIC_FINAL_TKCORE_PROVIDER** |

Every build: 0 compiler warnings, 0 compiler errors, 0 modpost warnings, 0 unresolved symbols, no `KBUILD_MODPOST_WARN`, no unresolved allowlist, no fake symvers.

In all three, the **only** semantic change is the `____versions` table. No function body changed to make anything link.

## The 19 edges

| Classification | Count |
|---|---:|
| `NATURAL_HISTORICAL_STOCK_CRC` | **5** |
| `ISLAND_NATURAL_PROVIDER_ABI` | **14** |
| `BLOCKED` | **0** |
| **N + M** | **19** |
| stock tkcore witnesses used | **0** |

Independently derived from the frozen consumer ELFs — 11 + 7 + 1 — matching the expected inventory exactly, with no extra or missing import.

The 5 category-A edges: `tee_map_cached_shm`, `tee_clkmgr_handle`, `tee_wait_queue_init`, `tee_wait_queue_exit`, `tee_spi_transfer`.

The 14 category-B edges are documented individually in `phase4-tkcore-island-phase3f-private-abi-provenance.md`. Their historical CRCs hash TrustKernel private member *spellings* that do not exist in a stripped `.ko`; the complete source island instead uses one naturally generated ABI, proven correct by byte-identical codegen across all 218 consumer functions.

## Non-tkcore providers — all natural

| Edge | Count | Result |
|---|---:|---|
| `ffa_v10` → `tkcore_drv` | 2 | NATURAL |
| `ffa_v10` → `tmem_ffa` | 1 | NATURAL |
| `gz_tz_system` → `tmem_ffa` | 9 | NATURAL |
| `fingerprint` → `microarray_fp_tee` | 4 | NATURAL |
| `spi-mt65xx` → `microarray_fp_tee` | 2 | NATURAL |

`tmem_ffa` historically recorded 16 edges from stock provider ELFs (7 TEEC + 9 KREE); Phase 3F reduces that to **zero**.

## Deployment conclusion (static)

**B. TRUSTKERNEL_SOURCE_ABI_ISLAND.** Measured stock-binary compatibility is 5/19, so `tkcore` cannot be swapped alone. `tkcore.ko` + `tkcore_drv.ko` + `tmem_ffa.ko` must move together. Stock `microarray_fp_tee.ko` remains compatible because its single edge is category-A.

## Verifiers

| Verifier | Result |
|---|---|
| **Phase 3F** | **181/181 CHECKS PASSED** |
| Phase 3E / 3D / 3C-R / 3C / 3B / 3A-R | 167/167 · 158/158 · 59/59 · 81/81 · 205/205 · 162/162 |
| `tkcore_drv` / `tmem_ffa` / fingerprint | 43/43 · 76/76 · 39/39 |
| `ffa_v10` / `gz_tz_system` / `spi-mt65xx` | 49/49 · 121/121 · 82/82 |

No verifier was weakened. The four acceptance-boundary guards were made monotone and strictly stronger; see `phase4-tkcore-island-phase3f-verifier-maintenance.md`.

## Status after Phase 3F

- TKCORE LINUX-SIDE SOURCE ISLAND: **STATICALLY COMPLETE**
- STOCK TKCORE RUNTIME DEPENDENCY: **STATICALLY ELIMINATED**
- RUNTIME VALIDATION: **NOT PERFORMED**
- TKCORE REPLACEMENT READY: **NO**

Next: **Phase 3G — controlled Slot-B TrustKernel runtime validation** (not performed here).
