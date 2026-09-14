# GQ5012BF1 tkcore island Phase 3C — ioctl + command-marshalling closure

## Classification

```text
TKCORE_ISLAND_PHASE3C_IOCTL_COMMAND_CLOSED
Overall tkcore:                  PARTIAL / NOT RUNTIME READY
Runtime provider:                STOCK
TKCORE REPLACEMENT READY:        NO
Final three-consumer acceptance: DEFERRED (todo #18 OPEN)
Next phase:                      3D - CLOCK RUNTIME + SECURE SPI
```

## Authorized scope actually used

Seven primary functions plus the two direct uaccess prerequisites explicitly authorized after the Phase-3C stop. **No other previously excluded subsystem was touched.** No new direct prerequisite was discovered, so no second stop was required.

## Measured result

| Metric | Phase 3B | Phase 3C | Target |
|---|---:|---:|---:|
| stock-function coverage | 104 / 122 | **113 / 122** | 113 / 122 |
| missing stock functions | 18 | **9** | 9 |
| byte-identical functions | 44 | **47** | — |
| island-only (fabricated) functions | 0 | **0** | 0 |
| module size | 166120 | 190504 | — |
| exports | 21 / 25 | 21 / 25 | unchanged |
| undefined imports | 97 | 97 | ≤ stock 100 |
| `depends` | empty | **empty** | empty |

The nine remaining missing functions are **exactly** the excluded set, confirmed by the verifier as a set equality rather than a count:

```text
tee_clkmgr_handle
tee_spi_cfg_padsel  tee_spi_transfer  tee_spi_transfer_disable
big_core_affinity_get_candidate_cpu  big_core_affinity_match_cpu
big_core_affinity_need_bind_cpu  plat_cpu_is_big  plat_tee_init
```

## Phase-3C module identity

```text
SHA256:     e7a8e2a725d7cd3dde2f674fdf9806edcc3766740fd9aa22df1e610b2c1a98fd
size:       190504
Build ID:   a39b62e0ed93fd691ff592a8503b84185f8063c1
srcversion: A8E1233E932526AA5843578
vermagic:   6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64
depends:    (empty)
import_ns:  DMA_BUF
```

## Per-function outcome

| Function | Stock | Island | Linkage | KCFI | Bytes |
|---|---:|---:|---|---|---|
| `convert_compat_tee_shm_io` | 276 | **276** | GLOBAL | `daee5623` exact | **identical** |
| `uaccess_ttbr0_enable` | 100 | **100** | LOCAL | n/a | **identical** |
| `uaccess_ttbr0_disable` | 92 | **92** | LOCAL | n/a | **identical** |
| `convert_compat_tee_spta_inst` | 516 | **516** | GLOBAL | `ba9dd2d9` exact | 129/129 insns, 1 tail-block order |
| `tee_session_compat_ioctl` | 132 | **132** | LOCAL | `e01408cd` exact | 33/33 insns, scheduling |
| `tee_session_ioctl` | 56 | **56** | LOCAL | `e01408cd` exact | scheduling |
| `tee_compat_ioctl` | 244 | 216 | LOCAL | `e01408cd` exact | see emission note |
| `tee_ioctl` | 64 | 52 | LOCAL | `e01408cd` exact | see emission note |
| `tee_internal_ioctl` | 3260 | 3304 | LOCAL | direct-only (correct) | see emission note |
| `tee_session_internal_ioctl` | 1996 | 1984 | LOCAL | direct-only (correct) | see emission note |

`tee_internal_ioctl` and `tee_session_internal_ioctl` carry **no** KCFI type word in either image. The verifier proves this the right way — by showing no `R_AARCH64_ABS64` relocation stores their address — rather than by reading whatever instruction happens to precede the entry point.

## The uaccess prerequisite: compiler-emitted, not hand-written

The preferred experiment succeeded on the first attempt. Writing only the proven source-level `put_user` shape, against the exact-GKI headers and toolchain, caused Clang to materialise both helpers by itself:

| Property | Result |
|---|---|
| names | `uaccess_ttbr0_enable`, `uaccess_ttbr0_disable` |
| binding | LOCAL = stock LOCAL |
| size | 100 / 92 = stock 100 / 92 |
| instruction bytes | **byte-identical to stock** |
| data relocations | `cpu_hwcaps` only, same relocation types |
| TTBR0/TTBR1, DAIF, ISB | identical sequences |

