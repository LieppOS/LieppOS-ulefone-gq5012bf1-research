# GQ5012BF1 tkcore island Phase 3B — baseline

Frozen before any Phase-3B source edit.

## Repository state

- Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`
- Research HEAD at start: `26977fef2da90df49f7aaca97d795c5f995f6e91` (branch `master`)
- Exact-GKI common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- `common` tracked-source modifications at start: **0**

Later unrelated commits were preserved; nothing was reset.

## Baseline gate (all required to pass before editing)

| Gate | Result |
|---|---:|
| `//lieppos/tkcore-island:tkcore` | `BUILD_RC=0` |
| compiler warnings | 0 |
| compiler errors | 0 |
| modpost warnings | 0 |
| unresolved symbols | 0 |
| static-assert failures | 0 |
| `//lieppos/trustkernel-layout:tk_layout_probe` | PASS (51 anchors) |
| Phase-3A-R verifier | **158/158 PASS** |
| `depends` | empty |

## Frozen Phase-3A-R artefacts

`workspace/phase4-tkcore-island/phase3b/before/`

- `tkcore.phase3a-r.ko` — SHA-256 `9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b`, 164032 bytes
- `tkcore.phase3a-r.ko.sha256`, `.nm.txt`, `.readelf.txt`, `.objdump.txt`, `.modinfo.txt`
- `section-sizes.tsv` — `.text 0x761c`, `.data 0x298`, `.bss 0x88`, `.rodata 0x5f8`
- `source-hashes.tsv` — SHA-256 of all 28 island/TrustKernel source files
- `build.log`

## Starting metrics

| Metric | Value |
|---|---:|
| stock functions | 122 |
| stock-function coverage | 91 |
| stock functions missing | 31 |
| byte-identical to stock | 33 |
| exports | 19 / 25 |
| undefined imports | 94 |
| defined objects | 50 |
| relocations | 2288 |
| island-only functions | 12 |

## Closed work carried in, not reopened

Core/provider lifecycle, the three IDR handle helpers, the four TEEC context/session APIs, proc/log, sysfs, peripheral clock registration/teardown, and `tee_supp_init`/`deinit`/`open`/`release` were all closed before Phase 3B and were not modified by it, with one narrow exception recorded in the regression report: two diagnostics in `tee_context_alloc_shm_tmp` (a shared-memory helper) were converted from `dev_err` to `pr_err` so its call multiset matches stock.
