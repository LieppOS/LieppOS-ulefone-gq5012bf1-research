# GQ5012BF1 tkcore island Phase 3C — direct uaccess prerequisite blocker

> **STATUS: `RESOLVED_BY_AUTHORIZED_DIRECT_PREREQUISITE_EXPANSION`**
>
> The stop recorded below was correct and is preserved verbatim as the
> historical reason the Phase-3C scope was expanded. Scope expansion to
> `uaccess_ttbr0_enable` and `uaccess_ttbr0_disable` — and to nothing else —
> was subsequently authorized.
>
> Outcome: **candidate interpretation 1 was confirmed.** Implementing only the
> proven source-level `put_user` shape caused the exact-GKI toolchain to
> materialise both helpers on its own, LOCAL and **byte-identical to stock**
> (100 and 92 bytes, `cpu_hwcaps` relocations only). No helper body was
> hand-written and no symbol was fabricated. Resolution evidence:
> `phase4-tkcore-island-phase3c-closure.md`.
>
> Everything below this line is the original, unmodified blocker record.

---

## Result

**PHASE 3C STOPPED BEFORE IMPLEMENTATION.**

The phase boundary explicitly excludes `uaccess_ttbr0_enable` and `uaccess_ttbr0_disable` unless one is proven to be a mandatory direct dependency of the seven primary targets, and then requires a stop and dependency report before scope expansion. Stock proves exactly that dependency.

No island source file has been edited. Phase 3B remains the live implementation and reproduces SHA-256 `860ad5ee0c4da579627c202b19892b20e44ef34287054f11ab802b09e9933640`; prerequisite verifiers remain 203/203 and 162/162.

## Blocked primary function

| Field | Evidence |
|---|---|
| function | `convert_compat_tee_cmd` |
| stock offset / size | `0x0384`, 3644 bytes |
| stock binding | GLOBAL, not exported |
| stock KCFI | `0xbb8e9218` |
| Phase-3B state | ABSENT |
| dependency 1 | `uaccess_ttbr0_enable`, stock LOCAL at `0x11c0`, 100 bytes; Phase 3B ABSENT |
| dependency 2 | `uaccess_ttbr0_disable`, stock LOCAL at `0x1224`, 92 bytes; Phase 3B ABSENT |

## Exact instruction evidence

Within `convert_compat_tee_cmd`, after validating `operation + 0x6c` (the upper 32-bit half of the compat session-pointer slot):

```text
07b8: and  x19, x8, #0xff7fffffffffffff
07bc: bl   0x11c0 <uaccess_ttbr0_enable>
07c0: mov  w22, wzr
07c4: sttr w22, [x19]                 # zero operation+0x6c
07c8: bl   0x1224 <uaccess_ttbr0_disable>
07cc: cbnz w22, 0x1094                # -EFAULT path
```

These are linked intra-`.text` branches, so no unresolved relocation remains at `0x07bc`/`0x07c8`; the named symbol targets and exact addresses are resolved by the stock ELF. This is stronger than an inferred call graph.

The two target bodies match exact-GKI `arch/arm64/include/asm/uaccess.h`: they conditionally manipulate TTBR0/TTBR1 under `CONFIG_ARM64_SW_TTBR0_PAN`, preserve interrupt state, issue ISBs, and return immediately when `system_uses_ttbr0_pan()` is false. Their only data relocation is `cpu_hwcaps`; neither imports another function.

## Candidate interpretations

1. **Most likely — compiler materialisation of exact-GKI static-inline helpers.** Both names are `static inline bool` in the exact GKI header. Clang may inline most `put_user` expansions in this 3644-byte converter but emit callable local copies for this site under its size/inlining decisions. This explains why the same function contains many inlined TTBR0 enable/disable sequences and exactly one direct pair.
2. **Less likely — explicit source calls around a raw user store.** TrustKernel source could directly call the header helpers around a low-level `__put_user` store. The emitted sequence is compatible with that source shape too.
3. **Rejected — unrelated branch or disassembler mislabelling.** Exact symbol boundaries, named branch targets, matching GKI helper bodies and placement immediately around the user store rule this out.

## Why the distinction matters

- Explicitly defining replacements would risk duplicate/wrong helper bodies and falsely treat exact-GKI header code as TrustKernel-owned implementation.
- Merely writing a normal `put_user` may or may not cause the exact compiler to materialise the two stock-local symbols; that changes measured coverage by two functions (nominal 111/122 versus potentially 113/122).
- Omitting the direct calls from a semantically “equivalent” converter would fail the required stock call-graph closure and leave two mandatory direct targets absent.
- Expanding into uaccess without acknowledgement violates the Phase-3C boundary even though the helpers are small.

## Evidence exhausted

Checked, offline only:

- stock symbol table and full relocation-aware `.text` disassembly;
- Phase-3B symbol table (all three functions absent);
- exact-GKI `common/arch/arm64/include/asm/uaccess.h` definitions;
- Phase-3B missing-function inventory/work queue;
- all stock converter call sites and its complete instruction body;
- public indexed-code searches for the proprietary converter source (no authoritative TrustKernel source found).

No runtime operation, device access, ioctl, supplicant request, secure-world interaction, consumer rebuild, flash or reboot occurred.

## Exact evidence needed to proceed

One of:

1. explicit authorization to expand Phase 3C minimally to the two **direct prerequisite** uaccess helpers, with acceptance based on natural exact-GKI compiler emission from the converter (preferred); or
2. authoritative TrustKernel source/preprocessed source/LLVM IR proving whether the helpers were explicitly called; or
3. authorization for a compile-only source experiment that implements only the proven converter store shape and checks whether the exact Clang/GKI configuration naturally emits both local symbols, reverting if it does not.

No clock, SPI, platform or affinity target is implicated or requested.

## Stop classification

```text
TKCORE_ISLAND_PHASE3C_STATUS=BLOCKED_DIRECT_PREREQUISITE
BLOCKED_FUNCTION=convert_compat_tee_cmd
DIRECT_PREREQUISITES=uaccess_ttbr0_enable,uaccess_ttbr0_disable
SOURCE_EDITS=0
RUNTIME_VALIDATION=NONE
FINAL_THREE_CONSUMER_ACCEPTANCE=DEFERRED
TODO_18=OPEN
```
