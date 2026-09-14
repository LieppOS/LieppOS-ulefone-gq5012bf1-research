# GQ5012BF1 tkcore island Phase 3D — baseline

Frozen before every Phase-3D source edit.

- `START_RESEARCH_HEAD = fcfabcfe9dd417f7f5b635a9c2d7615dff01176e`
- Research tree clean (0 dirty tracked files); 10 unrelated untracked paths left untouched.
- Exact-GKI `common`: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`

## Mandatory build gate

| Check | Result |
|---|---:|
| build RC | 0 |
| compiler warnings / errors | 0 / 0 |
| modpost warnings | 0 |
| unresolved symbols | 0 |
| module SHA-256 | `7d9d7979521853c8d5a4412bb08c534870cd977a2f1efebe363f172ef067aeee` (**exact Phase-3C-R reproduction**) |
| size | 190784 |
| depends | empty |
| layout probe | built |

## Mandatory verifier gate

| Verifier | Result |
|---|---:|
| **Phase 3C-R** | **63/63 PASS** |
| Phase 3C | 85/85 PASS |
| Phase 3B | 203/203 PASS |
| Phase 3A-R | 162/162 PASS |

`BASELINE_GATE=PASS`. The Phase-3C-R verifier exists, runs against the live
Phase-3C-R binary, and passes; the §5 stop condition was not triggered.

## Starting measured state

| Metric | Phase 3C-R |
|---|---:|
| stock-function coverage | 113 / 122 |
| missing | 9 |
| byte-identical | 47 |
| exports | 21 / 25 |
| undefined imports | 97 |
| island-only functions | 0 |

## Frozen evidence

`workspace/phase4-tkcore-island/phase3d/before/` holds the Phase-3C-R
`tkcore.ko` and its SHA, `nm`, full `readelf`, relocation-aware `objdump -dr`,
`modinfo`, section table, 18 island source hashes, 8 TrustKernel header hashes,
the layout probe and its SHA, all four verifier logs, the build log, and the
starting research HEAD.
