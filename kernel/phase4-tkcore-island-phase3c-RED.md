# GQ5012BF1 tkcore island Phase 3C — immutable RED

Captured against the clean, byte-exact Phase-3B baseline **before implementation**. This file records failure, not completion, and must never be rewritten as GREEN.

Oracle: committed stock `tkcore.ko`, SHA-256 `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`. Baseline: `tkcore.phase3b.ko`, SHA-256 `860ad5ee0c4da579627c202b19892b20e44ef34287054f11ab802b09e9933640`.

## Primary RED — seven required stock functions are absent

`NOT_EMITTED_DIRECT_ONLY` means stock places no KCFI type word before the function because the function is only reached by a direct call. It is not a guessed hash and not a mismatch.

| Function | Stock offset | Size | Stock KCFI | Linkage | Stock caller / object edge | Stock callees | External imports | Stock objects / strings | Phase-3B equivalent | Current failure |
|---|---:|---:|---|---|---|---|---|---|---|---|
| `tee_internal_ioctl` | `0x1f4c` | 3260 | NOT_EMITTED_DIRECT_ONLY | LOCAL | direct from `tee_ioctl`; native wrapper is `tee_{client,admin}_fops.unlocked_ioctl` | `tee_shm_alloc_io`, `tee_session_create_fd`, `tee_shm_fd_for_rpc` plus inline command-specific work | `__arch_copy_{from,to}_user`, `_printk`, `memset`, stack protector | runtime `/dev` descriptors; diagnostics for unknown command, bad SHM/session/op/data, SPTA operations | donor logic split among `tee_ioctl`, `tee_do_create_session`, `tee_do_shm_alloc`, `tee_do_get_fd_for_rpc_shm` | **ABSENT**; current dispatch covers only 3 commands and has no stock internal layer |
| `tee_session_internal_ioctl` | `0x4b7c` | 1996 | NOT_EMITTED_DIRECT_ONLY | LOCAL | direct from `tee_session_ioctl`; wrapper is `tee_session_fops.unlocked_ioctl` | inlined/direct command validation and backend path | `_printk`, stack protector | diagnostics for invoke, cancellation, invalid op/data and errors | donor logic split among `tee_session_ioctl`, `tee_do_invoke_command`, `tee_do_cancel_cmd` | **ABSENT** |
| `tee_session_compat_ioctl` | `0x4670` | 132 | `0xe01408cd` | LOCAL | `tee_session_fops.compat_ioctl` (+0x58 in stock randomized layout) | `convert_compat_tee_cmd` | none | `tee_session_fops` | none | **ABSENT**; Phase-3B wrongly points compat at native `tee_session_ioctl` |
| `tee_compat_ioctl` | `0x15e8` | 244 | `0xe01408cd` | LOCAL | `tee_client_fops.compat_ioctl`, `tee_admin_fops.compat_ioctl` (+0x58) | all three converters | none | both node fops | none; slot intentionally omitted in Phase-3B | **ABSENT** |
| `convert_compat_tee_cmd` | `0x0384` | 3644 | `0xbb8e9218` | GLOBAL, not exported | both compat wrappers | **direct local calls to `uaccess_ttbr0_enable` and `uaccess_ttbr0_disable`** around the `operation+0x6c` store | `__arch_copy_from_user`, `_printk`, stack protector | `"bad param %u"`; compat/native command structures | none | **ABSENT; mandatory prohibited uaccess prerequisite proven — STOP** |
| `convert_compat_tee_shm_io` | `0x1284` | 276 | `0xdaee5623` | GLOBAL, not exported | `tee_compat_ioctl` | none | none (user access is inlined) | compat/native SHM structures | none | **ABSENT** |
| `convert_compat_tee_spta_inst` | `0x139c` | 516 | `0xba9dd2d9` | GLOBAL, not exported | `tee_compat_ioctl` | none | none (user access is inlined) | compat/native SPTA structures | none | **ABSENT** |

Exact relocation-aware oracle blocks for all seven are frozen under `workspace/phase4-tkcore-island/phase3c/oracle-functions/stock.*.objdump.txt`.

### Primary stock diagnostics

