# GQ5012BF1 tkcore Phase 3E — regression report

## Functional delta

Exactly five stock functions were added and all are raw-byte identical:

- `big_core_affinity_need_bind_cpu`
- `big_core_affinity_match_cpu`
- `big_core_affinity_get_candidate_cpu`
- `plat_cpu_is_big`
- `plat_tee_init`

`init_module` and `cleanup_module` were repaired to stock behavior and are also raw-byte identical. No other stock function body lost raw-byte identity. Byte-identical count increases 47→54.

## Closed phases

The four Phase-3D target bodies, sizes, KCFI, calls, relocations, strings, export CRCs and consumer edges are unchanged. Phase 3C-R, 3C, 3B and 3A-R functions remain present; no function was removed. Full internal direct-call edge sets are equal at 103/103.

All 25 export names, Phase-3D CRCs, and KCFI values are unchanged. The five Phase-3E functions are internal and were not exported.

## Imports

Undefined imports move 97→101. Exactly four were added: `__cpu_possible_mask`, `_find_next_bit`, `cpu_topology`, and `nr_cpu_ids`; all four exist in stock and are directly required by raw-byte-identical Phase-3E bodies. Stock has 100 undefined imports; the sole island-minus-stock import remains the pre-Phase-3D documented `_dev_err` logging convention. No Phase-3E non-stock import was added and no import was removed.

## Objects and strings

Only four named object symbols were added: `large_cluster_id`, the function-static `candidate_cpu`, `big_core_affinity`, and `big_core_affinity_operations`. The existing `tkcore_fp` descriptor's reserved pointer changed from NULL to the proven const affinity object. Layouts, initial values and relocation topology match stock. Both reached strings match stock exactly, including the doubled `tkcore:` quirk.

## Monotone verifier maintenance

`phase4_tkcore_island_phase3d_verify.py` retained every behavioral Phase-3D assertion. Only temporal scope guards were made monotone:

- coverage accepts the original 117 state or complete 122 Phase-3E state;
- additions must be exactly the Phase-3D four, optionally plus the complete named Phase-3E five;
- missing set must be the Phase-3E five or empty;
- later imports must belong to stock;
- later objects are restricted to the five named Phase-3D/3E objects;
- Phase 3E must be wholly absent or wholly present.

It still rejects partial Phase-3E progress, island-only functions/imports/objects, export drift, and any Phase-3D behavioral regression.

Three older temporal guards also received monotone maintenance without changing their check counts or deleting behavioral assertions:

- Phase 3C-R allows only its target plus the optional stock-exact Phase-3E `init_module`/`cleanup_module` size repair, and only later imports found in stock; its Phase-3E boundary is all-or-none.
- Phase 3C permits only the pre-existing `_dev_err` excess over the stock import set and likewise requires Phase 3E all-or-none.
- Phase 3B accepts both `N of 122` and `N/122` live work-queue notation and verifies the surviving shared-memory section instead of requiring an obsolete top-paragraph phrase.

All continue to reject regression below their own achieved coverage. Nothing was deleted or weakened to permit incorrect behavior.

## Scope

No consumer, DT/DTBO, stock object, ELF metadata, CRC table, Module.symvers, or acceptance-directory content was modified. No runtime/device operation occurred. Todo #18 remains open.

Result: **NO UNEXPLAINED REGRESSION**.
