# MicroArray fingerprint TEE — MODVERSION ABI provenance split

This is the authoritative post-`spi-mt65xx`-closure provenance for the frozen
`microarray_fp_tee.ko` reconstruction. Consumer behavior was not reopened.

## Current acceptance result

- **66/66 stock MODVERSION edges exact**.
- **65/66 natural ABI edges** in the acceptance build.
- Of those, **2 are `NATURAL_SPI_PROVIDER`** edges from the real source-built
  `spi-mt65xx/Module.symvers`.
- **1/66 remains `STOCK_PROVIDER_WITNESS`** in the shippable acceptance build:
  `tee_spi_transfer` from stock runtime `tkcore`.
- Defined function set remains 27/27 exact and `depends` remains exactly
  `fingerprint,spi-mt65xx,tkcore`.

This is ABI provenance, not a claim that the whole fingerprint runtime stack
is source-pure. `tkcore` is still `NOT RECONSTRUCTED / STOCK RUNTIME PROVIDER`.
Separate tkcore ABI work has naturally regenerated the `tee_spi_transfer`
prototype/CRC as evidence, but it has not produced a shippable runtime tkcore.

## Per-provider split

### NATURAL — exact GKI and source-built providers

| group | edges | source of CRC |
|---|---:|---|
| exact-GKI kernel exports | 59 | `//common:kernel_aarch64` |
| `fingerprint` provider | 4 | real source-built `fingerprint/Module.symvers` |
| `spi-mt65xx` provider | 2 | real source-built `spi-mt65xx/Module.symvers` |
| total natural | **65** | real builds/genksyms |

The four fingerprint symbols remain:
`yft_waite_for_finger_dts_paser`, `yft_finger_set_reset`,
`yft_finger_set_spi_mode`, and `yft_finger_set_irq`.

The two newly natural SPI edges are:

| symbol | CRC | before | after |
|---|---|---|---|
| `mt_spi_enable_master_clk` | `0x1cc49782` | `STOCK_PROVIDER_WITNESS` | **`NATURAL_SPI_PROVIDER`** |
| `mt_spi_disable_master_clk` | `0xccc1e350` | `STOCK_PROVIDER_WITNESS` | **`NATURAL_SPI_PROVIDER`** |

They are emitted naturally by:
`//lieppos/spi-mt65xx:spi_mt65xx`, exact source revision
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`. The provider itself
uses no witness symvers or copied CRCs. See
`phase4-spi-mt65xx-reconstruction.md` and
`phase4-spi-mt65xx-export-abi.tsv`.

### Remaining stock runtime witness

| symbol | CRC | provider | reason |
|---|---|---|---|
| `tee_spi_transfer` | `0x184ce7da` | stock `tkcore` | acceptance build must retain the actual stock runtime provider; tkcore is not reconstructed |

Stock tkcore oracle SHA256:
`03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`.
The edge is extracted read-only from stock `__kcrctab`; it is never injected
into `spi-mt65xx`.

## Historical state

Before `spi-mt65xx` source closure, the MicroArray stock-compatible build had
**63 NATURAL + 3 STOCK_PROVIDER_WITNESS** edges. The two SPI witnesses above
were the only values changed in provenance; the MicroArray C, behavior,
function set, and TEE boundary were unchanged. Historical build artefacts
remain under `workspace/phase4-microarray-fp-tee/` and are not relabeled.

## Acceptance build

The post-closure package uses one MicroArray source file and these ABI inputs:

1. real source-built `fingerprint-recon/Module.symvers`;
2. real source-built `spi-mt65xx/Module.symvers`;
3. a one-line tkcore provider ABI record for the still-stock runtime edge.

```
tools/bazel build \
  //lieppos/microarray-fp-tee-recon-stockabi:microarray_fp_tee_recon_stockabi

python3 tools/phase4-microarray-fp-tee-verify.py \
  --stock workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/microarray_fp_tee.ko \
  --recon workspace/phase4-spi-mt65xx/acceptance/microarray_fp_tee.ko \
  --natural-provider workspace/phase4-spi-mt65xx/build/spi-mt65xx.ko \
  --provider workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/tkcore.ko \
  --allow-stock-provider-edges --accept-build-stamp-delta
```

Result: `PASS_WITH_DECLARED_DELTAS`, empty failures, 66/66 MODVERSIONs,
65 natural, 2 `NATURAL_PROVIDER`, 1 stock witness, exact function set and
exact dependencies. Build RC is zero with no compiler/modpost warnings and no
unresolved symbols. Evidence:
`workspace/phase4-spi-mt65xx/acceptance/verify.json`.

## Explicit boundaries

- No MicroArray ioctl, transfer, TEE, fingerprint glue, UUID, probe, or
  read/write behavior changed.
- No stock CRC was used to claim the source-built SPI provider reconstructed.
- No ELF was patched; no `KBUILD_MODPOST_WARN` or symbol laundering was used.
- Do not claim the fingerprint stack fully source-pure while runtime `tkcore`
  remains stock.
