# `big_core_affinity_get_candidate_cpu` contract

| Property | Proven value |
|---|---|
| stock offset / size | `0x2c40` / 144 bytes |
| binding / export | LOCAL / not exported |
| prototype | `int (void *context)` |
| KCFI | `0x89fb613d` = `_ZTSFiPvE` |
| rebuilt size/KCFI | 144 / `0x89fb613d` |
| classification | **EXACT_BYTE** |

## Selection algorithm

- Ignore `context`.
- Function-static `candidate_cpu` starts at `-1`.
- If it is nonnegative, return it immediately; stock never revalidates topology, possibility, or online state.
- Otherwise enumerate `__cpu_possible_mask` in ascending logical-CPU order, beginning at 0, through `_find_next_bit(mask, nr_cpu_ids, start)`.
- Select the first CPU for which `plat_cpu_is_big(cpu)` returns true.
- Cache it, emit `"\x016tkcore: candidate big cpu set to %d\n"`, and return it.
- If enumeration reaches `nr_cpu_ids` without a match, preserve and return `-1`.

There is no online/present-mask filter, current-CPU preference/avoidance, hard-coded ordering, capacity/scheduler helper, retry, or alternate fallback. An offline-but-possible CPU can be selected. No candidate means `-1`, not CPU 0.

The address is retained by ops slot 2, but there is no executable stock callsite. Raw rebuilt bytes are identical to stock.
