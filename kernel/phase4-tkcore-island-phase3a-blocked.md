# GQ5012BF1 tkcore island Phase 3A — blocked report

## Classification

`TKCORE ISLAND PHASE 3A: BLOCKED`

This is a **scope/dependency blocker**, not missing stock evidence and not a compiler blocker.

## Mandatory gate that failed

Phase 6 requires all five core APIs to be at least `SEMANTIC_HIGH_CONFIDENCE` and explicitly says to stop if one remains incomplete. Stock `tee_core_add` and `tee_core_del` have mandatory direct dependencies on subsystems that the Phase-3A scope explicitly says not to implement:

- stop before SPI implementation work;
- stop before clock-manager implementation work;
- stop before procfs/logging completion.

The recovered stock edges are:

```text
tee_core_add
  -> tee_init_procfs                 # 0x7c64, 760 bytes
  -> tee_init_sysfs
  -> tee_peridev_init                # 0x951c, 28 bytes
       -> plat_register_spi_clk       # 0x9630, 296 bytes
            -> tee_clkmgr_register

tee_core_add error path
  -> tee_exit_procfs                 # 0x7f60, 140 bytes

tee_core_del
  -> tee_peridev_exit                # 0x953c, 168 bytes
  -> tee_cleanup_sysfs
  -> misc teardown
  -> tee_supp_deinit
```

`tee_init_procfs` is not incidental logging: it creates four proc objects, initializes log state, may request an IRQ, initializes a waitqueue, starts a kernel thread and contains complete unwind logic. `plat_register_spi_clk` scans up to 20 DT nodes/clocks and registers them with the TrustKernel clock manager. `tee_peridev_exit` drains clock-manager records under its mutex.

Therefore omitting these calls changes registration success/failure semantics and teardown ordering. Defining them as no-op functions returning success would be a **speculative success stub**, expressly forbidden by Phase 20. Importing the stock object or patching the ELF would violate the source-island and forbidden-technique rules.

## Additional direct-boundary concern

`tee_core_alloc` and `tee_core_free` directly use `tee_supp_init`/`tee_supp_deinit`. `tee_supp_deinit` is already byte-identical, but `tee_supp_init` remains donor-ported with a different call set and is part of the explicitly deferred supplicant/RPC family. This reinforces the need to define a narrow, explicit lifecycle-only exception before claiming the full core group closed.

## Useful oracle findings completed before stopping

- All five core target bodies were disassembled and documented in `phase4-tkcore-core-lifecycle.md`.
- Exact Phase-3A closure frozen: 9 targets + 17 direct helpers = 26 functions.
- `struct tee` corrections proven:
  - RPC pointer `@0xb0`
  - atomic refcount `@0xb8`
  - max refcount `@0xbc`
  - three 8-byte stats entries `@0xc0..0xd7`
- `tee_misc_dev`: 0x68 bytes, embedded miscdevice `@0`, descriptor `@0x50`, node `@0x58`.
- `tee_device_configs`: 3 × 0x28 bytes with exact mappings:
  - `tkcore_admin` → `tee_admin_fops`
  - `tkcore_client` → `tee_client_fops`
  - `tkcore_fp` → `tee_client_fops`
- `__tee_get` exact prototype is `int __tee_get(struct tee *)`, KCFI `0xa1200a70`; the provisional pointer-return declaration is wrong.
- Stock opaque-handle implementation recovered during closure analysis:
  - `tee_core_alloc_uuid`: `idr_preload(GFP_KERNEL)` → spin lock → `idr_alloc(idr, ptr, 1, 0, GFP_NOWAIT)` → unlock → `idr_preload_end`; positive handles start at 1.
  - `tee_core_uuid2ptr`: `idr_find`.
  - `tee_core_free_uuid`: `idr_remove`.
- These IDR helpers explain how stock safely stores context/session handles in 32-bit `fd` fields instead of the donor's explicitly broken 64-bit pointer-to-int cast.

## Source disposition

An exploratory implementation was **rejected** because it temporarily used success-returning placeholders at the excluded boundaries. No rejected source or stub is committed. The exact Phase-2 source snapshot was restored to:

`/home/armol/kernel-work/gki-12901745-workspace/lieppos/`

Post-restore checks:

- `//lieppos/tkcore-island:tkcore`: `BUILD_RC=0`, 0 compiler warnings, 0 errors, 0 unresolved symbols.
- `//lieppos/trustkernel-layout:tk_layout_probe`: `BUILD_RC=0`, 0 static assertion failures; 31/31 existing anchors preserved.
- Phase-2 verifier: **52/52 CHECKS PASSED**.
- Rebuilt SHA remains `5fc3c38dbfbd1eb90fec4b7d1ec803e4f09a7b576e8e8220f68f1b794a2e6e62`.

No runtime validation was performed.

## Required decision/evidence to unblock

No new binary evidence is needed for the dependency fact. One of these planning decisions is required:

1. **Recommended:** execute the directly required Phase-3E/3F leaf reconstruction first (`tee_init_procfs`, `tee_exit_procfs`, `tee_peridev_init`, `plat_register_spi_clk`, clock-manager registration/teardown), then rerun Phase 3A.
2. Explicitly expand Phase 3A to include those lifecycle leaves despite the original stop boundary.
3. Relax the acceptance rule to permit fail-closed/non-stock behavior—but then the allowed success classification cannot be used.

Do not proceed to Phase 3B shared memory from this blocked state. The next dependency-correct work is the narrow Phase-3E/3F prerequisite closure, not shared memory.

## Status

- TKCORE REPLACEMENT READY: **NO**
- STOCK TKCORE RUNTIME DEPENDENCY: **STILL PRESENT**
- Overall tkcore status: **NOT RECONSTRUCTED / PARTIAL / STOCK RUNTIME PROVIDER / NOT RUNTIME READY**
