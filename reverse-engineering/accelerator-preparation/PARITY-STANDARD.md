# Complete accelerator module parity standard

A=exact shipped ELF identified by stock path/hash; B=source-built target; B1/B2=two independent clean builds of the same pinned source/config/toolchain. Preparation does not create B operands.

1. **Function coverage:** enumerate every stock function, including local/init/exit/alias/zero-size cases; no stock-only translation unit silently omitted. Close each body by byte identity or specific, independently checkable semantic proof. Count/size/name overlap alone is insufficient.
2. **Function bytes/semantics:** retain raw and normalized results separately; normalization must not erase calls, constants, branch behavior, IRQ/error/teardown ordering or firmware transfers. Every allowed register allocation/scheduling difference gets a symbol-specific proof.
3. **Data:** all objects, tables, initialized bytes, alignment/padding, BSS shape, relocation-initialized pointers and global layout. Function tables do not establish data parity; selected data objects do not establish whole-section identity.
4. **Imports/exports:** symbol names, namespaces, GPL/export bucket, natural CRC generation and ordered tables. Check every affected existing consumer/provider edge. Stock-derived symvers can isolate a baseline but cannot certify recovered source types; no fake CRC/KCFI stamping.
5. **Modversions:** all __versions and __kcrctab CRCs, with proven common/vendor header layout and enum identity; unknown private types are a blocker, not a permission to overwrite constants.
6. **KCFI:** exact address-taken target type IDs, indirect-call checks and interface prototypes. Inspect instrumented function entries and all relevant absolute IDs/relocations. `kcfi()` in `reverse-engineering/scripts/ko-kcfi-typeid.py` is a prototype oracle, not a module acceptance test.
7. **Relocations:** section, offset, type, target symbol name and addend multiset. Raw symbol indices/order are a distinct provenance axis; account for differences without hiding behavioral relocations.
8. **Symbols/strings:** defined/undefined symbol sets, visibility, init/exit surfaces, literal strings and source residue. Out-of-tree paths may be documented provenance exceptions, not blanket removal of diagnostics/semantics.
9. **.modinfo/vermagic:** dependencies, softdeps, aliases, license, import namespaces, name, release and all meaningful keys. Exact GKI 12901745/KMI/config/compiler and release-stamping provenance must be reproducible; matching vermagic alone proves no ABI.
10. **Whole sections:** all allocatable code/data/metadata; explain build-id/debug/signing provenance separately. Never report a signing-key difference as source identity or disguise a behavior-bearing section mismatch.
11. **Determinism:** independent clean B1/B2 must agree byte-for-byte, with pinned inputs, flags, headers, object composition, linker, generated data and patch series. No copied object from the first build.
12. **DT/observable ABI:** register/IRQ/clock/power/memory/IOMMU/mailbox references, fops/ioctls native+compat, mmap/poll/fences, allocation→map→submit→complete/abort→free, timeouts, resets, recovery and teardown. For non-module integration, complete observable behavior replaces the module-byte gate.

Tools already exist: `ko-pair-parity.py A B`; `ko-func-diff.py --summary A B`; `ko-residue-diff.py A B`. Their successful execution is **not** an automatic all-axes PASS. Preserve machine-readable per-module acceptance/residual reports and explicit proof operands. Existing camera function/data TSVs remain valid for their measured axes but do not automatically close CRC/KCFI/relocation/determinism/DT gates.

**DONE** is the entire explicitly owned normal-world kernel set and observable interface—not one successful compile, a generic-source label, Android's codec declarations, GPU libraries, DT enablement or module loading. Proprietary firmware algorithms/userspace and later authorized runtime acceptance remain separate.
