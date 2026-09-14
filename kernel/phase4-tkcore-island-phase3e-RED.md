# GQ5012BF1 tkcore island Phase 3E — RED

**Immutable. Recorded before any Phase-3E source edit.**

Baseline: Phase-3D `c34a16e78a385a995e626c922bbc02dc756217cca9ef403253dd37999f4031b5`, 117/122 functions, 25/25 exports, 97 imports, zero island-only functions.
Stock oracle: `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`.

## RED status — all five targets ABSENT

| Target | Stock off | Size | Bind/sec | Stock KCFI | Address taken | Phase 3D |
|---|---:|---:|---|---|---|---|
| `big_core_affinity_need_bind_cpu` | `0x2c0c` | 8 | LOCAL `.text` | `0x98d3ad02` | yes: ops slot 0 | **ABSENT** |
| `big_core_affinity_match_cpu` | `0x2c18` | 36 | LOCAL `.text` | `0x7850c00b` | yes: ops slot 1 | **ABSENT** |
| `big_core_affinity_get_candidate_cpu` | `0x2c40` | 144 | LOCAL `.text` | `0x89fb613d` | yes: ops slot 2 | **ABSENT** |
| `plat_cpu_is_big` | `0x95e8` | 68 | GLOBAL `.text` | `0xbd7efeae` | no; direct calls only | **ABSENT** |
| `plat_tee_init` | `0x97d4` | 176 | GLOBAL `.text` | `0x36b1c5a6` | no; direct call only | **ABSENT** |

No target is exported in stock. Phase 3E must not export one.

## Per-target facts

### `big_core_affinity_need_bind_cpu`

- Exact prototype from KCFI inversion: `bool (void *)` (`_ZTSFbPvE`).
- CFG/instructions: `mov w0,#1; ret`; context argument is ignored.
- Callers/callees/imports/objects/strings: none.
- CPU masks, per-CPU state, scheduler calls, DT/platform calls: none.
- Return: always true. It is policy-only and performs no mutation.

### `big_core_affinity_match_cpu`

- Exact prototype: `bool (void *, int)` (`_ZTSFbPviE`).
- Context in `x0` is ignored; candidate CPU in `w1` is moved to `w0`.
- Calls `plat_cpu_is_big(cpu)` at callsite `0x2c28`; masks result with `& 1` and returns it unchanged in polarity.
- No mask operation, online/present test, state access, scheduler call, DT access, log, or fallback.
- No executable caller exists; address is retained by ops slot 1.

### `big_core_affinity_get_candidate_cpu`

- Exact prototype: `int (void *)` (`_ZTSFiPvE`); context is ignored.
- Reads function-static `.data+0x78` `candidate_cpu`, initial value `-1`.
- If cached value is nonnegative, returns it immediately without revalidation.
- Otherwise enumerates `__cpu_possible_mask` from CPU 0 upward using `_find_next_bit(mask, nr_cpu_ids, start)`.
- Calls `plat_cpu_is_big(cpu)` at `0x2c94`; first matching possible CPU is cached.
- On first match logs `"\x016tkcore: candidate big cpu set to %d\n"` and returns it.
- If no match exists, leaves/returns `-1`. No online/present/current-CPU filter, no capacity/scheduler helper, no hard-coded CPU order, no fallback CPU.
- Address is retained by ops slot 2; no executable caller exists.

### `plat_cpu_is_big`

- Exact prototype: `bool (int)` (`_ZTSFbiE`).
- Reads `.data+0x208` `large_cluster_id`, initial value `-1`; returns false while uninitialized.
- For initialized state, compiler bounds-checks `cpu_topology[cpu]` against exact `NR_CPUS=32`; invalid signed values become unsigned out-of-range and execute UBSAN `brk #0x5512`.
- Reads `cpu_topology[cpu].cluster_id` at stride 56, member offset 8, and returns equality with `large_cluster_id`.
- Exact GKI `struct cpu_topology`: `cluster_id` is at +8 and `sizeof` is 56 with `CONFIG_NR_CPUS=32`.
- No mask, online/present test, capacity helper, MPIDR, DT, scheduler call, log, or import beyond `cpu_topology`.
- Direct callers: `big_core_affinity_match_cpu` (`0x2c28`) and `big_core_affinity_get_candidate_cpu` (`0x2c94`).

### `plat_tee_init`

- Exact prototype: `int (void)` (`_ZTSFivE`).
- Sole caller: `init_module`, stock `.init.text+0x30`; return value is discarded.
- Enumerates `__cpu_possible_mask` from 0 upward with `_find_next_bit` and `nr_cpu_ids`.
- Computes the signed maximum `cpu_topology[cpu].cluster_id`, starting at `-1`, then stores it to `large_cluster_id`.
- Logs stock string `"\x016tkcore: tkcore: big cluster_id = %d\n"` (the doubled `tkcore:` prefix is real).
- Always returns 0. Empty possible mask stores/logs `-1`. No allocation, registration, clock/SPI call, DT interaction, lock, error branch, cleanup, or idempotence guard.
- Repeated calls recompute and overwrite the same global.

## Objects and static registration

| Object | Stock location/size | Initial contents | Role |
|---|---|---|---|
| `candidate_cpu` | `.data+0x78`, 4 | `ffffffff` (`-1`) | first-big-possible-CPU cache |
| `large_cluster_id` | `.data+0x208`, 4 | `ffffffff` (`-1`) | maximum possible-CPU cluster id |
| `big_core_affinity` | `.rodata+0x220`, 16 | reloc to ops, then NULL | affinity descriptor |
| `big_core_affinity_operations` | `.rodata+0x230`, 24 | three relocations | need/match/candidate callbacks |
| `tee_device_configs[2].affinity` | `.data+0x60`, 8 | reloc to `.rodata+0x220` | only `tkcore_fp` carries descriptor |

Ops layout is exact: +0 need-bind, +8 match, +16 get-candidate. Local-symbol relocations are represented as `.text + 0x2c0c/0x2c18/0x2c40`, not by function name.

## Actual mutation RED finding

Stock imports no `set_cpus_allowed_ptr`, sched-setaffinity helper, migration helper, kthread affinity helper, or workqueue-affinity helper. No KCFI callsite with any of the three callback type IDs exists. `tee_device_configs` has one code reference, from `tee_core_add`; that function reads only descriptor `available` at +0x20 and never reads `affinity` at +0x10. Other descriptor consumers read node flags, not affinity.

Therefore **none of the five functions changes affinity, and stock contains no reachable affinity mutation point for this object**. The callback graph is dormant metadata on GQ5012BF1.

## Frozen oracle

Relocation-aware disassembly is preserved in `workspace/phase4-tkcore-island/phase3e/oracle/`. This RED record is not to be edited after implementation begins.
