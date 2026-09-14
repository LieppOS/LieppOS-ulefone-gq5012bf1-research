# GQ5012BF1 Phase 3C-R — regression report

Three-way comparison: stock oracle, frozen Phase-3C, rebuilt Phase-3C-R.

## Module identity

| | Phase 3C | Phase 3C-R |
|---|---|---|
| SHA-256 | `e7a8e2a725d7cd3dde2f674fdf9806edcc3766740fd9aa22df1e610b2c1a98fd` | `7d9d7979521853c8d5a4412bb08c534870cd977a2f1efebe363f172ef067aeee` |
| size | 190504 | 190784 |
| srcversion | `A8E1233E932526AA5843578` | `8AFF88A87FBB74AB1FCB2D7` |
| Build ID | `a39b62e0ed93fd691ff592a8503b84185f8063c1` | `316c670d516f9fb7f823c0b588ce586a186c3549` |
| depends | empty | empty |

Growth is +280 bytes of module, of which +68 bytes is `_update_client_tee_cmd` and +41 bytes is the new stock diagnostic string.

## Invariants held

| Metric | Stock | Phase 3C | Phase 3C-R | Verdict |
|---|---:|---:|---:|---|
| stock functions present | 122 | 113 | **113** | unchanged, as required |
| missing | 0 | 9 | **9** | unchanged |
| island-only functions | — | 0 | **0** | unchanged |
| byte-identical to stock | — | 47 | **47** | none lost, none gained |
| exports | 25 | 21 | **21** | unchanged |
| undefined imports | 100 | 97 | **97** | unchanged |
| relocations | 3098 | 2716 | 2725 | +9, all from the new call and string |

```text
added functions:   none
removed functions: none
new imports:       none
removed imports:   none
export delta:      none
```

**No function-count progress is claimed.** `_update_client_tee_cmd` already existed; this task improved semantic closure quality only.

The missing set is unchanged and remains exactly:

```text
tee_clkmgr_handle
tee_spi_cfg_padsel  tee_spi_transfer  tee_spi_transfer_disable
big_core_affinity_get_candidate_cpu  big_core_affinity_match_cpu
big_core_affinity_need_bind_cpu  plat_cpu_is_big  plat_tee_init
```

## The change is narrow, and that is proven rather than asserted

Exactly five functions differ byte-wise between Phase 3C and Phase 3C-R. Four of them have **identical sizes**:

| Function | 3C | 3C-R | Nature |
|---|---:|---:|---|
| `_update_client_tee_cmd` | 1608 | 1676 | **the intended semantic change** |
| `_init_tee_cmd` | 804 | 804 | placement only |
| `tee_session_create_and_open` | 660 | 660 | placement only |
| `tee_session_internal_ioctl` | 1984 | 1984 | placement only |
| `tee_session_invoke_be` | 300 | 300 | placement only |

Every difference in those four was attributed mechanically, not by inspection. Each differing line is either:

- a cross-function branch whose displacement moved by exactly **±68** bytes (the growth of the target), or
- a `.rodata.str1.1` relocation addend that moved by exactly **+41** bytes (the length of the added `"tkcore: Failed to copy op from client\n"` string).

```text
relocation addend shifts observed: {41}
unexplained differences:           0
VERDICT: PLACEMENT-ONLY
```

## Subsystems confirmed untouched

Byte-identical between Phase 3C and Phase 3C-R:

```text
core lifecycle      tee_core_alloc, tee_core_add
context/session     tee_context_copy_from_client
shared memory       tkcore_shm_get, tee_shm_alloc_from_rpc
native ioctl        tee_internal_ioctl
compat ioctl        tee_compat_ioctl, tee_session_compat_ioctl
compat converters   convert_compat_tee_cmd, convert_compat_tee_shm_io,
                    convert_compat_tee_spta_inst
uaccess helpers     uaccess_ttbr0_enable, uaccess_ttbr0_disable
command path        TEEC_InvokeCommand, _release_tee_cmd, tee_supp_cmd
```

`tee_session_internal_ioctl` appears in the changed list but is placement-only per the attribution above; its instruction stream and relocation targets are identical.

`tee_context_copy_from_client` is byte-identical to **stock** and was not modified.

## Target comparison

| | Stock | Phase 3C | Phase 3C-R |
|---|---:|---:|---:|
| size | 1652 | 1608 | 1676 |
| instructions | 413 | 402 | 419 |
| `tee_context_copy_from_client` edge | yes (1 site) | **no** | **yes (1 site)** |
| call set | `__stack_chk_fail`, `_printk`, `memset`, `tee_context_copy_from_client` | `_dev_err` | `__stack_chk_fail`, `_dev_err`, `_printk`, `memset`, `tee_context_copy_from_client` |
| stock-only edges remaining | — | 4 | **0** |
| type-dispatch partition vs stock | — | — | **identical** |

The 16-entry dispatch table groups parameter types into exactly the same five classes as stock, including `PARTIAL_INPUT` being grouped with the skipped input types rather than with the output-capable registered memrefs.

## Remaining call-set difference, explained

`_dev_err` is island-only. It is the island's established logging convention (`dev_err`/`dev_dbg` with a `%s:` function prefix) where stock uses `pr_err` with a `tkcore: ` prefix. It affects log text only: no argument crosses the ABI boundary, no allocation, no reference count, no lifetime. It is retained for consistency with the rest of the island.

The newly added diagnostic deliberately uses `pr_err` so that the emitted string matches stock byte-for-byte, including the `KERN_ERR` prefix:

```text
"\x013tkcore: Failed to copy op from client\n"
```

`memset` and `__stack_chk_fail` are now present in the island because the function gained a 280-byte zeroed stack local — the same reason stock has them.

## Ownership and lifetime

The corrected function's call set contains no `tkcore_shm_put`, `tkcore_shm_free`, `__list_add_valid`, or dma-buf entry. No put, free, list insertion, or ownership transfer was added. Provider-owned allocation lifetime and foreign-memory reference lifetime remain separated exactly as Phase 3B established.

## Verifiers

| Verifier | Phase 3C | Phase 3C-R |
|---|---:|---:|
| Phase 3C-R | — | **to be reported by its own verifier** |
| Phase 3C | 85/85 | **85/85** |
| Phase 3B | 203/203 | **203/203** |
| Phase 3A-R | 162/162 | **162/162** |

Zero `[FAIL]` lines across all three pre-existing verifiers.

## Build

```text
BUILD_RC=0  warnings=0  errors=0  modpost=0  unresolved=0  static-assert failures=0
depends=(empty)
```

No layout assertion was weakened, removed, or added.
