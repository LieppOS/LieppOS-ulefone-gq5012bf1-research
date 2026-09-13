# `gz_tz_system.ko` — mandatory RED (unmodified donor)

RED was performed **before** any source change, as required, and is recorded
here unedited. Two RED passes exist because the unmodified donor does not
compile in the stock configuration.

Artifacts: `workspace/phase4-gz-tz-system/red/`

---

## RED-A — pinned donor, unmodified, stock config (`CONFIG_TEE=y`)

Only build plumbing was authored (BUILD.bazel / Makefile wrapper / include
paths / config visibility). No C source was touched.

**Result: BUILD FAILED — 9 errors, 0 objects produced.**

```
tz_system.c:798:61: error: declaration of 'struct teec_context' will not be
                    visible outside of this function [-Werror,-Wvisibility]
__weak u32 teec_initialize_context(const char *name, struct teec_context *context)
tz_system.c:805:42: error: ... 'struct teec_context'   (teec_finalize_context)
tz_system.c:810:37: error: ... 'struct teec_context'   (teec_open_session)
tz_system.c:811:16: error: ... 'struct teec_session'
tz_system.c:812:22: error: ... 'struct teec_uuid'
tz_system.c:814:16: error: ... 'struct teec_operation'
tz_system.c:826:39: error: ... 'struct teec_session'   (teec_close_session)
tz_system.c:831:39: error: ... 'struct teec_session'   (teec_invoke_command)
tz_system.c:833:18: error: ... 'struct teec_operation'
9 errors generated.
```

This is a property of the donor, not of the build harness: `struct teec_*`
(lowercase) is declared in no header anywhere in the pinned tree. The
`CONFIG_TEE` path at revision `957dac18` is dead code that cannot be compiled.

RED-A therefore yields no binary to compare. It is nonetheless the decisive
measurement of this task: it proves the stock module **cannot** have been
built from the pinned `tz_system.c` text, and it localises the entire
discrepancy to one 45-line block.

---

## RED-B — pinned donor, unmodified C, `CONFIG_TEE` visibility off

To obtain a real RED baseline, the donor C was still left **completely
unmodified** and only the config predicate was cleared — the one lever the
protocol allows as build plumbing. Everything the stock config proves
(`CONFIG_PM_SLEEP=y`, `CONFIG_GZ_VPU_WITH_M4U` off, `CONFIG_MTK_ENG_BUILD`
off, `debugFg 0`) was left at its stock setting.

**Result: BUILD_RC=0, module produced.**
`workspace/phase4-gz-tz-system/red/gz_tz_system.red-b.ko`

### Function-level comparison

| axis | value |
|---|---|
| stock functions | 61 |
| donor functions | 56 |
| shared | 56 |
| extra (donor only) | **0** |
| missing (stock only) | **5** — `TEEC_InitializeContext`, `TEEC_FinalizeContext`, `TEEC_OpenSession`, `TEEC_CloseSession`, `TEEC_InvokeCommand` |
| size-identical | 54/56 |
| **byte-identical** | **54/56** |
| kCFI identical | 55/56 |

The two byte-differing functions are exactly the two that contain
`#if IS_ENABLED(CONFIG_TEE)` case arms:

| function | stock size | donor size | kCFI |
|---|---:|---:|---|
| `_GzServiceCall_body` | 1932 | 2024 | `0x3747dee1` = `0x3747dee1` (identical) |
| `_Gz_KreeServiceCall_body` | 332 | 152 | `0xc843babe` = `0xc843babe` (identical) |

Both keep their stock kCFI type id, i.e. the *prototypes* were already correct
in the donor; only the switch-case bodies behind `CONFIG_TEE` are absent.

The single kCFI "difference" (`ree_service_threads`, stock `0x17fffff1`
vs donor `0xd65f03c0`) is not a type-id change at all: neither value is a kCFI
type id, both are the encoding of the preceding function's trailing
instruction (`b …` and `ret` respectively). `ree_service_threads` is never
address-taken, so it carries no kCFI prologue in either build. Recorded here
for completeness; it resolved to an exact match in the final build.

### ABI-level comparison

| axis | stock | donor | result |
|---|---:|---:|---|
| imports (UND) | 50 | 50 | **IDENTICAL set** |
| MODVERSION records | 51 | 51 | **IDENTICAL, every CRC** |
| exports | 27 | 27 | **IDENTICAL names and classes** |
| **export CRCs regenerated naturally** | — | — | **27/27** |
| relocations | 1082 | — | (compared at final parity) |

**The entire 27-symbol export ABI already reproduced naturally from the
unmodified pinned source, with no witness and no injection.** That is the
single most important RED finding: the provider ABI was never in doubt, and
the `CONFIG_TEE` question could not affect it (the weak stubs are not
exported).

### String comparison

| axis | stock | donor |
|---|---:|---:|
| strings | 100 | 97 |

Donor-only strings: none. Stock-only strings: exactly three, all from the
`CONFIG_TEE` case arms:

```
[KREE][ERR][ERROR] TEEC_InitializeContext failed: %x\n
[KREE][ERR][ERROR] TEEC_OpenSession failed: %x\n
[KREE][ERR][ERROR] TEEC_InvokeCommand failed: %x\n
```

These strings are themselves independent proof that the stock build had
`CONFIG_TEE` **on** and reached those call sites.

### Module metadata

`license`, `name`, `depends`, both `alias` entries: identical to stock in
RED-B already.

---

## RED conclusion

Every stock/donor discrepancy — 5 missing functions, 2 differing function
bodies, 3 missing strings — traces to one cause: the `CONFIG_TEE` block in
`tz_system.c`. Nothing else in the module differs in any measured axis.

Delta recovery is therefore bounded to that block and is documented, with its
evidence, in `kernel/phase4-gz-tz-system-delta-ledger.tsv`.
