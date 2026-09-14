# GQ5012BF1 tkcore — affinity mutation audit

## Result: NONE

No function in the stock `tkcore.ko` performs a CPU-affinity mutation for the recovered `big_core_affinity` object.

## Proof

1. Undefined imports include `__cpu_possible_mask`, `nr_cpu_ids`, `_find_next_bit`, and `cpu_topology`, but do **not** include `set_cpus_allowed_ptr`, sched-setaffinity-like helpers, migration helpers, kthread-affinity helpers, or workqueue-affinity helpers.
2. `big_core_affinity_need_bind_cpu`, `match_cpu`, and `get_candidate_cpu` are address-taken by a 24-byte const ops table, but the entire stock image contains no KCFI indirect-call sequence for any of their three type IDs.
3. `big_core_affinity` is referenced only by `tee_device_configs[2].affinity` (`tkcore_fp`).
4. The only code reference to `tee_device_configs` is `tee_core_add`. It reads `available` at descriptor +0x20 and copies descriptor/name/fops data; it never reads affinity at +0x10.
5. Other descriptor consumers use the record for `supplicant`/node identity and likewise never dereference affinity.

## Consequences

- task pointer source: none
- target cpumask: none
- mutation function: none
- mutation return/error handling: none
- restore behavior: none
- undo point: none

The object is dormant policy metadata in this GQ5012BF1 build. Reconstruction retains it exactly but must not invent a call or scheduler mutation absent from stock.
