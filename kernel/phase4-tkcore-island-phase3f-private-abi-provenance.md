# Phase 3F — historical private-type CRC provenance

This report is mandatory for every `ISLAND_NATURAL_PROVIDER_ABI` (category-B) edge. There are **14** of them: 7 in `tkcore_drv` and 7 in `tmem_ffa`.

The correct statement is **not** "the CRC mismatch doesn't matter". It is:

> The historical binary ABI provenance differs, but the complete source island uses a single, naturally generated ABI. Provider and consumers are compiled against one authoritative TrustKernel type graph, so genksyms derives mutually agreeing CRCs for all of them with no CRC injection, no witness record, and no ELF patching.

## Why the historical CRC cannot be reproduced

`genksyms` expands a pointed-to struct **in full** and hashes every member's *spelling*, *order* and *type*. A CRC over `struct tee *` therefore hashes all member names of TrustKernel's private 312-byte `struct tee` and, transitively, `struct tee_context`, `struct tee_ops`, `struct tee_session`, `struct tee_shm` and the `TEEC_*` graph.

Member **names do not exist in a stripped `.ko`**. Layout is recoverable — every offset in the island headers is proven by instruction evidence — but spellings are not. An exhaustive search over candidate spellings failed to reproduce the historical values, and the OP-TEE donor spellings are provably wrong (they yield `tee_core_add 0x05670103`, `tee_core_del 0x34a19f52`, `__tee_get 0xbe5d9101`, none of which match stock).

So the blocking factor is **irreversible information loss in the vendor's own shipped binary**, not a defect in the reconstruction.

## Per-edge provenance

### tkcore_drv — 7 category-B edges

| Symbol | Historical | Island | Sensitising private type |
|---|---|---|---|
| `tee_core_alloc` | `0x68aaf1dc` | `0x00940cd5` | `struct tee` + `struct tee_ops` (and transitively `tee_session`, `tee_cmd`, `tee_shm`) |
| `tee_core_add` | `0x74f0ee2b` | `0xe8b45b91` | `struct tee` |
| `tee_core_del` | `0xf53dbff2` | `0xd3dca6f9` | `struct tee` |
| `__tee_get` | `0xa4df7b8a` | `0xf95a76a4` | `struct tee` |
| `tee_supp_cmd` | `0x6f7dfbee` | `0x82545465` | `struct tee` |
| `tee_wait_queue_sleep` | `0xcca24950` | `0x305931a9` | visible `struct device` expansion differs by include context |
| `tee_wait_queue_wakeup` | `0xe2de5bad` | `0x258a3f0c` | visible `struct device` expansion differs by include context |

The last two deserve precision. `struct tee_wait_queue_private` itself is **exactly right** — `tee_wait_queue_init` and `tee_wait_queue_exit`, which take *only* that pointer, both reproduce their historical CRCs naturally (`0x03c4c343`, `0xe773ba45`). That proves TrustKernel kept the OP-TEE donor's member names `mu`/`db`. The `sleep`/`wakeup` pair additionally takes `struct device *`, and the hashed expansion of that GKI type depends on which headers are visible at the declaration site. The private TrustKernel portion of these two prototypes is therefore *provably exact*; only the ambient kernel-type expansion differs.

### tmem_ffa — 7 category-B edges

| Symbol | Historical | Island | Sensitising private type |
|---|---|---|---|
| `TEEC_InitializeContext` | `0x89b94f9a` | `0xf395354f` | `TEEC_Context` → `struct tee_context` |
| `TEEC_RegisterSharedMemory` | `0xa7bb0a46` | `0x6f70dc3e` | `TEEC_Context` → `struct tee_context` |
| `TEEC_OpenSession` | `0xe821e2a3` | `0x90aa6e1d` | `TEEC_Context`, `TEEC_Session` → `struct tee_context`, `struct tee_session` |
| `TEEC_InvokeCommand` | `0x202b681e` | `0xdd7b8804` | `TEEC_Session` → `struct tee_session` |
| `TEEC_CloseSession` | `0xcb193c37` | `0x811d3eaf` | `TEEC_Session` → `struct tee_session` |
| `TEEC_ReleaseSharedMemory` | `0xc4d15e1c` | `0xee29e3f5` | `TEEC_SharedMemory` identifier union spelling |
| `TEEC_FinalizeContext` | `0x7b3bc43f` | `0xd203900b` | `TEEC_Context` → `struct tee_context` |

The GlobalPlatform value types themselves are byte-for-byte and name-for-name the OP-TEE definitions; the blocking edge in each case is the TrustKernel-private kernel object reachable through the context/session identifier union.

## Why the semantic prototype is nonetheless proven

For every category-B edge the *shape* of the prototype is established independently of the spellings:

1. **Layout evidence** — each struct offset asserted in the island headers is pinned by an instruction or relocation in the stock image (e.g. `tee_core_alloc` does `devm_kmalloc(dev, priv_len + 0x138)` giving `sizeof(struct tee)`; `snprintf(tee + 0x20, 64, ...)` giving `name[64] @0x20`).
2. **Call-site evidence** — argument count, register classes and return handling are read directly from the frozen consumers' call sites.
3. **KCFI evidence** — the provider reproduces the stock KCFI type id for these functions, which is an independent hash of the *type shape* (not member names). Because it matches, the argument/return type shape is confirmed correct even where genksyms member spellings are lost.
4. **Codegen evidence** — the decisive proof. Rebuilding each consumer against the common authority produced **byte-identical code**: tkcore_drv 50/50 functions, tmem_ffa 141/141 functions, microarray 27/27 functions, with zero KCFI differences and exactly equal relocations. If any prototype's shape were wrong, the emitted calls would differ.

## Why provider and consumer agree naturally

`tkcore`, `tkcore_drv`, `tmem_ffa` and `microarray_fp_tee` are all compiled against `lieppos/trustkernel/include/trustkernel/`. genksyms runs once on the provider and writes the values into the provider's own `Module.symvers`; modpost then copies those values into each consumer's `__versions`. Measured agreement is exact: 7/7 for tkcore_drv, 7/7 for tmem_ffa, 1/1 for microarray.

Where a frozen consumer's source required a different member spelling to compile unchanged, the overlay supplies a **compiler-only** view guarded by `#ifdef __GENKSYMS__`, so the ABI hash always sees the authoritative member stream while the frozen code keeps compiling to identical bytes. This changes no layout: both views are the same size at the same offsets.

## Why no CRC manipulation was used

- No `__crc_` symbol was written, edited or injected.
- No `__versions` section was edited; it is produced by modpost from provider records only.
- No `__kcrctab` was edited.
- No fake or hand-written `Module.symvers` exists in any Phase-3F package; the historical `stock-provider.symvers` and `tkcore-provider.symvers` witness files were **removed**, not reused.
- No ELF patching or binary symbol rewriting.
- `KBUILD_MODPOST_WARN` is absent from every Phase-3F Makefile, so every build was fail-closed with 0 unresolved symbols.