**No helper body was written by hand and no symbol was fabricated to raise the count.** They exist because exact-GKI `arch/arm64/include/asm/uaccess.h` static-inlines were materialised out-of-line by the compiler — candidate interpretation 1 from the blocker report, now confirmed.

## Compiler emission notes (differences, explained not forced)

- **`convert_compat_tee_cmd`**: island 2204 bytes / 551 instructions vs stock 3644 / 911. Both perform the same conversions in the same order with the same error contract. Stock fully unrolls the four-parameter walk and inlines most TTBR0 toggling; the island retains the loop and reaches the out-of-line helpers seven times. This is an inlining/unrolling threshold difference driven by source shape, which is not recoverable from the binary. Not forced.
- **`tee_ioctl` / `tee_compat_ioctl`**: slightly smaller. Stock places its `BUG_ON` traps inline; the island's land out-of-line. Same guards, same order.
- **`tee_internal_ioctl`**: 44 bytes larger, from the same trap-placement effect plus one extra branch in the supplicant gate.

Instruction counts were compared after normalising link-time branch targets to function-relative offsets, so raw address differences are not reported as divergence.

## ABI preserved exactly

- Six accepted ioctl commands, native and compat command numbers identical.
- Same-size in-place compat overlays; **no packed 32-bit replacement structures were invented**.
- `-EINVAL` vs `-EFAULT` distinctions preserved, including the wrappers collapsing any nonzero converter result to `-EFAULT`.
- Unknown commands return `-EINVAL`, not `-ENOSYS`/`-ENOIOCTLCMD`.
- The compat-only SPTA path is preserved with its stock inconsistency intact: conversion succeeds, native dispatch then rejects the command with `-EINVAL`. **No seventh command was invented.**
- All six fops ioctl edges resolve exactly as stock; compat slots are **not** aliased to the native handlers, and the verifier asserts the non-aliasing explicitly.
- `tee_client_fops`, `tee_admin_fops`, `tee_session_fops`: 272 bytes each, GLOBAL, matching stock slot occupancy.

## Struct tag recovered from the binary

`struct tee_spta_inst_desc` was **recovered**, not synthesised, by inverting the KCFI type id `0xba9dd2d9` over the signature shape pinned by the stock call site. Single solution in 77.07M candidates (expected false positives ≈ 0.018), confirmed by the real compiler, and independently corroborated by the function then compiling to stock's exact 516 bytes. See `phase4-tkcore-kcfi-type-recovery.md`.

## Verification

| Verifier | Result |
|---|---:|
| Phase 3C (new) | **85 / 85 PASS** |
| Phase 3B shared memory | **203 / 203 PASS** |
| Phase 3A-R core/context/session | **162 / 162 PASS** |
| build RC / warnings / errors / modpost / unresolved / assert failures | 0 / 0 / 0 / 0 / 0 / 0 |

Two verifier maintenance changes were required and are strengthening, not weakening:

1. `tee_core.c` registered as **co-owned** by Phase 3C, using the mechanism Phase 3B already established for `tee_kernel_api.c`. The immutable snapshot hash stays pinned and the Phase-3A-R behavioural assertions still run.
2. The Phase-3A-R "current build" check was resolving `phase3b/build/tkcore.phase3b.ko`, which went stale the moment Phase 3C landed — it was silently re-validating an old artifact. It now prefers the live build output, which is what its own comment always claimed it did.

## Open item carried forward

`_update_client_tee_cmd` is present but **not closed**: its call-edge set is disjoint from stock and it lacks stock's `tee_context_copy_from_client` re-read on the registered-memref output path. It is owned by Phase 3B and was outside the Phase-3C authorized set, so it is reported rather than rewritten. See `phase4-tkcore-command-path-audit.md`.

## Not performed

No runtime testing, device access, ioctl issuance, supplicant request, secure-world interaction, consumer rebuild, flash or reboot. `workspace/phase4-tkcore-island/acceptance/` remains empty and is asserted empty by the Phase-3C verifier.
