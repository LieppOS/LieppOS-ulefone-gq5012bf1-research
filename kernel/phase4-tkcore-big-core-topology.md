# GQ5012BF1 tkcore — proven big-core topology policy

Static stock-ELF and exact-GKI analysis only; no CPU affinity or topology was changed.

## Exact criterion

Stock defines a big CPU as:

```c
cpu_topology[cpu].cluster_id == large_cluster_id
```

where `plat_tee_init()` computes `large_cluster_id` as the signed maximum `cluster_id` among CPUs in `__cpu_possible_mask`.

## Exact-GKI grounding

Exact kernel: Linux 6.1.115-android14-11, common `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, `CONFIG_NR_CPUS=32`.

`common/include/linux/arch_topology.h` defines:

- `struct cpu_topology.thread_id` +0
- `core_id` +4
- **`cluster_id` +8**
- `package_id` +12
- four `cpumask_t` fields and one Android vendor-data slot
- total size **56 bytes** under the exact config

Stock uses stride `0x38` and loads member `+0x08`; its `cpu >= 32` UBSAN trap exactly corroborates `cpu_topology[NR_CPUS]`.

## Inputs stock does and does not use

| Candidate basis | Stock result | Evidence |
|---|---|---|
| cluster number | **YES** | `cpu_topology[cpu].cluster_id`, max/equality |
| possible CPU mask | **YES** | relocations to `__cpu_possible_mask`, `nr_cpu_ids`, `_find_next_bit` |
| online/present masks | NO | no relocation/access |
| CPU capacity / scheduler capacity | NO | no helper, object, or arithmetic |
| CPU ID as ranking | NO | used only as array index/enumeration order |
| MPIDR / architecture register | NO | no system-register access |
| hard-coded big CPU numbers | NO | only constant 32 is exact array bound |
| device tree | NO | no OF call/import/string |
| scheduler/current task | NO | no access/call |

The policy does **not** imply “CPU 6/7” or “highest numbered CPU.” The first candidate is the lowest-numbered *possible* CPU whose cluster id equals the maximum cluster id. The actual MT6878 CPU numbering is deliberately not guessed.

## Offline and invalid CPUs

Initialization and candidate selection use the possible mask, not the online mask; an offline-but-possible CPU is not filtered. `plat_cpu_is_big()` itself performs no mask test. When initialized, any `cpu` outside unsigned range `[0,31]` (including a negative `int`) takes the compiler's bounds trap. While `large_cluster_id == -1`, the function returns false before indexing, so even an invalid input does not trap in that uninitialized state.
