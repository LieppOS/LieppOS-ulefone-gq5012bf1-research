# ZERO-BLOB stock-oracle queue

## Frozen/source-ready

- `yft_gpio_keys` — FROZEN FOR RE
- `leds_ln2403` — FROZEN FOR RE
- `yft_tiny2c_usb` — FROZEN FOR RE
- `hynitron` — **STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**;
  SOURCE_RECONSTRUCTED; SOURCE_NOW; FROZEN FOR RE; 34/34 verifier; stock
  `yft_devinfo` provider ABI pinned; both `spi_tiny_co5300_lcd` consumer edges
  READY/EXACT
- `spi_tiny_co5300_lcd` — **NO_PUBLIC_SOURCE_FOUND /
  STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**; SOURCE_RECONSTRUCTED; SOURCE_NOW;
  FROZEN FOR RE; exact 25-function/58-MODVERSION sets; exact rebuilt-Hynitron
  and stock-YFT provider edges; 30/30 verifier
- `microarray_fp_tee` — **NO_USEFUL_SOURCE / EMPTY-SOURCE RED /
  BEHAVIORALLY-COMPLETE, LOAD-COMPATIBLE, WITH DECLARED ABI PROVENANCE SPLIT**;
  FROZEN FOR RE; 27/27 functions; complete ioctl/UAPI/TEE/DT closure;
  **post-SPI closure: 65/66 natural ABI edges, including both
  `NATURAL_SPI_PROVIDER` edges; one stock-runtime tkcore witness
  (`tee_spi_transfer`); acceptance target 66/66 exact**
- `spi-mt65xx` — **DIRECT_SOURCE_MATCH / FROZEN FOR RE**; exact pinned Nothing
  MT6878 MediaTek source; 31/31 function bytes and KCFI exact, 65/65 imports,
  66/66 MODVERSIONs, all 3 export CRCs natural, sole MicroArray consumer
  accepted, clean exact-GKI build, 82/82 verifier

- `tkcore` — **NO_PUBLIC_SOURCE_FOUND / PROVIDER_ABI_PARTIAL — NOT
  RECONSTRUCTED**; stock oracle frozen and fully inventoried (122 functions,
  25 exports, 101 MODVERSIONs, 3098 relocations); **14/25 export CRCs +
  KCFI type ids naturally regenerated** against exact GKI 12901745 by
  `//lieppos/tkcore-recon` (build-only ABI witness, never loadable);
  **11/25 declared `PROVIDER_ABI_BLOCKED`** because their genksyms CRCs expand
  TrustKernel's private `struct tee` / `struct tee_context` member names, which
  exist in no binary and no public source; 36/36 fail-closed verifier.
  See `kernel/phase4-tkcore-provider-abi.md`,
  `kernel/phase4-tkcore-stock-inventory.md`,
  `kernel/phase4-tkcore-source-candidates.md`.

- `tkcore_drv` — **SOURCE_RECONSTRUCTED / SOURCE_NOW_WITH_PROVIDER_WITNESSES /
  PROVIDER_ABI_PARTIAL**; **FROZEN FOR RE**; stock oracle
  `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d` (63480 B).
  Pure consumer (0 exports). Real readable C in
  `//lieppos/tkcore-drv-recon` (4 .c + 4 .h: transports, `struct tee_ops`
  backend, RPC loop, per-CPU secure-call dispatcher, SHM pool, handle DB).
  **66/67 stock `__versions` entries reproduced with zero CRC mismatches and
  zero extra imports**; the single unreproduced import `alt_cb_patch_nops`
  (2 arm64 `ALTERNATIVE_CB` sites) is an allowlisted codegen artefact.
  **Current provider ABI split (post-2026-09-13 `ffa_v10` closure), never
  conflated: 8/13 `NATURAL`** (6 tkcore edges regenerated from C by
  `//lieppos/tkcore-recon` — `tee_map_cached_shm`, `tee_clkmgr_handle`,
  `tee_wait_queue_init/exit/sleep/wakeup` — plus 2 `NATURAL_FFA` edges,
  `ffa_driver_register`/`ffa_driver_unregister`, regenerated from C by the now
  source-closed `//lieppos/ffa-v10` provider) and **5/13
  `STOCK_PROVIDER_WITNESS`** (`tee_core_alloc/add/del`, `__tee_get`,
  `tee_supp_cmd` — all tkcore, read read-only from the stock provider
  `__kcrctab`). The natural-evidence target reports those same 5 as
  `PROVIDER_ABI_GAP`. **50/50 functions by name** (17 byte-identical, 24
  size-identical) and **20/21 Clang kCFI type ids equal stock**, which proves
  the prototypes — including TrustKernel's struct tag names
  `tee`/`tee_session`/`tee_cmd`/`tee_shm` — are spelled exactly as stock
  spelled them. The 21st (`run_tee_task`) is a declared residual: its arity and
  argument roles are proven from the stock call sites, but 3,690 candidate
  spellings of its two private parameter struct tag names hashed to zero hits.
  **43/43 fail-closed verifier** (`kernel/scripts/phase4_tkcore_drv_verify.py`),
  verdict `PASS_WITH_DECLARED_PROVIDER_WITNESSES`. The rebuilt `.ko` is
  byte-identical to the pre-`ffa_v10`-closure build — behavior was not
  reopened, only ABI provenance improved.
  See `kernel/phase4-tkcore-drv-reconstruction.md`.

  *(Historical, pre-`ffa_v10`-closure result: 6/13 `NATURAL`, 7/13
  `STOCK_PROVIDER_WITNESS` including both `ffa_driver_*` edges, 37/37
  verifier.)*

