# GQ5012BF1 tkcore supplicant-init lifecycle audit

Scope: lifecycle sufficiency of `tee_supp_init`/`tee_supp_deinit` for `tee_core_alloc`, `tee_core_free` and `tee_core_del` only. The supplicant/RPC command surface (`tee_supp_cmd`, `tee_supp_read`, `tee_supp_write`) is **not** audited or changed here.

## Result

**LIFECYCLE-SUFFICIENT.** Both functions are now byte-identical to stock, and `tee->rpc` is proven to be initialised at the correct offset with the correct object size.

| Function | Stock offset | Size | KCFI | Phase-2 | Phase-3P |
|---|---:|---:|---|---|---|
| `tee_supp_init` | `0x6c94` | 176 | `0xa1200a70` | donor-ported, call-set different (200 bytes) | **EXACT_BYTE** |
| `tee_supp_deinit` | `0x6d48` | 52 | `0x246c186b` | EXACT_BYTE | **EXACT_BYTE** (unchanged) |

## What changed

Only one thing: the island's `struct tee_rpc` carried a fourth mutex, `reqsync`, that stock does not have. It was dead — referenced nowhere in the island source except its own declaration — and it inflated the object to `0x208`. Stock allocates exactly `0x1d8` (472) bytes and initialises exactly three mutexes. Removing the dead member makes the allocation size, the initialisation sequence and the emitted code match stock byte for byte. A `static_assert(sizeof(struct tee_rpc) == 0x1d8)` now pins this.

## Verified initialisation contract

`tee_supp_init(struct tee *tee)`:

1. `devm_kmalloc(tee->dev, 0x1d8, GFP_KERNEL | __GFP_ZERO)` — flags `0xdc0`, i.e. the zeroing managed allocation the donor spelled `devm_kzalloc`.
2. Allocation failure → return `-ENOMEM`. Stock emits **no** message here; the donor's `dev_err` was removed, which is part of reaching byte parity.
3. Two semaphores initialised to count 0 with self-linked wait lists:
   - `datatouser` at `rpc+0x110`, wait list `rpc+0x118`
   - `datafromuser` at `rpc+0x128`, wait list `rpc+0x130`
4. Three mutexes with stock's exact lockdep names:
   - `rpc+0x140` `&rpc->thrd_mutex`
   - `rpc+0x170` `&rpc->outsync`
   - `rpc+0x1a0` `&rpc->insync`
5. `atomic_set(&rpc->used, 0)` at `rpc+0x1d0`.
6. `tee->rpc = rpc` stored at **`tee+0xb0`**.
7. Return `0`.

This confirms the Phase-3A finding that the RPC pointer lives at `tee+0xb0`; the anchor is now enforced by `TK_ASSERT_OFF(struct tee, rpc, 0xb0)`.

`tee_supp_deinit(struct tee *tee)` calls `devm_kfree(tee->dev, tee->rpc)` and clears the pointer.

## Lifecycle sufficiency checklist

| Requirement | Status |
|---|---|
| Allocation size and flags | Exact (`0x1d8`, `GFP_KERNEL|__GFP_ZERO`) |
| Field initialisation | Exact (two semaphores, three mutexes, one atomic) |
| Locks | Exact count, offsets and lockdep names |
| Waitqueues | None required — stock uses counting semaphores, not waitqueues |
| Failure return | Exact (`-ENOMEM`, no message) |
| `tee->rpc` population | Exact offset `0xb0`, set only on success |
| Teardown pairing | Exact; `tee_supp_deinit` already byte-identical |

## No dependency on deferred code

`tee_supp_init` calls only `devm_kmalloc` and `__mutex_init`. It does not touch `tee_supp_cmd`, `tee_supp_open`, `tee_supp_read`, `tee_supp_write` or any shared-memory routine, so nothing outside the allowed lifecycle scope had to be implemented and no behaviour had to be invented. The layout the RPC command surface will later need is now fixed by the byte-exact initialiser, which reduces risk for the deferred supplicant phase rather than pre-empting it.
