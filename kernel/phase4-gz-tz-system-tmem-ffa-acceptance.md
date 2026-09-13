# `tmem_ffa` acceptance rebuild against the real source-built `gz_tz_system`

**Result: PASS — 9/9 KREE provider edges NATURAL, tmem_ffa behaviour unchanged.**

`tmem_ffa`'s reconstruction status is **not** reopened by this. Its source was
not modified in any way; only the *provider* supplying 9 of its 76 import
edges changed, from a stock ABI record to a real source-built module.

## 1. What changed in the acceptance build

| input | frozen `tmem_ffa` build | this acceptance build |
|---|---|---|
| `tmem_ffa` source | unchanged | **unchanged (identical tree)** |
| FF-A provider | real source-built `//lieppos/ffa-v10` | same |
| tkcore provider | stock ABI record (7 `TEEC_*`) | same |
| **gz_tz_system provider** | **stock ABI record (9 `KREE_*`)** | **real source-built `//lieppos/gz-tz-system`** |

The 9 `KREE_*` lines were **deleted** from `stock-provider.symvers`, so they
can only resolve through the real provider's `Module.symvers`. The witness
file now carries 7 lines (tkcore only), down from 16.

Bazel target: `//lieppos/tmem-ffa-gzaccept:tmem_ffa_gzaccept`
with `deps = ["//lieppos/ffa-v10:ffa_v10", "//lieppos/gz-tz-system:gz_tz_system"]`.

## 2. The 9 KREE edges

Machine table: `kernel/phase4-gz-tz-system-tmem-ffa-acceptance.tsv`

| symbol | stock `tmem_ffa` requires | acceptance `tmem_ffa` | source-built `gz_tz_system` exports | status |
|---|---|---|---|---|
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | `0x552d4efc` | **NATURAL** |
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | `0x5878d629` | **NATURAL** |
| `KREE_TeeServiceCall` | `0xec19e146` | `0xec19e146` | `0xec19e146` | **NATURAL** |
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | `0x3d5d5254` | `0x3d5d5254` | **NATURAL** |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | `0x0175c8da` | `0x0175c8da` | **NATURAL** |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | `0x8dceb484` | `0x8dceb484` | **NATURAL** |
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | `0x9a19c31a` | `0x9a19c31a` | **NATURAL** |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | `0x44781e48` | `0x44781e48` | **NATURAL** |
| `KREE_ConfigSecureMultiChunkMemInfo` | `0xbdb6a34b` | `0xbdb6a34b` | `0xbdb6a34b` | **NATURAL** |

**9/9.** Every CRC is genksyms output from real C, not a copied value.

## 3. `tmem_ffa` parity against its own stock oracle

Re-measured from scratch in the acceptance build:

| axis | result |
|---|---|
| functions | 141 stock / 141 rebuilt, shared 141, extra 0, missing 0 |
| size-identical | 141/141 |
| **byte-identical** | **141/141** |
| KCFI type ids | **141/141 exact** |
| imports | 76 / 76 — **identical set** |
| MODVERSIONs | 77 / 77 — **identical, every CRC** |
| exports | 15 / 15, **15/15 CRCs natural** |
| strings | 286 / 286 — identical |

Identical to the frozen baseline in every axis.

## 4. Did `tmem_ffa` behaviour change?

**No.** Comparing the acceptance build directly against the frozen
`workspace/phase4-tmem-ffa/build/tmem_ffa.rebuilt.ko`:

| axis | result |
|---|---|
| functions / sizes / **bytes** | 141/141 identical |
| KCFI | 141/141 identical |
| imports / MODVERSIONs | identical |
| exports + CRCs | identical |
| strings | identical |
| module size | 151448 = 151448 |
| **first differing byte** | 68433 — inside `.note.gnu.build-id` |

```
frozen     b7c384437cf22f7d3f868fada0c4f28036783a2956fe7592d52693361445579e
acceptance 470c9c74bde417d2417053cf4560f73cf476ca214534e124ab661cd69b35c834
```

The **only** difference between the two modules is the GNU build-id, which is
a hash over the build inputs — and the build inputs legitimately changed (a
different symvers set was supplied). Every byte of code, data, relocation and
metadata is identical.

## 5. Provider provenance: before → after

| class | before | after |
|---|---:|---:|
| `GKI_NATURAL` | 59 | 59 |
| `FFA_V10_NATURAL` | 1 | 1 |
| `GZ_PROVIDER_STOCK_RUNTIME` | **9** | **0** |
| `GZ_TZ_SYSTEM_NATURAL` | **0** | **9** |
| `TKCORE_STOCK_RUNTIME` | 7 | 7 |
| total | 76 | 76 |

This is exactly the upgrade the task predicted. **Only provider provenance
improved** — no behaviour, no reconstruction status, no classification of
`tmem_ffa` changed.

## 6. Remaining stock-runtime dependency of `tmem_ffa`

7 `TEEC_*` edges on `tkcore`, which remains
`NO_PUBLIC_SOURCE_FOUND / PROVIDER_ABI_PARTIAL / NOT RECONSTRUCTED`. Of those
7, 3 are in tkcore's naturally-reproducible 14/25 set and 4 are in the
`PROVIDER_ABI_BLOCKED` 11/25 set. That boundary is untouched by this task.

## 7. Safety

The acceptance module was built and compared statically. It was never loaded,
GenieZone was never invoked, and no secure-memory API was called.
