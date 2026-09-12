# MicroArray fingerprint TEE — MODVERSION ABI provenance split

This report states, per symbol, where every CRC in the reconstructed
`microarray_fp_tee.ko` `__versions` table comes from. It is the authoritative
answer to "is this reconstruction source-pure?".

## Headline

- **63 / 66 MODVERSION edges are naturally regenerated** from C by genksyms in
  the exact-GKI build.
- **3 / 66 edges are inherited from real stock provider ABI witnesses.** They
  are **not** reconstructed naturally and must never be described as such.
- The stock-provider-compatible target reaches **66 / 66 exact** parity with
  the stock consumer.
- Source purity of `microarray_fp_tee` itself is a **separate question** from
  source purity of `spi-mt65xx` and `tkcore`. This project reconstructs the
  consumer only; the two vendor providers remain stock binaries and their
  internal source purity is out of scope and unclaimed.

## Why three CRCs cannot be regenerated

`modpost` copies a *kernel* export's CRC out of `Module.symvers`. It does not
recompute it. A *provider module's own* export CRCs are computed by `genksyms`
during **that provider's build**, from the type graph visible in **that
provider's headers**.

`spi-mt65xx.ko` and `tkcore.ko` are stock MediaTek/TrustKernel vendor modules.
Their export CRCs were produced against MediaTek vendor headers that the exact
GKI workspace does not contain.

### Control experiment (decisive)

MediaTek's verbatim upstream definition is

```c
void mt_spi_enable_master_clk(struct spi_device *spidev)
void mtk_spi_set_autosuspend_delay(struct spi_device *spi, int delay_ms)
```

Compiling `mtk_spi_set_autosuspend_delay` with that exact prototype in the
exact-GKI workspace yields CRC `0x063a223e`. The stock `spi-mt65xx.ko`
publishes `0xd3e99558` for the same symbol. The prototype is not in doubt, so
the divergence is in the provider-side type graph, not in our declaration.

Corroborating evidence that the workspace itself is correct:

| evidence | result |
|---|---|
| 59 GKI-exported imports of the stock consumer vs our GKI `Module.symvers` | **59/59 exact** |
| 4 `yft_*` imports vs the real source-built `fingerprint.ko` | **4/4 exact** |
| 16 candidate prototypes for `tee_spi_transfer` (`void*`/`u8*`/`const`/`u32`/`size_t`/extra arg/…) | none reproduce `0x184ce7da` |

`yft_*` reproduce because they are `int f(int)` — no vendor struct in the type
graph. The three failing symbols all reach MediaTek/TrustKernel vendor types.

## Per-symbol provenance

### NATURAL — 63 edges

All 59 GKI exports plus the four `fingerprint.ko` edges:

| symbol | CRC | source of CRC |
|---|---|---|
| `yft_waite_for_finger_dts_paser` | `0x4202702c` | real source-built `fingerprint.ko` |
| `yft_finger_set_reset` | `0xcae83e02` | real source-built `fingerprint.ko` |
| `yft_finger_set_spi_mode` | `0x0cf6e61a` | real source-built `fingerprint.ko` |
| `yft_finger_set_irq` | `0x6d125ec3` | real source-built `fingerprint.ko` |
| 59 further symbols (`spi_sync`, `spi_setup`, `_printk`, …) | see `phase4-microarray-fp-tee-modversions.tsv` | exact-GKI `//common:kernel_aarch64` |

The `fingerprint` edges continue to use the **real source-built** provider
`Module.symvers`; no witness or extracted record is used for them.

### STOCK_PROVIDER_WITNESS — 3 edges

| symbol | CRC | provider module | provider ELF sha256 | extraction |
|---|---|---|---|---|
| `mt_spi_enable_master_clk` | `0x1cc49782` | `spi-mt65xx` | `5463e06c205623e4b1b713416836e3b5235dc246c7d536595f6613ba3492d712` | `__kcrctab[+0x04]` via `__crc_mt_spi_enable_master_clk` |
| `mt_spi_disable_master_clk` | `0xccc1e350` | `spi-mt65xx` | `5463e06c205623e4b1b713416836e3b5235dc246c7d536595f6613ba3492d712` | `__kcrctab[+0x00]` via `__crc_mt_spi_disable_master_clk` |
| `tee_spi_transfer` | `0x184ce7da` | `tkcore` | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | `__kcrctab[+0x44]` via `__crc_tee_spi_transfer` |

Extraction method: `tools/phase4-extract-stock-provider-symvers.py` locates the
local `__crc_<symbol>` symbol, confirms its defining section is `__kcrctab`,
and reads the 32-bit CRC at that offset. It is read-only; the provider ELFs are
never modified. Output:
`workspace/phase4-microarray-fp-tee/stockabi/stock-provider.symvers`
with machine-generated provenance in `stock-provider.provenance.json`.

These three values are the ABI the stock providers themselves publish, and they
match the stock consumer's `__versions` table exactly. They are **inherited**,
not regenerated.

## What was explicitly NOT done

- No handwritten CRC literal appears anywhere in the reconstruction C.
- No ELF was patched or edited.
- No `__versions` section was hand-modified.
- No `KBUILD_MODPOST_WARN`, no `--allow-undefined`, no forced symbol resolution.
- No fake provider implementation was substituted for `tee_spi_transfer`; the
  TrustKernel call path is preserved, and no generic TEE API or direct SPI
  transfer was put in its place.
- The stock `tkcore`/`tkcore_drv` subsystem was not started, modified, or
  rebuilt.

The two build-only ABI witness modules
(`lieppos/spi-mt65xx-provider-abi`, `lieppos/tkcore-provider-abi`) exist solely
so `genksyms` derives the *natural* CRCs from C for the primary target. They
have empty bodies, are never installed, and are documented as non-loadable.

## Verifier classification

`tools/phase4-microarray-fp-tee-verify.py` emits one of:

| class | meaning |
|---|---|
| `NATURAL` | CRC regenerated from C in this build |
| `STOCK_PROVIDER_WITNESS` | CRC inherited from a named stock provider ELF, with that ELF's sha256 recorded |
| `PROVIDER_ABI_GAP` | natural target: CRC differs from stock because the provider CRC is non-regenerable |
| `MISMATCH` / `MISSING` / `EXTRA` | genuine defect, always fatal |

The verifier fails closed: any `MISMATCH`, `MISSING`, `EXTRA`, function-set
divergence, unwitnessed inherited edge, or unexpected modinfo delta is a
non-zero exit. It refuses to accept an inherited edge unless the CRC is
actually found in a supplied provider ELF.