- `tee_internal_ioctl`: `create_session: copy_from_user failed`; `internal_ioctl: Unknown command: %u`; invalid SHM pointer/size/fd; expected-unregistered SHM; invalid flags; copy failure; invalid op/data; invalid session fd.
- `tee_session_internal_ioctl`: invoke/cancel copy failure, invalid op/data, and invoke errors.
- `convert_compat_tee_cmd`: `bad param %u`.
- The other four functions carry no diagnostic string.

## File-operations RED

Stock defines three 272-byte `struct file_operations` objects. Relocation targets are exact despite randomized member offsets:

| Object | Non-NULL stock fields |
|---|---|
| `tee_client_fops` | owner; `unlocked_ioctl=tee_ioctl`; `compat_ioctl=tee_compat_ioctl`; `open=tee_ctx_open`; `release=tee_ctx_release` |
| `tee_admin_fops` | owner; `read=tee_supp_read`; `write=tee_supp_write`; `unlocked_ioctl=tee_ioctl`; `compat_ioctl=tee_compat_ioctl`; `open=tee_supp_open`; `release=tee_supp_release` |
| `tee_session_fops` | owner; `unlocked_ioctl=tee_session_ioctl`; `compat_ioctl=tee_session_compat_ioctl`; `release=tee_session_release` |

Phase 3B omits both client/admin compat slots and aliases the session compat slot to the native handler. Thus the stock fops graph is not closed even though all three objects exist.

## Existing command path — presence is not acceptance

| Function | Stock / Phase-3B size | KCFI | Stock versus baseline call evidence | RED status |
|---|---:|---|---|---|
| `TEEC_InvokeCommand` | 300 / 224 | `0x593c5866` exact | stock additionally calls `memset` and `_printk`; both call IDR lookup and `tee_session_invoke_be` | PRESENT, **UNAUDITED / NOT ACCEPTED** |
| `tee_supp_cmd` | 340 / 336 | `0xa47645b6` exact | call sequences match except stock `_printk` versus island `_dev_err` | PRESENT, **UNAUDITED / NOT ACCEPTED** |
| `_init_tee_cmd` | 808 / 804 | NOT_EMITTED in both | same ownership calls; stock uses two `_printk`, island has `_dev_err` + `_printk` | PRESENT, **UNAUDITED / NOT ACCEPTED** |
| `_update_client_tee_cmd` | 1652 / 1608 | NOT_EMITTED in both | materially different calls: stock has `memset`, `tee_context_copy_from_client`, 5×`_printk`, stack protector; baseline has 5×`_dev_err` | PRESENT, **SEMANTICS UNPROVEN** |
| `_release_tee_cmd` | 600 / 548 | NOT_EMITTED in both | same exact multiset: `tkcore_shm_free` 5×, `tkcore_shm_put` 4×; CFG still differs | PRESENT, **LIFETIME ORDER UNPROVEN** |
| `tee_copy_from_user` | 432 / 432 | NOT_EMITTED in both | **byte-identical**; same user-copy / kernel-copy / zeroing paths | PRESENT, strong evidence but command-path use still audited |
| `tee_shm_alloc_from_rpc` | 188 / 192 | stock `0x45b20ce9`, baseline `0x6fc0bbe3` | same call multiset; prototype mismatch is pre-existing | PRESENT, quarantined mismatch; may change only if direct Phase-3C RPC evidence proves it wrong |

## Boundary blocker found during RED recovery

The full stock block proves `bl 0x11c0 <uaccess_ttbr0_enable>` at `0x07bc` and `bl 0x1224 <uaccess_ttbr0_disable>` at `0x07c8`. Both target symbols are also absent in Phase 3B and explicitly outside the Phase-3C boundary unless directly required. This satisfies the mandatory stop condition before any implementation. See `phase4-tkcore-island-phase3c-uaccess-prerequisite-blocker.md`.

## RED conclusion

```text
PRIMARY_PRESENT=0/7
FOPS_COMPAT_CLOSED=NO
TEEC_INVOKE_ACCEPTED=NO
COMMAND_HELPERS_ACCEPTED=NO
PASS_STATIC_INVOKE=NO
PASS_STATIC_COMMAND=NO
TKCORE_ISLAND_PHASE3C_STATUS=RED
```

No source was edited before this RED state and its binary/function evidence were frozen.
