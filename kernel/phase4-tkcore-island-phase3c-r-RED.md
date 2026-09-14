# GQ5012BF1 tkcore island Phase 3C-R — immutable RED

Recorded before any source edit. Not to be rewritten.

## Baseline

```text
START_RESEARCH_HEAD = f1fb99f05e2326b88d9ac87dda2ce524bffde843
Phase-3C module SHA = e7a8e2a725d7cd3dde2f674fdf9806edcc3766740fd9aa22df1e610b2c1a98fd
size                = 190504
build               = RC 0, 0 warnings, 0 errors, 0 static-assert failures
verifiers           = 3C 85/85, 3B 203/203, 3A-R 162/162
```

## Target

| Property | Stock | Island (Phase 3C) |
|---|---|---|
| symbol | `_update_client_tee_cmd` | `_update_client_tee_cmd` |
| offset | `0x3d64` | `0x3454` |
| size | 1652 | 1608 |
| linkage | LOCAL | LOCAL |
| KCFI | none emitted (direct-call-only) | none emitted (direct-call-only) |
| address-taken | no | no |

## Call sets

```text
stock  : __stack_chk_fail, _printk, memset, tee_context_copy_from_client
island : _dev_err

STOCK-ONLY  : __stack_chk_fail, _printk, memset, tee_context_copy_from_client
ISLAND-ONLY : _dev_err
shared      : 0
```

**The decisive RED fact: stock calls `tee_context_copy_from_client`; the current island does not.**

## Relocation targets

```text
stock : .rodata+0x288, .rodata.str1.1+0x129, +0x993, +0xa38, +0xff, +0xffa,
        __stack_chk_fail, _printk, cpu_hwcaps, memset,
        tee_context_copy_from_client
island: .rodata+0x260, .rodata.str1.1+0x277, +0x7d, +0x82a, +0xb2b, +0xd3f,
        _dev_err, cpu_hwcaps
```

Stock references a 16-entry dispatch table at `.rodata+0x288`; the island has an equivalent table at `.rodata+0x260`. `cpu_hwcaps` is present in both, from inlined uaccess.

Stock strings reached from this function:

```text
+0x129  "tkcore:   *** Wrong returned size from %d:%zd > %zd\n"
+0x993  "tkcore: Failed to copy op from client\n"          <-- no island equivalent
+0xa38  "tkcore: can't update %d data to user\n"
+0xff   "tkcore: can't update %d result to user\n"
+0xffa  "tkcore: type is invalid (type %02x)\n"
```

The island has no counterpart to `+0x993`, because it never performs the copy that can fail.

## Direct dependency state

| Property | Stock | Island |
|---|---|---|
| `tee_context_copy_from_client` size | 436 | 436 |
| linkage | GLOBAL | GLOBAL |
| KCFI | `0x7050299b` | `0x7050299b` |
| bytes | — | **byte-identical** |

The helper the island must call is already present and already exact. Only the call site is missing.

## Semantic defect at RED

Stock copies the entire 280-byte `TEEC_Operation` from the client into a zeroed stack local once, then reads every client-supplied field from that local while writing outputs to the client object.

The island reads client-supplied fields by dereferencing `cmd_io->op` directly:

```c
if (size_new != cmd_io->op->params[idx].tmpref.size)
offset = cmd_io->op->params[idx].memref.offset;
size   = cmd_io->op->params[idx].memref.size;
```

For a user client `cmd_io->op` is a `__user` pointer, so these are unchecked kernel-context reads of user addresses, performed outside the uaccess machinery stock routes through.

## Affected parameter kinds

From the stock dispatch table at `.rodata+0x288`:

| Type | Stock target | Consumes refreshed fields |
|---|---|---|
| `TEEC_MEMREF_WHOLE` (12) | `+0x10` | yes |
| `TEEC_MEMREF_PARTIAL_OUTPUT` (14) | `+0x10` | yes |
| `TEEC_MEMREF_PARTIAL_INOUT` (15) | `+0x10` | yes |
| `TEEC_MEMREF_TEMP_OUTPUT` (6) | `+0x20` | yes |
| `TEEC_MEMREF_TEMP_INOUT` (7) | `+0x20` | yes |
| `TEEC_VALUE_OUTPUT` (2) / `VALUE_INOUT` (3) | `+0x110` | no |
| `TEEC_MEMREF_PARTIAL_INPUT` (13) | `+0x478` | skipped |
| `NONE` (0), `VALUE_INPUT` (1), `TEMP_INPUT` (5) | `+0x478` | skipped |

## Required GREEN

1. `tee_context_copy_from_client` appears in the island call set for `_update_client_tee_cmd`.
2. The call occurs once, before the parameter loop, after `err`/`origin` publication.
3. Every client-supplied read in the loop is served from the refreshed local copy.
4. Outputs continue to be written to the client object.
5. Copy failure produces a diagnostic and an immediate return.
6. No change to ownership, release, or list handling.
7. Coverage stays 113/122; missing set unchanged; exports stay 21/25.
