# `plat_tee_init` contract

| Property | Proven value |
|---|---|
| stock offset / size | `0x97d4` / 176 bytes |
| binding / export | GLOBAL / not exported |
| prototype | `int plat_tee_init(void)` |
| KCFI | `0x36b1c5a6` = `_ZTSFivE` |
| rebuilt size/KCFI | 176 / `0x36b1c5a6` |
| classification | **EXACT_BYTE** |

## Ordering and behavior

Stock `init_module` calls it after initializing `tee_idr_lock` and `tee_idr`. The call result is discarded and `init_module` returns literal 0.

`plat_tee_init`:

1. starts a local maximum at `-1`;
2. enumerates `__cpu_possible_mask` in ascending order with `_find_next_bit`/`nr_cpu_ids`;
3. reads exact-GKI `cpu_topology[cpu].cluster_id` and keeps the signed maximum;
4. writes static `large_cluster_id`;
5. logs exact reached string `"\x016tkcore: tkcore: big cluster_id = %d\n"`;
6. returns 0 unconditionally.

An empty possible mask stores/logs `-1`. The compiler-generated exact array-bounds trap applies if a malformed possible mask produces CPU >= `NR_CPUS`.

It performs no registration, allocation, lock operation, DT access, affinity callback invocation, clock/SPI action, proc/sysfs/misc/supplicant setup, or error propagation. It is not placed in `.init.text` itself; only its caller is module-init code. It has no cleanup requirement and no idempotence guard; a repeated call recomputes and overwrites the same integer.

Raw rebuilt bytes are identical to stock.
