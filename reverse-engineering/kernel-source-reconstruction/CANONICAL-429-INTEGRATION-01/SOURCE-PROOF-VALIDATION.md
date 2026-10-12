# Source-proof validation (re-checked, not taken from reports)

## Codex G-SOURCE-RECOVERY-BATCH-02 (aa212a88)

| Family | Repo commit (local HEAD, clean) | Bundle sha256 matches | Fresh clone tree == repo, fsck | Binaries in repo | B1/B2 A modules (normalized sha256 equal) | C rejects (MIXED-RESULTS) | ELF mutation entries per build |
|---|---|---|---|---|---|---|---|
| board_io | `3f61cb8a532d0a3b663d195b9fb8dd3f78c01bf6` | yes | yes | 0 | extdev_io_class, leds-rgb-aw2013, rt5133-regulator, spi-mt65xx, yft_gpio_keys | — | 68 PASS / 0 FAIL |
| camera_aux | `2a164f9ee0b8dbb42b3cff423f89ae3149c6cff8` | yes | yes | 0 | camera_eeprom_v4l2 | aw36515, aw36518, aw36518_v2: `REJECT_NOT_WAIVED`, strict exit 1 | 17 / 0 |
| biometric_transport | `157ab59523c594ac84f0f54af18b8999806e6618` | yes | yes | 0 | microarray_fp_tee | fingerprint, tkcore_drv: `REJECT_NOT_WAIVED` | 16 / 0 |

- **Raw differences:** each A module differs from stock only inside the 20-byte GNU build-ID window (19 or 20
  bytes).
- **Mutation count:** the logs hold 101 PASS entries per build (202 in total). Codex's summary cites 186; the
  difference is in how control cases are counted, and no entry is FAIL.

## Claude tmem_ffa (fork `android_kernel_modules_trustkernel_abi` 15e7e8d8)

- **B1/B2 (committed):** 9/9 strict PASS, 124/124 mutations each, 18 outputs and 57 intermediates identical.
- **New B3 (this integration):** a fresh `--no-hardlinks` clone of bundle `d2614b1e…` at
  `15e7e8d8d4f9cbf56982791b2fac0e54087d0f49` (tree `1d133097…`).
  - Build, verify and mutation all exit 0.
  - OUTPUT, INTERMEDIATE, CONFIG and joint-extra.symvers are byte-identical to B1.
  - `tmem_ffa` PASS; its only raw difference is the 20-byte build ID at 68432.

## Source references

All 47 source repositories referenced by A/B rows resolve, and each referenced commit exists locally (0
unresolved).
