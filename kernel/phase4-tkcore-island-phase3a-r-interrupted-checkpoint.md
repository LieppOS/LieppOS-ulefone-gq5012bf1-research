# GQ5012BF1 tkcore island Phase 3A-R — interrupted checkpoint

Date: 2026-04-02

## Interruption classification

The preceding Phase-3A-R run stopped because of **external model-provider rate limiting**. It did not stop on a source, compiler, linker, ABI, oracle, or verifier blocker. No accepted Phase-3A-R source was reverted or discarded.

## Repository state before continuation

- Research repository: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`
- Research HEAD: `91570c37bd22ff0be1935fec37b2de0a0fb3d337`
- Branch: `master`
- The six already-produced Phase-3A-R reports were untracked at the checkpoint and were preserved.
- The research worktree also contained unrelated pre-existing untracked work. It was not modified, staged, removed, or included in this phase.
- Exact-GKI common tree: `/home/armol/kernel-work/gki-12901745-workspace/common`
- Common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- `common` was clean after the checkpoint build (`git status --short` and `git diff --stat` empty).
- The `lieppos/` island is a workspace-local source overlay rather than a Git worktree. Its accepted changes are therefore frozen by path, SHA-256, rebuilt ELF, and complete ELF metadata rather than by a misleading Git diff.

Raw state captures:

- `workspace/phase4-tkcore-island/phase3a-r/interrupted-checkpoint/research-git-status.txt`
- `workspace/phase4-tkcore-island/phase3a-r/interrupted-checkpoint/gki-common-git-status-and-diff.txt`

## Accepted modified-source hashes

These are the four source files changed by the interrupted Phase-3A-R run:

| SHA-256 | Size | Workspace path |
|---|---:|---|
| `4ce4546b01562bf6589a1f0d4ad2d150f16c7e981bc8b09269d7c375e51c2b17` | 12330 | `lieppos/trustkernel/include/trustkernel/tee_core.h` |
| `4c11747c56f8687235e6f05d0ad7ee4124c0624c7d1de7ad4f2b23f57b7799a1` | 17521 | `lieppos/tkcore-island/tkcore/tee_core.c` |
| `21784134e1794c99e66d1b1879fe1579b37cb41e1946ac5b418cb6c3de403f5b` | 2187 | `lieppos/tkcore-island/tkcore/tee_core_priv.h` |
| `c605687194e8e1123bf6451b5d2e647a77fa376bde5d410acdf8297b0d9147a1` | 8468 | `lieppos/tkcore-island/tkcore/tee_kernel_api.c` |

Machine-readable copy: `workspace/phase4-tkcore-island/phase3a-r/interrupted-checkpoint/source-hashes.tsv`.

## Checkpoint rebuild

A clean exact-GKI build was run after `make ARCH=arm64 mrproper`:

```text
//lieppos/tkcore-island:tkcore
//lieppos/trustkernel-layout:tk_layout_probe
```

Results:

| Gate | Result |
|---|---:|
| build return code | `0` |
| compiler warnings | `0` |
| compiler errors | `0` |
| modpost warnings | `0` |
| unresolved-symbol diagnostics | `0` |
| static-assert failures | `0` |
| layout probe | **PASS** |

Build log: `workspace/phase4-tkcore-island/phase3a-r/interrupted-checkpoint/build.log`.

## Frozen rebuilt ELF

- File: `workspace/phase4-tkcore-island/phase3a-r/interrupted-checkpoint/tkcore.interrupted-checkpoint.ko`
- SHA-256: `9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b`
- Size: `164032` bytes
- Build ID: `4cf34b11fcc60e92c5a09b926f9f2d3b7c88a41e`
- `vermagic`: `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64`
- `srcversion`: `CD46AAA7D1DA68FC83CABEB`
- `depends`: empty
- `.text`: `0x761c`
- `.data`: `0x298`
- `.bss`: `0x88`
- `.rodata`: `0x5f8`

The SHA exactly reproduces the already-accepted Phase-3A-R build, proving that the interruption did not alter the source checkpoint.

Frozen metadata:

- `tkcore.interrupted-checkpoint.ko.sha256`
- `tkcore.nm.txt`
- `tkcore.readelf.txt`
- `tkcore.objdump.txt`
- `tkcore.modinfo.txt`

The layout-probe ELF is also frozen as `tk_layout_probe.interrupted-checkpoint.ko` with SHA-256 `38744923b9ab62b7d37965fb3c68b28170debf41f4dc2fdcc779f520795ed7f0`.

## Preserved closure state

The checkpoint preserves the already-proven closure of:

- five core APIs: `tee_core_alloc`, `tee_core_add`, `tee_core_del`, `tee_core_free`, `__tee_get`;
- three byte-identical IDR helpers: `tee_core_alloc_uuid`, `tee_core_uuid2ptr`, `tee_core_free_uuid`;
- four context/session APIs already classified in the scope ledger: `TEEC_InitializeContext`, `TEEC_FinalizeContext`, `TEEC_OpenSession`, `TEEC_CloseSession`.

Core and IDR work is frozen and must not be reopened absent a concrete regression.
