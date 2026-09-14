# Phase 3F — microarray_fp_tee final-provider acceptance

Result: **PASS_STATIC_FINAL_TKCORE_PROVIDER**

## Build

- Target: `//lieppos/microarray-fp-tee-phase3f:microarray_fp_tee_phase3f`
- SHA-256: `2c002adba4eeff73997b025757089158df2acbf1668d50c821b6b64665c6bada`, size 69688
- RC / compiler warnings / compiler errors / modpost warnings / unresolved: **0 / 0 / 0 / 0 / 0**
- `depends=fingerprint,spi-mt65xx,tkcore`
- Stock tkcore witness: **0** — the historical `tkcore-provider.symvers` record (the single line `0x184ce7da tee_spi_transfer tkcore EXPORT_SYMBOL`) is **absent** from this package.

`microarray_fp_tee.c` is a symlink to the frozen reconstruction. Not one byte of driver source changed.

## The tkcore edge

| Field | Value |
|---|---|
| Symbol | `tee_spi_transfer` |
| Historical stock CRC | `0x184ce7da` |
| Phase-3E provider CRC | `0x184ce7da` |
| Phase-3F consumer CRC | `0x184ce7da` |
| Stock KCFI | `0xffeb18b3` (provider-side, reproduced in Phase 3D) |
| Classification | **NATURAL_HISTORICAL_STOCK_CRC** |

This was expected but is now **measured**: the final provider satisfies the frozen consumer with the exact historical value, with the stock record removed from the build.

### Declaration divergence, resolved without editing frozen source

The frozen `microarray_fp_tee.c` carries its own inline declaration:

```c
extern int tee_spi_transfer(void *conf, int conf_size, const char *txbuf,
                            char *rxbuf, int len);
```

The authority `trustkernel/tee_spi.h` spells it `(void *, uint32_t, void *, void *, uint32_t)`. §14 forbids auto-editing a frozen consumer's historical local copy, and this declaration lives in the `.c` itself, so no include-path override could reach it without a source edit. It was therefore **kept**, and equivalence proven instead:

- AArch64 AAPCS passes `int` and `uint32_t` identically in a 32-bit `w` register; `const char *`, `char *` and `void *` identically in a 64-bit `x` register; the `int` return in `w0`.
- All five call sites are `R_AARCH64_CALL26` **direct** calls, so KCFI type ids are not consulted at the callsite.
- The emitted code is byte-identical to the frozen accepted reconstruction (below), which is the decisive empirical proof.
- The `__versions` CRC is supplied by the provider record, and equals the historical value.

## Behavior preservation

Against the frozen accepted reconstruction `microarray_fp_tee.recon-stockabi.ko`:

| Property | Result |
|---|---|
| Functions | 27/27, set equal |
| Function bytes | **27/27 identical** |
| KCFI differences | **0** |
| Relocations | exactly equal |
| Objects changed | **0** (including `____versions`) |
| Import names | 66/66 equal |
| Import CRC changes | **0** |
| Section sizes | no differences |
| vermagic / depends | identical |
| `init_connect.smt_conf` ioctl/config object | identical |

The **five probe-time `tee_spi_transfer` call sites are preserved exactly**, all owned by `init_connect`, at offsets `0x478`, `0x4a0`, `0x514`, `0x53c`, `0x584`, all `R_AARCH64_CALL26`.

The only residual file-level delta is the ELF build-id/signature block, which changes on any rebuild.

## Complete provider provenance

| Provider | Edges | Natural |
|---|---:|---:|
| exact GKI ab/12901745 | 59 | 59 |
| tkcore (final Phase-3E) | 1 | **1** |
| fingerprint (real source-built) | 4 | **4** |
| spi-mt65xx (real source-built) | 2 | **2** |
| **Total** | **66** | **66** |

- fingerprint: `yft_finger_set_irq` `0x6d125ec3`, `yft_finger_set_reset` `0xcae83e02`, `yft_finger_set_spi_mode` `0x0cf6e61a`, `yft_waite_for_finger_dts_paser` `0x4202702c` — **NATURAL**
- spi-mt65xx: `mt_spi_disable_master_clk` `0xccc1e350`, `mt_spi_enable_master_clk` `0x1cc49782` — **NATURAL**

The former stock-runtime tkcore witness has disappeared.

Runtime/device operations: **0**.
