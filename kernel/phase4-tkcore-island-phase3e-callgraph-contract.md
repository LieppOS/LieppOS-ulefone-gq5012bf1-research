# GQ5012BF1 tkcore Phase 3E — callgraph contract

Derived from the stock oracle before writing Phase-3E C.

## Executable edges

| Caller | Callsite | Callee | Arguments | Return use | Condition / loop | Lock/IRQ context |
|---|---:|---|---|---|---|---|
| `init_module` | `.init.text+0x30` | `plat_tee_init()` | none | discarded; module init returns literal 0 | after `spin_lock_init(&tee_idr_lock)` and `idr_init(&tee_idr)` | process/module-init context; no local lock or IRQ change |
| `plat_tee_init` | `0x9818` | `_find_next_bit` | possible mask, `nr_cpu_ids`, current start | next CPU | possible-CPU max-cluster loop | no lock/IRQ change |
| `plat_tee_init` | `0x9860` | `_printk` | exact info string, max cluster id | discarded | after loop/global store | no lock/IRQ change |
| `big_core_affinity_match_cpu` | `0x2c28` | `plat_cpu_is_big(cpu)` | its second argument (`w1`) | returned as boolean after `&1` | unconditional | no lock/IRQ change |
| `big_core_affinity_get_candidate_cpu` | `0x2c7c` | `_find_next_bit` | possible mask, `nr_cpu_ids`, start | candidate CPU | only while static cache is negative | no lock/IRQ change |
| `big_core_affinity_get_candidate_cpu` | `0x2c94` | `plat_cpu_is_big(cpu)` | enumerated possible CPU | true stops loop/caches CPU | once per enumerated possible CPU | no lock/IRQ change |
| `big_core_affinity_get_candidate_cpu` | `0x2cb4` | `_printk` | candidate log and CPU | discarded | first match only | no lock/IRQ change |

`plat_cpu_is_big` and `big_core_affinity_need_bind_cpu` have no callees.

## Registration-only, non-executable edges

`big_core_affinity_operations` stores callback addresses in this exact order:

1. `big_core_affinity_need_bind_cpu`
2. `big_core_affinity_match_cpu`
3. `big_core_affinity_get_candidate_cpu`

`big_core_affinity` points to that ops object, and only `tee_device_configs[2]` (`tkcore_fp`) points to `big_core_affinity`.

These are address-taking data-relocation edges, not calls. They explain why all three LOCAL functions carry KCFI words and survive linking.

## Existing Phase-3D callers

Only `init_module` is an existing Phase-3D function that stock proves must call a Phase-3E target (`plat_tee_init`). The island Phase-3D `init_module` is a placeholder log and must be repaired to the stock ordering.

No existing function calls any `big_core_affinity_*` function. No indirect callsite of KCFI types `0x98d3ad02`, `0x7850c00b`, or `0x89fb613d` exists in stock.

## Proven hierarchy

```text
init_module
  └─ plat_tee_init
       ├─ for_each_possible_cpu / _find_next_bit
       └─ _printk

big_core_affinity_operations       [dormant callback registration]
  ├─ need_bind_cpu                 -> true
  ├─ match_cpu                     -> plat_cpu_is_big(cpu)
  └─ get_candidate_cpu
       ├─ for_each_possible_cpu / _find_next_bit
       ├─ plat_cpu_is_big(cpu)
       └─ _printk (first match)

plat_cpu_is_big
  └─ cpu_topology[cpu].cluster_id == large_cluster_id
```

There is no edge from `plat_tee_init` to an affinity callback, no clock/SPI edge, and no actual affinity-changing edge.
