# `yft_finger_set_spi_mode` contract

Prototype and ABI:

```c
int yft_finger_set_spi_mode(int mode); /* CRC 0x0cf6e61a, KCFI 0x00050794 */
```

“SPI mode” here means four-pin pinmux selection. It is not CPOL/CPHA mode
0/1/2/3, controller configuration, clock gating, or a standalone CS toggle.

## Exact mapping and order

| mode | selection order |
|---:|---|
| 0 | CLK GPIO -> CS GPIO -> MI GPIO -> MO GPIO |
| 1 | CLK SPI -> CS SPI -> MI SPI -> MO SPI |
| other | no selections; return 0 |

GPIO mode drives the DT-defined GPIO configurations (each has `output-low`).
SPI mode selects MT6878 alternate function 2 on pins 60/61/63/62 for
CLK/CS/MI/MO respectively.

Before dispatch, the function validates all eight state pointers in this exact
category order: CLK GPIO, CS GPIO, MI GPIO, MO GPIO, CLK SPI, CS SPI, MI SPI,
MO SPI. Any `ERR_PTR` prints the stock reset-style error string and returns
literal `-1`. Once validation succeeds, every `pinctrl_select_state()` return
is ignored; the sequence is not aborted and the export returns 0. There is no
lock, rollback, delay, or state variable.

## Stock consumer

`microarray_fp_tee.ko` calls only mode 1:

1. `.text+0x1bc` from `mas_finger_set_gpio_info`, between reset-high and IRQ
   pull-up selection;
2. `.text+0x330` from `mas_sync`, reached by `mas_read` before the consumer's
   mutex/SPI path.

Both returns are ignored. No stock consumer call to mode 0 was found.
