# GQ5012BF1 tkcore island Phase 3E — closure

Classification: **`TKCORE_ISLAND_PHASE3E_PLATFORM_AFFINITY_CLOSED`**.
Static/offline only. Runtime validation and final three-consumer acceptance were not performed.

## Identity and coverage

| Metric | Result |
|---|---|
| stock SHA-256 | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` |
| Phase-3D SHA-256 | `c34a16e78a385a995e626c922bbc02dc756217cca9ef403253dd37999f4031b5` |
| Phase-3E SHA-256 | `caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983` |
| size / Build ID | 199592 / `dd6133a1331bc2e5819d82e363474eb2da76690b` |
| srcversion | `62905469CAF571E2946FD55` |
| vermagic | `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64` |
| depends / import namespace | empty / `DMA_BUF` |
| stock coverage | 117/122 → **122/122** |
| stock-minus-island / island-minus-stock | empty / empty |
| byte-identical functions | 47 → **54** |
| exports | 25/25 → **25/25**, no loss or Phase-3D CRC movement |
| undefined imports | 97 → 101; four new stock imports; no removals |

The island's 101 undefined imports equal the complete stock set plus the pre-existing documented `_dev_err` logging helper. Phase 3E adds only `__cpu_possible_mask`, `_find_next_bit`, `cpu_topology`, and `nr_cpu_ids`.

## Final five

| Function | Stock/rebuilt size | KCFI | Result |
|---|---:|---|---|
| `plat_cpu_is_big` | 68 / 68 | `0xbd7efeae` exact | **EXACT_BYTE** |
| `big_core_affinity_match_cpu` | 36 / 36 | `0x7850c00b` exact | **EXACT_BYTE** |
| `big_core_affinity_get_candidate_cpu` | 144 / 144 | `0x89fb613d` exact | **EXACT_BYTE** |
| `big_core_affinity_need_bind_cpu` | 8 / 8 | `0x98d3ad02` exact | **EXACT_BYTE** |
| `plat_tee_init` | 176 / 176 | `0x36b1c5a6` exact | **EXACT_BYTE** |

`init_module` (64 bytes) and `cleanup_module` (4 bytes) are also newly raw-byte identical to stock.

## Proven policy

- Big CPU criterion: logical CPU's `cpu_topology[cpu].cluster_id` equals the maximum cluster id computed over the possible-CPU mask.
- Candidate: cached first ascending possible CPU matching that criterion; no online/present/current/capacity filter; no match returns `-1`.
- Need-bind: always true, policy-only.
- Actual affinity mutation: **NONE**. The callbacks are dormant const metadata carried only by `tkcore_fp`; stock contains no callback callsite or scheduler-affinity import.
- Platform init: after IDR/lock initialization, compute/store/log max cluster id and return 0; caller discards result. No registration, clock, SPI, proc, sysfs, misc, supplicant, or cleanup action.

## Quality

- Full internal direct-call edge sets: 103 stock / 103 island / zero differences.
- Object, relocation, string, KCFI, import, export, and forbidden-technique audits: PASS.
- Exact-GKI tkcore and layout-probe targets: RC 0; compiler warnings 0; compiler errors 0; modpost warnings 0; unresolved symbols 0; depends empty.
- Verifiers: Phase 3E 167/167; Phase 3D 158/158; Phase 3C-R 59/59; Phase 3C 81/81; Phase 3B 205/205; Phase 3A-R 162/162. Zero `FAIL` lines.
- Todo #18: OPEN. `workspace/phase4-tkcore-island/acceptance/`: empty.

## Scope boundary

This closes provider-internal static function coverage only. It does **not** mean runtime-tested, secure-world-tested, safe to flash, or ready to replace stock. Recommended next work is **Phase 3F — final TrustKernel island acceptance** for `tkcore_drv`, `tmem_ffa`, and `microarray_fp_tee`, including all 19 consumed export edges. Phase 3F was not performed here.
