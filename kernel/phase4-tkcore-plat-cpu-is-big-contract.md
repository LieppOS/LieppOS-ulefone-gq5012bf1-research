# `plat_cpu_is_big` contract

| Property | Proven value |
|---|---|
| stock offset / size | `0x95e8` / 68 bytes |
| binding / export | GLOBAL / not exported |
| prototype | `bool plat_cpu_is_big(int cpu)` |
| KCFI | `0xbd7efeae` = `_ZTSFbiE` |
| rebuilt size/KCFI | 68 / `0xbd7efeae` |
| classification | **EXACT_BYTE** |

## Semantics

1. Read static `large_cluster_id` (initial `-1`).
2. If it is `-1`, return false without dereferencing topology.
3. Otherwise access `cpu_topology[cpu]`; exact-GKI array bounds instrumentation traps with `brk #0x5512` for unsigned `cpu >= 32` (negative `int` included).
4. Return whether `cpu_topology[cpu].cluster_id == large_cluster_id`.

CPU numbering is the kernel logical CPU index. The topology input is arm64 `struct cpu_topology.cluster_id`; there is no capacity, MPIDR, DT, scheduler, online-mask, possible-mask, present-mask, fallback, or logging in this function.

An offline logical CPU is treated solely by its topology entry. The caller must supply a valid index after initialization. Raw rebuilt function bytes are identical to stock.
