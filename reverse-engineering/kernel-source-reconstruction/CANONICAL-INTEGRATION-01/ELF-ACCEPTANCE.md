# Whole-ELF acceptance

Re-verification in the combined environment (`evidence/reverify/`): each family's unchanged strict
verifier, at the verified recipe commit, against `stock-vendor-flat` (398 vendor identities copied
from the integration worktree operands that passed the inventory checker; every file hash-checked
against its audit row, read-only, no same-name collisions).

| Family | Recipe | B1 | B2 | Mutation controls per build |
|---|---|---:|---:|---:|
| CMDQ (joint) | 0b4b07f3 | 35/35 | 35/35 | 40 (absent export/KCFI axes recorded) |
| Thermal (joint) | ff6e97b3 | 34/34 | 34/34 | 11 |
| Connectivity | 40bf4296 | 17/17 | 17/17 | 44 |
| DRM / shared infrastructure | 4697eac3 | 12/12 | 12/12 | 34 |

Total 196 strict acceptances and 258 actual-ELF mutation cases; only the structural 20-byte GNU
build ID differs. CMDQ export/import CRCs are naturally generated (Microtrust disabled by the board TEE
configuration, ALL-C cmdq recipe 059e2fe4); no CRC constant or Module.symvers substitution. All other A rows
keep their original package acceptance evidence (COMPLETED-BATCHES-INTEGRATION-01: 114 A ELF
acceptances, 12 C rejections; NEXT-DG-BATCH-01: 550 ELF mutation controls).
