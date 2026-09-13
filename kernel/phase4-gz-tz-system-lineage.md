# `gz_tz_system.ko` — source lineage

## 1. Chain of custody

```
Ulefone GQ5012BF1 stock firmware
  └─ vendor_dlkm/lib/modules/gz_tz_system.ko
       sha256 4b29f9b401c43fe98373d17c0360340c0c58f2cc15e2dfbfd536a60bb9484e38
       79648 B · Build ID dcba5910d6fc9b3d5e71f9d172d49a68b3189b1a
       vermagic 6.1.115-android14-11-g945dff7bc1bf
         │
         │  identified by: complete function/export/string/alias match
         ▼
NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878
  @ 957dac185efe46cbf6336b0fff9516d84c8cd78f            <- SAME PIN as ffa_v10 + tmem_ffa
  └─ drivers/misc/mediatek/geniezone/
       ├─ Makefile     obj-$(CONFIG_MTK_GZ_TZ_SYSTEM) += gz_tz_system.o
       │               gz_tz_system-objs += tz_system.o mtee-kree/tz_mmap.o mtee-kree/kree_mem.o
       ├─ Kconfig      config MTK_GZ_TZ_SYSTEM (tristate)
       ├─ tz_system.c        34048 B
       ├─ mtee-kree/kree_mem.c 27272 B
       ├─ mtee-kree/tz_mmap.c   3247 B
       └─ public/{kree,tz_cross,gz-trusty}/  (headers, same revision)
         │
         ▼
/home/armol/kernel-work/gki-12901745-workspace/lieppos/gz-tz-system/
         │
         ▼  //lieppos/gz-tz-system:gz_tz_system  against  //common:kernel_aarch64
gz_tz_system.ko  —  61/61 functions byte-identical, 27/27 export CRCs natural
```

## 2. Why this revision is the right pin

The pin was not chosen for convenience — it is the revision already proven
twice on this device:

| module | pin | result |
|---|---|---|
| `ffa_v10.ko` | `957dac18`, `trusted_mem/ffa_v10/` | 34/34 byte-identical, 5/5 CRCs natural |
| `tmem_ffa.ko` | `957dac18`, `trusted_mem/` | 141/141 byte-identical, 15/15 CRCs natural |
| **`gz_tz_system.ko`** | `957dac18`, `geniezone/` | **61/61 byte-identical, 27/27 CRCs natural** |

Three different MediaTek subsystems from one revision all reproduce the stock
GQ5012BF1 binaries. That is strong, independent corroboration that
`device_modules@957dac18` is the correct vendor baseline for this device's
`vendor_dlkm` TEE/secure-memory stack.

## 3. Dating the source

| signal | value |
|---|---|
| last upstream change to `tz_system.c` in the pinned repo | `890d12f5a640`, 2023-04-06, "[ALPS07941753] gz: check probe done condition" |
| file content at `957dac18` | identical to `890d12f5a640` |
| kernel baseline | 6.1.115-android14-11 (ab/12901745) |

The file has been stable since April 2023 in that tree. The full commit
history touching it (12 commits, 2020-09→2023-04) was enumerated and each
revision checked for the CamelCase weak-stub form — **none has it**, which is
what establishes the delta below as a vendor-integrator difference rather than
a revision we simply failed to locate.

## 4. The one lineage discontinuity

`tz_system.c`'s `CONFIG_TEE` block at every reachable public revision declares
its five weak fallbacks in snake_case against `struct teec_context`,
`teec_session`, `teec_uuid`, `teec_operation` — types that **no header in the
tree defines**. The block therefore cannot compile (RED-A, 9 ×
`-Wvisibility -Werror`), while the call sites 60 lines below it already use
the CamelCase `TEEC_*` API from the `tee_client_api.h` included under the same
guard.

The GQ5012BF1 stock binary has the self-consistent form: five WEAK symbols
named `TEEC_InitializeContext` / `TEEC_FinalizeContext` / `TEEC_OpenSession` /
`TEEC_CloseSession` / `TEEC_InvokeCommand`.

**How the exact prototypes were pinned without guessing:** clang's kCFI type
id is a hash of the complete prototype *including struct tag names*. The five
stock stubs carry

```
TEEC_InitializeContext 0x124b473b    TEEC_FinalizeContext 0xf4c49135
TEEC_OpenSession       0xde69c0a6    TEEC_CloseSession    0x31bed4ef
TEEC_InvokeCommand     0x593c5866
```

which are **byte-identical to the ids on tkcore's real implementations of the
same five functions** (`kernel/phase4-tkcore-exports.tsv`). Five independent
32-bit matches fix the prototypes to the GlobalPlatform CamelCase forms with
certainty; nothing was invented.

## 5. Classification

`EXACT_SOURCE` for `mtee-kree/tz_mmap.c` and `mtee-kree/kree_mem.c` (used
completely unmodified), and `EXACT_SOURCE_DIFFERENT_REVISION` for one 45-line
block of `tz_system.c`, closed by a rename that is evidence-pinned five ways.

Overall module classification: **`SOURCE_DELTA_RECONSTRUCTION_EXACT`** — see
`kernel/phase4-gz-tz-system-reconstruction.md` §Classification for why this is
preferred over `DIRECT_SOURCE_MATCH`.

## 6. Local artifacts

| path | content |
|---|---|
| `lieppos/gz-tz-system/src/` | pinned vendor source (one evidence-backed delta, commented in place) |
| `lieppos/gz-tz-system/inc/` | byte-identical vendor headers, same revision |
| `lieppos/gz-tz-system/Makefile` | build plumbing + proven config set only |
| `lieppos/gz-tz-system/BUILD.bazel` | kleaf target against `//common:kernel_aarch64` |
| `lieppos/gz-tz-system/stock-provider.symvers` | 7 genuine stock provider ABI records |
| `lieppos/gz-tz-system-red/` | the untouched RED donor package |
