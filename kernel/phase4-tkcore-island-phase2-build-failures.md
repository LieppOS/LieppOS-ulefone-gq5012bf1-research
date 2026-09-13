# GQ5012BF1 tkcore island — Phase 2 build-failure analysis

Frozen pre-fix log: `workspace/phase4-tkcore-island/phase2/before/build.log`
(2710 lines, captured with `-ferror-limit=0` so nothing was truncated; that
flag was measurement-only and was removed before the final build).

**330 compiler errors**, 0 warnings, across 6 translation units.

## 1. Errors by file

| file | errors |
|---|---:|
| tee_shm.c | 110 |
| tee_session.c | 104 |
| tee_core.c | 83 |
| tee_context.c | 24 |
| tee_sysfs.c | 8 |
| tee_kernel_api.c | 1 |

## 2. Errors by message class

| count | message class |
|---:|---|
| 151 | incompatible integer to pointer conversion `[-Wint-conversion]` |
| 135 | call to undeclared function `[-Wimplicit-function-declaration]` |
| 24 | no member named `miscdev` in `struct tee` |
| 3 | incompatible pointer types `refcount_t *` vs `const atomic_t *` |
| 2 | address of array always true `[-Wpointer-bool-conversion]` |
| 2 | incompatible function pointer types initializing |
| 3 | field designator does not refer to any field in `struct dma_buf_ops` |
| 1 | `sprintf` will always overflow `[-Wfortify-source]` |
| 1 | cast to `void *` from smaller integer type |
| 1 | comparison of distinct pointer types |
| 4 | implicit int / missing prototype / expected declarator |
| 3 | assorted int-to-pointer assignment |

The two dominant classes are not independent: `_DEV` was undeclared (131
call sites), so every `_DEV(tee)` returned implicit `int`, which then failed
to convert to the `const struct device *` parameter of `dev_err`/`dev_dbg`.
**286 of the 330 errors collapse to one root cause.**

## 3. Distinct root causes

| id | root cause | file(s) | kernel API | classification |
|---|---|---|---|---|
| RC1 | `_DEV(tee)` expanded to `tee->miscdev.this_device`; `struct tee` has no inline `miscdev` because TrustKernel links misc devices through `list_misc` @0x0a0 | all | `struct miscdevice`, `misc_register` | TYPE_GRAPH_CONFLICT (donor vs stock structure, resolved without changing any verified layout) |
| RC2 | `miscdev` member referenced directly (25 sites) | tee_core.c, tee_sysfs.c, tee_debugfs.c | miscdevice | TYPE_GRAPH_CONFLICT |
| RC3 | `atomic_read(&ctx->refcount.refcount)` — `kref::refcount` became `refcount_t` in Linux 4.11 | tee_context.c | `kref_read` | MECHANICAL_6_1_PORT |
| RC4 | `dma_buf_ops::kmap` / `kmap_atomic` / `kunmap` removed in Linux 5.6 | tee_shm.c | dma-buf | MECHANICAL_6_1_PORT |
| RC5 | `dma_buf_ops::attach` lost its `struct device *` parameter in Linux 5.0 | tee_shm.c | dma-buf | MECHANICAL_6_1_PORT |
| RC6 | `MODULE_SUPPORTED_DEVICE` removed in Linux 5.13 | tee_core.c | module.h | MECHANICAL_6_1_PORT |
| RC7 | `compat_ptr` used without `<linux/compat.h>` | tee_core.c | compat | BUILD_HARNESS |
| RC8 | `IS_ERR_VALUE` applied to an `int` | tee_shm.c | err.h | MECHANICAL_6_1_PORT |
| RC9 | `_UUID_STR_SIZE` 35 vs the 37 bytes a UUID string needs | tee_session.c | fortify | MECHANICAL_6_1_PORT (genuine donor buffer overflow) |
| RC10 | `-Wpointer-bool-conversion` on two array-address truth tests | tee_kernel_api.c, tee_session.c | clang | MECHANICAL_6_1_PORT |

## 4. Second-stage failures (surfaced only after the 330 were cleared)

| id | root cause | classification | resolution |
|---|---|---|---|
| RC11 | modpost: 8 `dma_buf_*` symbols used from namespace DMA_BUF without importing it | VENDOR_API_DRIFT | `MODULE_IMPORT_NS(DMA_BUF)` — stock `.modinfo` declares exactly `import_ns=DMA_BUF` and imports the same 8 symbols |
| RC12 | modpost: `debugfs_initialized` undefined | VENDOR_API_DRIFT | `EXPORT_SYMBOL_GPL` in source but **absent from the trimmed GKI symbol list**. Stock tkcore imports **no debugfs symbol at all**, so the donor debugfs unit was removed as an evidence-driven deletion, not a convenience one |

## 5. Classification summary

| classification | root causes |
|---|---:|
| MECHANICAL_6_1_PORT | 7 |
| TYPE_GRAPH_CONFLICT | 2 |
| VENDOR_API_DRIFT | 2 |
| BUILD_HARNESS | 1 |
| MISSING_BEHAVIOR | 0 |
| UNKNOWN | 0 |

**No failure required inventing TrustKernel behavior, and none required
changing a compiler-verified layout.** The two TYPE_GRAPH_CONFLICT items were
resolved by adding an island-private `struct tee_misc_dev` record that links
through the already-PROVEN `list_misc` member, leaving `struct tee` at 0x138.
