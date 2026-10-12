# `yft_finger_set_reset` contract

Prototype and ABI:

```c
int yft_finger_set_reset(int value); /* CRC 0xcae83e02, KCFI 0x00050794 */
```

## Mapping

| value | action | electrical meaning |
|---:|---|---|
| 0 | select `finger_reset_en0` / `yft_finger_reset_low` | GPIO30 mode 0, output-low |
| 1 | select `finger_reset_en1` / `yft_finger_reset_high` | GPIO30 mode 0, output-high |
| other | no action | accepted no-op |

The naming and DT establish active-high electrical semantics: 0 drives reset
low and 1 drives reset high. The provider does not describe whether low means
sensor reset asserted; that interpretation belongs to the sensor protocol.

Both state pointers are checked with `IS_ERR` before argument dispatch. If
either is an error pointer the function prints
`err: yft_finger_reset_low or yft_finger_reset_high is error!!!` and returns
literal `-1`. NULL is not treated as `IS_ERR`.

A selected state's `pinctrl_select_state()` return is ignored. Valid values and
invalid no-op values return 0. There is no delay, busy wait, sleep, pulse, GPIO
request, or cached reset-state field. Timing and sequences are caller-owned.

## Stock consumer sequence

`microarray_fp_tee.ko:mas_finger_set_gpio_info` calls only
`yft_finger_set_reset(1)`, at `.text+0x1b4`, after its regulator path and before
`set_spi_mode(1)` and `set_irq(1)`. It ignores the return. No stock call to
value 0 was found.
