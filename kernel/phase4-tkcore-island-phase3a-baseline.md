# GQ5012BF1 tkcore island Phase 3A pre-edit baseline

## Identity

- Research repository starting commit: `eb6fc0bc9ae6239ae47590591e995d7bf7a2b8bd`
- Exact GKI workspace: `/home/armol/kernel-work/gki-12901745-workspace`
- GKI: Linux 6.1.115-android14-11, Android CI `ab/12901745`
- Common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- Build target: `//lieppos/tkcore-island:tkcore`
- Layout target: `//lieppos/trustkernel-layout:tk_layout_probe`

## Frozen binaries

| Object | SHA256 | Size |
|---|---|---:|
| Stock `tkcore.ko` | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | 221352 |
| Phase-2 rebuilt `tkcore.ko` | `5fc3c38dbfbd1eb90fec4b7d1ec803e4f09a7b576e8e8220f68f1b794a2e6e62` | 132528 |

The Phase-2 ELF, build log, disassembly, symbol inventory and readelf metadata are frozen under
`workspace/phase4-tkcore-island/phase3a/before/`.

## Source identity

| Input | SHA256 |
|---|---|
| `tkcore-island/tkcore/tee_core.c` | `fd7e813bb9972e0e541ad3fd02fc6e0df97d84f431853cfb60d95eb4fa59aa97` |
| `tkcore-island/tkcore/tee_kernel_api.c` | `008b73c7cb409bfc02e237c2f8dcf3104b3850f4ad650a5eea748bcc3ed5c937` |
| `trustkernel/include/trustkernel/tee_core.h` | `6d81b835eb60e58584a3214c030c63781399d637167fc2e968f7f82ce143fe57` |
| `trustkernel/include/trustkernel/layout-assert.h` | `7dbdbd39399fa792abc26c8415a312fa05dab742a86b6e31f7ff8791e3d66c43` |
| tkcore-island tree manifest hash | `013cf482d51eda8f285bb5f2d77939e6a52df3bb75dd725137ac5c2720f05f74` |
| common TrustKernel-header tree manifest hash | `6a545d451d5826b4a512695d1bab1244e815f7af1813637fb9dc148d2aa72161` |

The tree-manifest hashes are SHA256 over sorted `relative-path NUL file-SHA256` records.

## Baseline gates

- Phase-2 verifier: **52/52 CHECKS PASSED**.
- Phase-2 module build: `BUILD_RC=0`, compiler warnings 0, errors 0, unresolved symbols 0.
- Layout build: `BUILD_RC=0`, static assertion failures 0; existing **31/31** anchors preserved.
- Runtime validation: **not performed** (static/offline requirement).

An interrupted dual-target build produced ignored arm64 generated headers in the source tree. This was an infrastructure side effect, not a source delta; it was removed with `make ARCH=arm64 mrproper`, after which the two baseline targets passed sequentially.

## Nine direct targets at entry

| Function | Phase-2 state |
|---|---|
| `tee_core_alloc` | DONOR_PORTED / call-set different |
| `tee_core_add` | DONOR_PORTED / call-set different |
| `tee_core_del` | DONOR_PORTED / call-set different |
| `tee_core_free` | EXACT_BYTE |
| `__tee_get` | MISSING |
| `TEEC_InitializeContext` | DONOR_PORTED / missing opaque-handle call |
| `TEEC_FinalizeContext` | DONOR_PORTED / missing opaque-handle calls |
| `TEEC_OpenSession` | DONOR_PORTED / missing opaque-handle calls |
| `TEEC_CloseSession` | DONOR_PORTED / missing opaque-handle calls |
