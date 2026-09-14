# GQ5012BF1 tkcore island Phase 3P pre-edit baseline

## Identity

- Research start commit: `91d523665091570887368d946465dce2d3c1d648`
- Exact GKI workspace: `/home/armol/kernel-work/gki-12901745-workspace`
- GKI: Linux 6.1.115-android14-11, Android CI `ab/12901745`
- Common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- Runtime access: prohibited; static/offline only

## Frozen binary baseline

| Object | SHA256 | Size |
|---|---|---:|
| Stock `tkcore.ko` | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | 221352 |
| Phase-2 rebuilt `tkcore.ko` | `5fc3c38dbfbd1eb90fec4b7d1ec803e4f09a7b576e8e8220f68f1b794a2e6e62` | 132528 |

The Phase-2 ELF, build log, `nm`, `readelf -a`, `objdump -dr`, source hashes and per-header hashes are frozen under `workspace/phase4-tkcore-island/phase3p/before/`.

## Source identity

| Input | SHA256 |
|---|---|
| `tkcore-island/tkcore/tee_core.c` | `fd7e813bb9972e0e541ad3fd02fc6e0df97d84f431853cfb60d95eb4fa59aa97` |
| `tkcore-island/tkcore/tee_kernel_api.c` | `008b73c7cb409bfc02e237c2f8dcf3104b3850f4ad650a5eea748bcc3ed5c937` |
| `trustkernel/include/trustkernel/tee_core.h` | `6d81b835eb60e58584a3214c030c63781399d637167fc2e968f7f82ce143fe57` |
| `trustkernel/include/trustkernel/layout-assert.h` | `7dbdbd39399fa792abc26c8415a312fa05dab742a86b6e31f7ff8791e3d66c43` |
| tkcore-island manifest (16 files) | `a8fdea42ab0874ac1aa546d37be52b65e992f277b5aca37c0f9323dfa175142b` |
| TrustKernel common-header manifest (8 files) | `f3c3a13d94c00e40a43ff60c25603ea08717dd8f29a3b6ce1d394744e59352d5` |

Manifest algorithm: SHA256 over sorted `relative-path NUL file-SHA256` records separated and terminated by newline.

## Hard baseline gates

- `//lieppos/tkcore-island:tkcore`: `BUILD_RC=0`, warnings 0, errors 0, unresolved 0.
- `//lieppos/trustkernel-layout:tk_layout_probe`: `BUILD_RC=0`; existing 31/31 anchors pass.
- `kernel/scripts/phase4_tkcore_island_phase2_verify.py`: **52/52 CHECKS PASSED**.
- `common/`: clean at the required commit.
- Research worktree contained unrelated untracked NFC/extcon/Qwen work; it was not touched.

Phase 3P may proceed.
