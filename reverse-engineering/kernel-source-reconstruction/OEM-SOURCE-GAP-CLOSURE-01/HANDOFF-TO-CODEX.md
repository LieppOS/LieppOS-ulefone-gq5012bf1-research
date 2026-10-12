# Handoff to Codex G-SOURCE-RECOVERY-BATCH-02 (information only; nothing of Codex's was modified)

Your `biometric_transport-D3` provider-boundary errors include CRC mismatches on `tkcore.ko` exports: `__tee_get`,
`tee_core_add`, `tee_core_alloc`, `tee_core_del` and `tee_supp_cmd`. Those are exactly the `struct tee` closure
solved here.

## The declaration delta

In the public 7:2.2 `include/linux/tee_tkcore.h` (ff290548), remove the `uint16_t shm_name;` member from
`struct tee_shm`, and apply H1 (unprefixed GP `TEEC_*` aliases).

## Evidence it is correct

- All 25 stock `tkcore.ko` export CRCs come out naturally from genksyms.
- Stock code has no 16-bit access at `tee_shm+0x3c`, and its `tee_shm_alloc_from_rpc` takes 3 arguments.
- Compiling also requires removing the named-shm code. The consistent patch, using authentic 4.0p0 text, is
  `android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1:patches/source/0002-trustkernel-6.1.1-stock-evidenced-no-named-shm.patch`.
- Built provider `Module.symvers` = stock for all 25 exports.

## Notes

- **armtz:** `armtz/tee_tz_drv.c` (`tkcore_drv`, yours) also references `named_shm` in 7:2.2. Stock evidence for
  the armtz side was not examined here.
- **Missing compiled definitions:** your `MISSING_COMPILED_DEFINITION` entries (`tee_clkmgr_handle`,
  `tee_spi_transfer`) are build-scope matters, not affected by this change.
- **No ownership change:** none of `tkcore_drv`, `microarray_fp_tee` or `fingerprint` was claimed or built here.
