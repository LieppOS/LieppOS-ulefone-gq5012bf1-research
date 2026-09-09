# Stock MicroArray consumer boundary

## Scope

This document analyzes stock `microarray_fp_tee.ko` only far enough to close its
dependency on stock `fingerprint.ko`. It does not reconstruct or modify the
MicroArray, TrustKernel, or SPI-controller drivers.

Oracle: `workspace/phase4-fingerprint/oracle/microarray_fp_tee.stock.ko`

- SHA256: `8e1449cea5d07ef663d368ce5eea27e8c879a9cd70d39f8fc2b5b25445c2cf33`
- size: 69,296 bytes
- stock provider dependency: `/lib/modules/fingerprint.ko`

## Imported fingerprint symbols

| symbol | consumer MODVERSION CRC | relocation calls | provider KCFI | proven argument(s) | result handling |
|---|---:|---:|---:|---|---|
| `yft_finger_set_reset` | `0xcae83e02` | 1 | `0x00050794` | constant `1` | ignored; next call is unconditional |
| `yft_finger_set_spi_mode` | `0x0cf6e61a` | 2 | `0x00050794` | constant `1` at both sites | ignored; execution continues unconditionally |
| `yft_finger_set_irq` | `0x6d125ec3` | 1 | `0x00050794` | constant `1` | ignored; consumer returns its own saved status |
| `yft_waite_for_finger_dts_paser` | `0x4202702c` | 1 | `0xa540670c` | no arguments | ignored; GPIO/power setup follows unconditionally |

No other `yft_*` symbol is imported by this stock consumer. The provider's six
other exports are public ABI but are not stock-MicroArray edges.

The three setter exports share one KCFI type. The wait export shares the
`void(void)` KCFI type with stock `yft_finger_power_deinit`. Disassembly and
natural CRC reproduction are used in the reconstruction to fix the exact C
prototypes; no CRC is patched.

## Call sites

| consumer function | `.text` call relocation | call | argument | handling and sequencing |
|---|---:|---|---:|---|
| `mas_probe` | `0x724` | `yft_waite_for_finger_dts_paser()` | none | return register is not tested; immediately calls `mas_finger_set_gpio_info(spi, 1)` |
| `mas_finger_set_gpio_info` | `0x1b4` | `yft_finger_set_reset(1)` | 1 | ignored |
| `mas_finger_set_gpio_info` | `0x1bc` | `yft_finger_set_spi_mode(1)` | 1 | ignored; follows reset call |
| `mas_finger_set_gpio_info` | `0x1c4` | `yft_finger_set_irq(1)` | 1 | ignored; follows SPI-mode call |
| `mas_sync` | `0x330` | `yft_finger_set_spi_mode(1)` | 1 | ignored; then takes the consumer mutex and performs its SPI path |

The three board-control calls in `mas_finger_set_gpio_info` happen only after
the consumer has obtained and enabled its `vmch` regulator. If regulator
setup fails, the consumer skips to the same tail at `0x1b0`; therefore the
stock consumer still issues all three board-control calls and returns its own
saved error/status value.

## Context / sleepability

- `mas_probe` is the SPI driver's probe path and runs in process context.
- Its direct `mas_finger_set_gpio_info` call is therefore sleepable.
- The second SPI-mode call is reached from `mas_read` through `mas_sync`, hence
  from a userspace read syscall in process context; `mas_read` checks the
  result of `mas_sync`, but `mas_sync` does not check any result from the YFT
  setter.
- No stock fingerprint-provider call is made by the MicroArray IRQ handler.
- Thus every proven stock consumer edge is sleepable; none is an atomic/IRQ
  call site.

## Proven sequencing graph

```text
microarray SPI probe (`mas_probe`)
  -> yft_waite_for_finger_dts_paser()       [return ignored]
  -> mas_finger_set_gpio_info(spi, 1)
       -> acquire/configure/enable `vmch`
       -> yft_finger_set_reset(1)            [return ignored]
       -> yft_finger_set_spi_mode(1)         [return ignored]
       -> yft_finger_set_irq(1)              [return ignored]
  -> consumer obtains IRQ and registers its own threaded handler
  -> consumer configures IRQ wake
  -> consumer/TEE/SPI setup

userspace read (`mas_read`)
  -> mas_sync(...)
       -> yft_finger_set_spi_mode(1)         [return ignored]
       -> consumer mutex/SPI transfer path
```

Only edges shown above are claimed. In particular, Linux IRQ registration,
`disable_irq`, `irq_set_irq_wake`, and the interrupt handler all belong to
`microarray_fp_tee.ko`, not `fingerprint.ko`.

## Evidence

- `workspace/phase4-fingerprint/consumer-inventory/microarray-imports.tsv`
- `workspace/phase4-fingerprint/consumer-inventory/microarray-modversions.tsv`
- `workspace/phase4-fingerprint/consumer-inventory/microarray-relocations.tsv`
- `workspace/phase4-fingerprint/consumer-inventory/disassembly.text.txt`
- call relocations: `.text+0x1b4`, `+0x1bc`, `+0x1c4`, `+0x330`, `+0x724`
