# gz_main_mod — RED (Reference Effort Delta), pinned donor UNMODIFIED

This report was produced **before** any source change was contemplated. It is
the mandatory baseline. It is preserved verbatim; later work must not rewrite
it.

## 1. What was built

The pinned donor source, byte-identical, with **no C modification of any
kind**. The only authored files are build plumbing:

* `Makefile` (object list copied from `Makefile.vendor`, `-I` list mirrored,
  config visibility from the stock-proven config contract)
* `BUILD.bazel`
* `stock-provider.symvers` + `.provenance.json` (the single `mtk_sec_heap`
  edge, declared, not injected)

Two supporting filegroup `BUILD.bazel` files were added for the external
vendor headers (`drivers/dma-buf/heaps`, `drivers/misc/mediatek/trusted_mem`).
Neither contains driver code.

Build target and dependency set are as recorded in
`kernel/phase4-gz-main-mod-lineage.md`. All GenieZone providers are REAL
source-built modules; no gz_tz_system / gz_ipc_mod / gz_trusty_mod / ffa_v10 /
tmem_ffa witness participates.

## 2. Build result

| item | value |
|---|---|
| BUILD_RC | 0 |
| compiler errors | 0 |
| compiler warnings | 0 |
| modpost warnings | 0 |
| unresolved symbols | 0 (76/76 imports resolved) |
| `KBUILD_MODPOST_WARN` | never set |

Two iterations of *build plumbing* were needed before the first successful
compile, neither touching driver source:

1. `memory_ssmr.h` includes `../private/tmem_device.h`; the
   `trusted_mem/private` header directory had to be present.
2. The corresponding bazel filegroup had to export it.

## 3. Stock vs RED parity

| metric | stock | RED | result |
|---|---|---|---|
| defined functions | 42 | 42 | shared 42, missing 0, extra 0 |
| size-identical functions | — | — | **42/42** |
| byte-identical functions | — | — | **42/42** |
| KCFI type ids | 42 | 42 | **42/42 exact** |
| imports (UND) | 76 | 76 | IDENTICAL |
| MODVERSION records | 77 | 77 | IDENTICAL (all CRCs equal) |
| exports | 0 | 0 | IDENTICAL (module is a leaf) |
| relocations | 2817 | 2817 | **IDENTICAL** |
| defined objects | 45 | 45 | 44 identical; 1 differs in size only (`__UNIQUE_ID_vermagic333`, 87 vs 85 bytes) |
| ELF sections | 45 | 45 | same names; 2 differ in size |
| `.rodata`/`.modinfo` strings | 286 | 286 | 285 identical, 1 differs (`vermagic`) |
| whole-file identity | 159400 B | 159392 B | not identical — 8 bytes, provenance only |

## 4. Every mismatch, explained

There are exactly two, and both are pure build provenance:

1. **`vermagic` git-describe suffix.**
   stock `6.1.115-android14-11-g945dff7bc1bf …`
   RED `6.1.115-android14-11-maybe-dirty …`
   The local exact-GKI checkout is not a git working tree, so `scripts/setlocalversion`
   cannot emit the upstream describe string. Two bytes of length difference in
   `.modinfo`, and the corresponding `__UNIQUE_ID_vermagic333` object size.
   Runtime effect: none beyond module-loader vermagic matching, which is a
   build-identity check, not driver behaviour.

2. **`.llvm_addrsig` encoding.**
   stock `0x58` bytes, RED `0x4e` bytes. The address-significance table is
   link-time metadata for ICF; it carries no runtime semantics and no code or
   data. The same 10-byte-class residual was accepted for `gz_trusty_mod`,
   `gz_ipc_mod` and `tmem_ffa`.

There is **no functional residual**: every instruction byte, every relocation,
every import CRC, every KCFI id and every behaviour-bearing string matches.

## 5. RED verdict

The pinned donor, unmodified, already reproduces stock. The required source
delta is **empty**.

Consequently the delta ledger
(`kernel/phase4-gz-main-mod-delta-ledger.tsv`) contains no functional row, and
the final module is classified `DIRECT_SOURCE_MATCH` rather than
`SOURCE_DELTA_RECONSTRUCTION_EXACT`.

The final build is byte-identical to this RED build
(`sha256 7b7cb36b03d7749e5f7b3d53c8b0207bfc7f7e6b4bf2819c501b42d42cb5df51`),
which is itself the proof that no source change was introduced afterwards.
