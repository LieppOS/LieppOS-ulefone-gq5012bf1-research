# GenieZone main-stack acceptance (through gz_main_mod)

## 1. The stack, with provenance

```
exact GKI ab/12901745  (Linux 6.1.115-android14-11, common 6b18f0b574ab)
        |
gz_trusty_mod   V:145   DIRECT_SOURCE_MATCH               / FROZEN FOR RE
        |
gz_ipc_mod      V:146   DIRECT_SOURCE_MATCH               / FROZEN FOR RE
        |
gz_tz_system    V:149   SOURCE_DELTA_RECONSTRUCTION_EXACT / FROZEN FOR RE
        |
gz_main_mod     V:150   DIRECT_SOURCE_MATCH               / THIS TASK
        |
       (leaf - no kernel consumers; userspace ABI only)

side providers, both consumed by gz_main_mod:
ffa_v10         vendor ramdisk   DIRECT_SOURCE_MATCH / FROZEN FOR RE
tmem_ffa        V:152            SOURCE_NOW          / FROZEN FOR RE

declared stock runtime provider:
mtk_sec_heap    V:?              STOCK - not reconstructed
```

## 2. Every cross-module edge

| consumer | provider | edges | provenance | result |
|---|---|---:|---|---|
| `gz_ipc_mod` | `gz_trusty_mod` | 3 | source-built | NATURAL (pre-existing, unchanged) |
| `gz_tz_system` | `gz_ipc_mod` | 5 | source-built | NATURAL (pre-existing, unchanged) |
| `gz_tz_system` | `gz_trusty_mod` | 2 | source-built | NATURAL (pre-existing, unchanged) |
| **`gz_main_mod`** | `gz_tz_system` | **15** | source-built (witness-free acceptance build) | **NATURAL** |
| **`gz_main_mod`** | `gz_trusty_mod` | **5** | source-built | **NATURAL** |
| **`gz_main_mod`** | `gz_ipc_mod` | **1** | source-built | **NATURAL** |
| **`gz_main_mod`** | `ffa_v10` | **1** | source-built | **NATURAL** |
| **`gz_main_mod`** | `tmem_ffa` | **2** | source-built | **NATURAL** |
| **`gz_main_mod`** | `mtk_sec_heap` | **1** | **STOCK runtime provider, declared** | EXACT, not natural |
| **`gz_main_mod`** | exact GKI | **51** | exact GKI | **NATURAL** |
| `tmem_ffa` | `gz_tz_system` | 9 | source-built | NATURAL (pre-existing) |
| `tmem_ffa` | `ffa_v10` | 1 | source-built | NATURAL (pre-existing) |
| `tmem_ffa` | `tkcore` | 7 | **STOCK runtime provider** | pre-existing declared boundary, untouched |

`gz_main_mod` totals: **76 imports, 75 natural, 1 declared stock.**

## 3. Frozen providers were not disturbed

Re-run after the `gz_main_mod` build completed:

| verifier | result |
|---|---|
| `phase4_gz_trusty_mod_verify.py` | **239/239 CHECKS PASSED** |
| `phase4_gz_ipc_mod_verify.py` | **269/269 CHECKS PASSED** |
| `phase4_gz_transport_stack_verify.py` | **738/738 CHECKS PASSED** |
| `phase4_gz_tz_system_verify.py` | **120/120 CHECKS PASSED** |

`gz_main_mod` is a pure consumer: it exports nothing, so no provider was
re-linked, no CRC anywhere else changed, and no frozen classification moved.

## 4. Remaining non-source providers in this stack

Exactly two, both explicitly declared, neither introduced by this task:

| provider | consumer(s) | edges | status |
|---|---|---:|---|
| `mtk_sec_heap` | `gz_main_mod` | 1 (`dmabuf_to_secure_handle`) | genuinely stock; **newly declared by this task** |
| `tkcore` | `tmem_ffa` | 7 (`TEEC_*`) | genuinely stock; pre-existing boundary, untouched |

Neither is described as reconstructed anywhere.

## 5. What is explicitly NOT claimed

* No claim of secure-world source purity. The GenieZone hypervisor, the
  Trusty/Nebula TEE OS, and all TA code remain closed and unanalysed.
* `mtk_sec_heap` and `tkcore` are stock binaries at runtime.
* SMC semantics beyond what the Linux source states are not reverse
  engineered.

## 6. Linux-side status of the GenieZone stack

With `gz_main_mod` closed, the Linux-visible GenieZone client stack —
transport (`gz_trusty_mod`, `gz_ipc_mod`), KREE provider (`gz_tz_system`),
main client and userspace ABI owner (`gz_main_mod`), FF-A transport
(`ffa_v10`) and trusted memory (`tmem_ffa`) — is source-closed end to end,
with every source-available provider edge natural.