## Active remaining queue

- `tkcore` — blocked on original TrustKernel headers only (no further binary
  analysis can unblock it); stays a stock vendor binary meanwhile
- connectivity and panel/provider work per remaining-module triage

Do not reopen frozen targets. Hynitron's stock provider remains stock
`yft_devinfo`; this queue does not mark yft_devinfo reconstructed.

`spi-mt65xx` is now independently source-closed and shippable. Both of its
MicroArray edges are natural. This does **not** mark `tkcore` reconstructed or
the full fingerprint runtime stack source-pure: runtime `tkcore` remains the
stock vendor binary. Source purity of the consumer is separate from that
remaining provider boundary.

The `tkcore` work above upgrades one of those edges: `tee_spi_transfer` is no
longer "read out of the shipped ELF" — its prototype is now confirmed by the
stock KCFI type id `0xffeb18b3` and its CRC `0x184ce7da` is regenerated
naturally from C. The other 10 `tkcore_drv` / 4 `tmem_ffa` blocked edges are
not, and `tkcore` itself remains stock.

Likewise, `tkcore_drv` being reconstructed does **not** mark `tkcore`
reconstructed or source-pure: 5 of its 13 provider edges are still only
available as stock ELF witnesses (all five are TrustKernel's private-type
blockers). The stock load order (`ffa_v10 → teeperf → tkcore → tkcore_drv`)
is preserved.

- `ffa_v10` — **DIRECT_SOURCE_MATCH**; **FROZEN FOR RE**; stock oracle
  `2f8341d3f920418f3d9f4b8f64299acf97e591ad232a6bbbf6298b63231eebde`
  (38688 B). Exact MediaTek vendor copy of the upstream Linux FF-A transport
  found verbatim in the pinned Nothing MT6878 tree
  (`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`,
  `drivers/misc/mediatek/trusted_mem/ffa_v10/`), dated to the
  android14-6.1 v6.1.34–v6.1.56 window by reverting three stable commits from
  the current GKI copy (mandatory RED performed first: pristine current-GKI
  donor built unmodified, 5/5 export CRCs matched but only 30/34 functions
  byte-identical; root-caused and then the exact vendor snapshot located).
  Built unmodified against exact GKI 12901745: **34/34 functions
  byte-identical**, **40/40 kernel imports + 41/41 MODVERSION CRCs
  identical**, **34/34 kCFI type ids identical**, and **all 5/5 export CRCs
  regenerated NATURALLY by genksyms — no witness, no CRC injection, no ELF
  patch, no `KBUILD_MODPOST_WARN`** — including both hard-gate symbols
  `ffa_driver_register` (`0x0d53cde9`) and `ffa_driver_unregister`
  (`0x3c660e4c`). All 471 stock modules were scanned for consumers: three
  found (`tkcore_drv`, `tmem_ffa`, and a newly discovered third,
  `gz_main_mod`), all three accept the rebuilt provider. `tkcore_drv`'s
  stock-ABI target was rebuilt against the real provider and is
  byte-identical to its pre-closure build (behavior not reopened); its
  provenance split moved from 6 NATURAL/7 STOCK_PROVIDER_WITNESS to **8
  NATURAL/5 STOCK_PROVIDER_WITNESS**, verifier 43/43 (was 37/37).
  49/49 fail-closed verifier (`kernel/scripts/phase4_ffa_v10_verify.py`).
  See `kernel/phase4-ffa-v10-reconstruction.md`.

Do not mark `tkcore` reconstructed because `ffa_v10` closed: `tkcore` remains
`PROVIDER_ABI_PARTIAL / NOT RECONSTRUCTED / STOCK RUNTIME PROVIDER`, blocked
on original TrustKernel private headers. It was not reopened by the `ffa_v10`
task.
