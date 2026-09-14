# GQ5012BF1 tkcore island Phase 3C-R — baseline

Frozen before every Phase-3C-R source edit.

## Identity

- Mission: close the one known semantic residual, `_update_client_tee_cmd`. Static/offline only.
- `START_RESEARCH_HEAD = f1fb99f05e2326b88d9ac87dda2ce524bffde843`
- Exact-GKI `common`: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- Research tree clean (0 dirty tracked files); 10 unrelated untracked research paths observed and left untouched.

## Mandatory build gate

Built from the live island before edits:

```text
//lieppos/tkcore-island:tkcore
//lieppos/trustkernel-layout:tk_layout_probe
```

| Check | Result |
|---|---:|
| build RC | 0 |
| compiler warnings | 0 |
| compiler errors | 0 |
| static-assert failures | 0 |
| module SHA-256 | `e7a8e2a725d7cd3dde2f674fdf9806edcc3766740fd9aa22df1e610b2c1a98fd` (**exact Phase-3C reproduction**) |
| module size | 190504 |
| layout probe | built |

## Mandatory verifier gate

| Verifier | Result |
|---|---:|
| Phase 3C ioctl/compat | **85/85 PASS** |
| Phase 3B shared memory | **203/203 PASS** |
| Phase 3A-R core/context/session | **162/162 PASS** |

`BASELINE_GATE=PASS`. No repair was needed or performed.

## Frozen evidence

`workspace/phase4-tkcore-island/phase3c-r/before/` contains the exact Phase-3C `tkcore.ko` and its SHA, `nm`, full `readelf`, relocation-aware `objdump -dr`, `modinfo`, section sizes, the layout-probe ELF and SHA, all 18 island source hashes, all 8 TrustKernel header hashes, the three verifier logs, the build log, and the starting research HEAD.

Per-function stock / before / after dumps for the target live in `workspace/phase4-tkcore-island/phase3c-r/oracle/`.

## Starting measured state

| Metric | Phase 3C |
|---|---:|
| stock-function coverage | 113 / 122 |
| missing stock functions | 9 |
| byte-identical functions | 47 |
| exports | 21 / 25 |
| undefined imports | 97 |
| island-only functions | 0 |

## Boundary frozen at baseline

Phase 3C-R may correct only `_update_client_tee_cmd`, plus a direct mandatory dependency if one is proven. It must not implement `tee_clkmgr_handle`, the three secure-SPI functions, the three big-core-affinity functions, `plat_cpu_is_big`, or `plat_tee_init`. It must not perform final consumer acceptance. `workspace/phase4-tkcore-island/acceptance/` remains empty and todo **#18 remains OPEN**.
