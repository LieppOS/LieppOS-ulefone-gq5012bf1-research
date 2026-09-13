# GenieZone transport all-consumer acceptance

## Method

All 471 committed stock `.ko` placements were scanned. For each `gz_trusty_mod` and `gz_ipc_mod` export, every consumer `__versions` requirement was compared first to the stock provider CRC and then to the natural CRC emitted by unchanged pinned source.

## Result

- provider/export/consumer edges checked: **40**
- provider-consumer pairs: **9**
- unique direct consumer modules: **7**
- natural CRC matches: **40/40**
- broken consumers: **0**

| Provider | Consumer | Edges | Natural acceptance |
|---|---|---:|---:|
| `gz_trusty_mod` | `gz_ipc_mod.ko` | 3 | 3/3 |
| `gz_trusty_mod` | `gz_irq_mod.ko` | 5 | 5/5 |
| `gz_trusty_mod` | `gz_log_mod.ko` | 6 | 6/6 |
| `gz_trusty_mod` | `gz_main_mod.ko` | 5 | 5/5 |
| `gz_trusty_mod` | `gz_tz_system.ko` | 2 | 2/2 |
| `gz_trusty_mod` | `gz_virtio_mod.ko` | 11 | 11/11 |
| `gz_trusty_mod` | `sapu.ko` | 2 | 2/2 |
| `gz_ipc_mod` | `gz_main_mod.ko` | 1 | 1/1 |
| `gz_ipc_mod` | `gz_tz_system.ko` | 5 | 5/5 |

All 14 Trusty exports are consumed somewhere in stock. Six of 15 IPC exports are consumed by stock modules; the nine unconsumed channel-level exports are still reproduced naturally and remain available to future/runtime clients.

Machine evidence: `phase4-gz-transport-consumer-acceptance.tsv`. Every row contains provider, export, consumer, consumer-required CRC, source-built CRC, and `NATURAL_OK` status.

**Consumer acceptance: PASS; zero regressions.**
