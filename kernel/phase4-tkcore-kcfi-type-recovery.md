# GQ5012BF1 — recovering stock type names from KCFI type ids

## Result

A stock struct tag that the project previously had to treat as unrecoverable was **recovered exactly** from the stock ELF:

```text
convert_compat_tee_spta_inst(struct tee_spta_inst_desc __user *)
```

This is the first island type name recovered from binary evidence rather than chosen as a `SYNTHETIC_ISLAND_NAME`.

## Why this was thought impossible

Member and tag spellings are not recoverable from a stripped `.ko` through genksyms: CRC search over millions of candidate spellings previously failed (`kernel/phase4-tkcore-historical-vs-island-crc.md`). That conclusion is still correct **for genksyms CRCs**, because those hash the full member list.

KCFI type ids are a different and much weaker function: they depend only on the **function signature**, not on member names. That makes them invertible when the signature shape is already proven.

## The mechanism

Clang with `-fsanitize=kcfi` emits, in the word immediately preceding a function entry point:

```text
kcfi_type_id = low 32 bits of xxHash64("_ZTSF" + <Itanium-mangled function type> + "E")
```

The hash function is named in the emitted IR module flags:

```text
!{i32 4, !"kcfi", i32 1}
!{i32 4, !"kcfi-hash", !"xxHash64"}
```

Verified against three independently compiler-produced values before use:

| Signature | Mangled string | Computed | Compiler |
|---|---|---:|---:|
| `int f(struct tee_cmd_io *)` | `_ZTSFiP10tee_cmd_ioE` | `bb8e9218` | `bb8e9218` |
| `int f(struct tee_shm_io *)` | `_ZTSFiP10tee_shm_ioE` | `daee5623` | `daee5623` |
| `int f(struct tee_spta_inst *)` | `_ZTSFiP13tee_spta_instE` | `014a7540` | `014a7540` |

The xxHash64 implementation used was itself first validated against the published reference vectors (`""`, `"a"`, `"abc"`).

## Constraining the signature before searching

The search space is only tractable because the stock call site pins the signature. From `tee_compat_ioctl`:

```text
1698: mov  x0, x21
169c: bl   <convert_compat_tee_spta_inst>
16a0: cbnz w0, 0x1690          # 0x1690: mov x0, #-0xe  (-EFAULT)
```

Exactly one register (`x0`) is set, so there is exactly one pointer argument; the result is tested as a 32-bit value, so the return type is `int`. The unknown is therefore reduced to a single struct tag, and the mangled string is fully determined by it:

```text
_ZTSFiP<len><tag>E
```

## The search

Vocabulary of 66 domain tokens, joined with `_` to depth 4, each also tried with a leading `_`, a leading `__`, and a `_t` suffix. 77,066,616 candidates evaluated. Exactly one hit:

```text
tee_spta_inst_desc  ->  ba9dd2d9   (stock: ba9dd2d9)
```

Confirmed afterwards by the real compiler, not only by the reimplemented hash.

## Why this is a recovery and not a coincidence

- **Collision probability.** 77.07M candidates against a 32-bit space gives an expected false-positive count of 77.07e6 / 2^32 ≈ **0.018**. A spurious hit would be a ~1.8% event.
- **Uniqueness.** The search returned exactly one candidate out of 77M, not a family.
- **Semantic fit.** "SPTA instance descriptor" is the natural reading of a record that the compat layer pre-converts.
- **Structural fit.** With the tag applied, `convert_compat_tee_spta_inst` compiles to **exactly stock's 516 bytes and exactly stock's 129 instructions**, which the previous spelling did not achieve by construction.

It remains an inference, but it is a constrained, reproducible, single-solution inference, and it is labelled as recovered-by-hash-inversion rather than proven-by-relocation.

## Reusability

This technique generalises to any KCFI-bearing tkcore function whose signature shape is pinned by a call site. It cannot recover:

- member names (KCFI ids do not depend on them);
- tags used only in non-address-taken code (no type word is emitted);
- tags of functions whose signature shape is itself unknown.

It therefore does **not** overturn the genksyms CRC conclusion; it supplements it for a narrow, well-defined class of names.

## Reproduction

`workspace/phase4-tkcore-island/phase3c/kcfi-recovery/` holds the validated hash implementation, the candidate generator, the verification transcript, and the compiler cross-check.
