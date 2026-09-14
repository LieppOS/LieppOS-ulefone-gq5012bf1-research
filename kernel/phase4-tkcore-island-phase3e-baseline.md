# GQ5012BF1 tkcore island Phase 3E — baseline

Frozen before every Phase-3E source edit.

- `START_RESEARCH_HEAD = d17a1dd201e9571248ec298af165f5bdc8491407`
- Research tree clean for tracked files; unrelated untracked work was left untouched.
- Exact-GKI `common`: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`

## Mandatory build gate

| Check | Result |
|---|---:|
| build RC | 0 |
| compiler warnings / errors | 0 / 0 |
| modpost warnings | 0 |
| unresolved symbols | 0 |
| module SHA-256 | `c34a16e78a385a995e626c922bbc02dc756217cca9ef403253dd37999f4031b5` (**exact Phase-3D reproduction**) |
| size | 196904 |
| Build ID | `65bcfb2d5e7fb386c8ecf0a0356295d382835787` |
| srcversion | `3E2810D195047DBD1697163` |
| depends | empty |
| layout probe | built |

## Mandatory verifier gate

| Verifier | Result |
|---|---:|
| **Phase 3D** | **158/158 PASS** |
| Phase 3C-R | 59/59 PASS |
| Phase 3C | 81/81 PASS |
| Phase 3B | 205/205 PASS |
| Phase 3A-R | 162/162 PASS |

`BASELINE_GATE=PASS`. There were zero `FAIL` lines. The §7 stop condition was not triggered.

## Starting measured state

| Metric | Phase 3D |
|---|---:|
| stock-function coverage | 117 / 122 |
| missing | 5 |
| byte-identical | 47 |
| exports | 25 / 25 |
| undefined imports | 97 |
| island-only functions | 0 |

Exact missing set:

- `big_core_affinity_get_candidate_cpu`
- `big_core_affinity_match_cpu`
- `big_core_affinity_need_bind_cpu`
- `plat_cpu_is_big`
- `plat_tee_init`

## Frozen evidence

`workspace/phase4-tkcore-island/phase3e/before/` contains the Phase-3D module and SHA, `nm`, complete `readelf`, relocation-aware `llvm-objdump -dr`, `modinfo`, section sizes, source/header hashes, layout probe and SHA, all five verifier logs, build log, and starting research HEAD.
