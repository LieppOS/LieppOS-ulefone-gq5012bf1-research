# `big_core_affinity_match_cpu` contract

| Property | Proven value |
|---|---|
| stock offset / size | `0x2c18` / 36 bytes |
| binding / export | LOCAL / not exported |
| prototype | `bool (void *context, int cpu)` |
| KCFI | `0x7850c00b` = `_ZTSFbPviE` |
| rebuilt size/KCFI | 36 / `0x7850c00b` |
| classification | **EXACT_BYTE** |

The context argument (`x0`) is ignored. The second argument (`w1`) is the candidate logical CPU. Stock moves it to `w0`, directly calls `plat_cpu_is_big(cpu)`, masks the returned value with 1, and returns that boolean with unchanged polarity: **true means match**.

There is no mask operation, online/present/possible test, fallback, state mutation, current-task access, or log. Invalid/offline behavior is exactly that of `plat_cpu_is_big`.

No executable caller exists in stock. The function is address-taken only by slot 1 of `big_core_affinity_operations`; no callsite of its KCFI type exists. Polarity is therefore proven by its own call/return CFG and ops-slot registration, not inferred from the name or from a nonexistent caller. Raw rebuilt bytes are identical to stock.
