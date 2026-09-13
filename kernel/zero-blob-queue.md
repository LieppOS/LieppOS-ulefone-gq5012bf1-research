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
  **63/66 MODVERSION edges naturally regenerated, 3/66 inherited from real
  stock provider ABI witnesses (`mt_spi_enable_master_clk`,
  `mt_spi_disable_master_clk`, `tee_spi_transfer`), stock-compatible target
  66/66 exact**; `fingerprint` edges use the real source-built provider
  `Module.symvers`

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

- `tkcore_drv` — **RECONSTRUCTED / PROVIDER_ABI_PARTIAL**; SOURCE_RECONSTRUCTED;
  FROZEN FOR RE; stock oracle
  `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d` (63480 B).
  Pure consumer (0 exports). Real readable C in
  `//lieppos/tkcore-drv-recon` (4 .c + 4 .h: transports, `struct tee_ops`
  backend, RPC loop, per-CPU secure-call dispatcher, SHM pool, handle DB).
  **66/67 stock `__versions` entries reproduced with zero CRC mismatches and
  zero extra imports**; the single unreproduced import `alt_cb_patch_nops`
  (2 arm64 `ALTERNATIVE_CB` sites) is an allowlisted codegen artefact.
  Provider ABI split, never conflated: **6/13 `NATURAL`** (regenerated from C
  by `//lieppos/tkcore-recon`: `tee_map_cached_shm`, `tee_clkmgr_handle`,
  `tee_wait_queue_init/exit/sleep/wakeup`) and **7/13
  `STOCK_PROVIDER_WITNESS`** (`tee_core_alloc/add/del`, `__tee_get`,
  `tee_supp_cmd`, `ffa_driver_register/unregister`) read read-only from the
  stock provider `__kcrctab`/`__kcrctab_gpl`. The natural-evidence target
  reports those same 7 as `PROVIDER_ABI_GAP`. 34/34 fail-closed verifier
  (`kernel/scripts/phase4_tkcore_drv_verify.py`).
  See `kernel/phase4-tkcore-drv-reconstruction.md`.

## Active remaining queue

- `tkcore` — blocked on original TrustKernel headers only (no further binary
  analysis can unblock it); stays a stock vendor binary meanwhile
- connectivity and panel/provider work per remaining-module triage

Do not reopen frozen targets. Hynitron's stock provider remains stock
`yft_devinfo`; this queue does not mark yft_devinfo reconstructed.

`microarray_fp_tee` being frozen does **not** mark `spi-mt65xx` or `tkcore` as
reconstructed or source-pure. Those remain stock vendor binaries; only their
published export CRCs were read out of the shipped ELFs so the consumer can
link against them. Source purity of the consumer is a separate question from
source purity of those providers.

The `tkcore` work above upgrades one of those edges: `tee_spi_transfer` is no
longer "read out of the shipped ELF" — its prototype is now confirmed by the
stock KCFI type id `0xffeb18b3` and its CRC `0x184ce7da` is regenerated
naturally from C. The other 10 `tkcore_drv` / 4 `tmem_ffa` blocked edges are
not, and `tkcore` itself remains stock.

Likewise, `tkcore_drv` being reconstructed does **not** mark `tkcore` or
`ffa_v10` reconstructed or source-pure: 7 of its 13 provider edges are still
only available as stock ELF witnesses, and `ffa_v10` has not been analysed
beyond reading the two export CRCs it publishes. The stock load order
(`ffa_v10 → teeperf → tkcore → tkcore_drv`) is preserved.
