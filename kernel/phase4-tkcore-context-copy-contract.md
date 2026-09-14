# GQ5012BF1 `tee_context_copy_from_client` — audit

Audited as a direct dependency of `_update_client_tee_cmd`, **not** treated as a black box.

## Verdict

**ALREADY STOCK-EXACT. NOT MODIFIED.**

| Property | Stock | Island | Match |
|---|---|---|---|
| offset | `0x362c` | `0x2d28` | n/a (placement) |
| size | 436 | 436 | yes |
| linkage | GLOBAL | GLOBAL | yes |
| exported | no | no | yes |
| KCFI type id | `0x7050299b` | `0x7050299b` | yes |
| instruction bytes | — | — | **byte-identical** |
| call set | `__arch_copy_from_user`, `__check_object_size`, `memcpy`, `memset` | identical | yes |

SHA-256 of the function body is identical in both images (`866aac38583b54ff…`).

Per the task rule "if it is already correct, do not rewrite it", no change was made.

## Recovered prototype

```c
int tee_context_copy_from_client(const struct tee_context *ctx,
                                 void *dest, const void *src, size_t size);
```

## Behaviour

- **User client** (`ctx->usr_client != 0`): performs a checked copy from user space — `__check_object_size` followed by `__arch_copy_from_user`, i.e. the standard `copy_from_user` expansion with hardened usercopy enabled.
- **Kernel client** (`ctx->usr_client == 0`): plain `memcpy`.
- `memset` appears on the short-copy path, zero-filling the unwritten tail exactly as `copy_from_user` semantics require.
- **Return convention**: 0 on success, non-zero on failure. Callers test with `cbnz`.
- **Context field used**: `usr_client` at offset `0x8c` of `struct tee_context`, matching the existing PROVEN layout anchor.

## Why this matters for the residual

This helper is the only place in the command path that decides user-versus-kernel copy semantics. Because it is already byte-exact, routing `_update_client_tee_cmd`'s client reads through it is sufficient to restore stock behaviour — no new uaccess code, and no new import, is required.

It is already used identically by `_init_tee_cmd`, so the corrected `_update_client_tee_cmd` reuses an established, verified island call site pattern rather than introducing a new one.
