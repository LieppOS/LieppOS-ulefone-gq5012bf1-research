# GQ5012BF1 tkcore island — Phase 2 result

**Classification: `TKCORE_ISLAND_PHASE2_COMPILE_COMPARE_PASS`**

**TKCORE REPLACEMENT READY: NO.
STOCK TKCORE RUNTIME DEPENDENCY: STILL PRESENT.
RUNTIME VALIDATION: NOT PERFORMED.**

Static/offline only. No module loaded, no device node opened, no TEEC command
issued, no secure world contacted.

Verifier: `kernel/scripts/phase4_tkcore_island_phase2_verify.py` — **52/52
CHECKS PASSED**, certifying `PHASE2_COMPILE_AND_COMPARE_COMPLETE` only.

---

## 1. What Phase 2 achieved

The reconstructed tkcore source now **compiles cleanly** against exact GKI
ab/12901745 and produces the first comparable ELF.

| metric | result |
|---|---|
| initial errors | **330** (frozen in `phase2/before/build.log`) |
| final BUILD_RC | **0** |
| compiler warnings | **0** |
| modpost warnings | **0** |
| unresolved symbols | **0** |
| vendor-module dependencies added | **0** (`depends:` empty, as in stock) |
| port deltas applied | **23**, all ledgered |

286 of the 330 errors collapsed to a single root cause: `_DEV()` expanded to
`tee->miscdev.this_device`, but TrustKernel has no inline `miscdevice`.

## 2. The structural finding that matters

The ELF independently confirms the previously *estimated* donor coverage:

**67 of 122 stock functions are present in the rebuilt module — exactly the
67 predicted by name-set intersection before the build existed.**

And a genuinely strong result:

| parity class | count |
|---|---:|
| **EXACT_BYTE** (identical machine code to stock) | **16** |
| SIZE_IDENTICAL | 5 |
| DONOR_PORTED (present, differing code) | 46 |
| MISSING (not yet reconstructed) | 55 |
| EXTRA (donor-only, absent from stock) | 16 |

The 16 byte-identical functions include the **entire wait-queue subsystem**
(`tee_wait_queue_init`, `tee_wait_queue_exit`, `tee_wait_queue_get`), plus
`tee_context_destroy`, `tee_context_copy_from_client`, `tee_core_free`,
`tee_inc_stats`, `tee_dec_stats`, `tee_copy_from_user`, `tee_copy_to_user`,
`tee_supp_deinit`, `tee_plt_device_release`, `tee_show_state`, and the
`conf_show` / `name_show` / `type_show` sysfs handlers.

Sixteen functions compiling to the *exact* machine code of the stock
TrustKernel binary is independent proof that the donor lineage, the
reconstructed type graph and the compiler configuration are all correct.

## 3. KCFI — the new prototype oracle

| KCFI state | count |
|---|---:|
| **EXACT** | **60** |
| MISMATCH | 7 |
| STOCK_ONLY (not yet built) | 55 |
| REBUILT_ONLY (donor-only) | 16 |

**60 of the 67 shared functions carry a byte-identical KCFI type id**, which
means 60 reconstructed prototypes are provably identical to stock. The 7
mismatches are the precise, bounded list of prototypes that still need work
and are recorded in `phase4-tkcore-island-phase2-kcfi.tsv`.

## 4. GKI ABI contract

| metric | stock | rebuilt |
|---|---:|---:|
| undefined imports | 100 | 61 |
| shared | — | 57 |
| missing | — | 43 |
| extra | — | 4 |
| **shared imports with matching MODVERSION CRC** | — | **57 / 57** |

Every single shared GKI import CRC matches. The 43 missing imports belong to
the 55 unreconstructed functions. The 4 extra imports are explained:

* `sg_nents` — stock **defines its own local copy** rather than importing it
* `strncmp`, `kstrtoull`, `_dev_err` — stock neither defines nor imports
  these, i.e. stock does not use them; they arrive from donor code paths
  (stock logs via `pr_*`, not `dev_*`)

None of the four is a vendor-module dependency.

## 5. Exports

| metric | count |
|---|---:|
| stock exports | 25 |
| rebuilt exports | 17 |
| shared | 17 |
| **fabricated** | **0** |

The 8 absent exports are exactly the unreconstructed subsystems:
`__tee_get`, `tee_clkmgr_handle`, `tee_clkmgr_register`, `tee_map_cached_shm`,
`tee_unmap_cached_shm`, `tee_spi_cfg_padsel`, `tee_spi_transfer`,
`tee_spi_transfer_disable`.

They are **marked missing, not faked**. No export was emitted that stock does
not have.

Historical CRC comparison is deliberately **not** performed in this phase: 8
of the 25 exports do not exist yet, so an export-CRC verdict would be
premature and is deferred to the acceptance phase.

## 6. Type graph preserved

The compiler-verified type graph was **not weakened** to achieve the build.
`//lieppos/trustkernel-layout:tk_layout_probe` still passes, and all **31
layout anchors** were re-measured with actual values:

`struct tee` 0x138 · `struct tee_context` 0xd0 · `TEEC_Context` 0x108 ·
`TEEC_Session` 0x8 · `TEEC_SharedMemory` 0x28 · `TEEC_Operation` 0x118 ·
`TEEC_UUID` 0x10 · `tee_wait_queue_private` 0x40, plus all 23 field offsets.

The one structural conflict (donor's inline `miscdevice` vs TrustKernel's
`list_misc` @0x0a0) was resolved by **adding** an island-private
`struct tee_misc_dev` record, not by altering `struct tee`.

## 7. Two evidence-driven deletions

* **debugfs**: the donor's debugfs unit was removed because stock tkcore
  imports **no debugfs symbol at all** (`llvm-nm -u` on the frozen oracle).
  Stock's trace surface is the 6 procfs functions in the closure matrix.
  `debugfs_initialized` is also absent from the trimmed GKI symbol list.
* **`MODULE_SUPPORTED_DEVICE`**: removed from Linux in v5.13; emitted nothing.

`MODULE_IMPORT_NS(DMA_BUF)` was *added* because stock declares exactly
`import_ns=DMA_BUF` and imports the same 8 `dma_buf_*` symbols.

## 8. Forbidden-technique audit

| technique | status |
|---|---|
| CRC injection | not used |
| `__versions` editing | not used |
| ELF / binary patching | not used |
| `KBUILD_MODPOST_WARN` | not used |
| fake `Module.symvers` | not used |
| stock provider witness for tkcore | not used |
| `-Wno-*` suppression | not used |
| speculative stubs returning success | not used |
| deleting code because it was hard to port | not done (both deletions are evidence-backed) |
| changing a verified layout | not done (probe still passes) |

## 9. What remains

**55 functions** across 8 subsystems, queued in
`kernel/phase4-tkcore-island-phase3-work-queue.md`:

shared memory 12 · platform 10 · procfs 6 · core 5 · log 5 · compat 4 ·
helper 4 · spi 3 · clkmgr 2 · session 2 · supplicant 2

Consumer acceptance builds (`tkcore_drv`, `tmem_ffa`, `microarray_fp_tee`)
were **not** run and must not be until the 8 missing exports exist.

**TKCORE ISLAND PHASE 2: COMPILE + COMPARE PASS**
