# `yft_finger_set_irq` contract

Prototype and ABI:

```c
int yft_finger_set_irq(int value); /* CRC 0x6d125ec3, KCFI 0x00050794 */
```

## Mapping

| value | selected state | exact meaning |
|---:|---|---|
| 0 | `finger_eint_pull_down` | GPIO/EINT3 mode 0, pull-down |
| 1 | `finger_eint_pull_up` | GPIO/EINT3 mode 0, pull-up |
| 2 | `finger_eint_pull_dis` | GPIO/EINT3 mode 0, bias disabled |
| other | none | accepted no-op |

This export configures only pinctrl/bias. It does **not** call `enable_irq`,
`disable_irq`, `irq_set_irq_wake`, GPIO direction APIs, or request an interrupt.
The stock interrupt handler, Linux IRQ enable/disable, and wake configuration
reside in `microarray_fp_tee.ko`.

All three state pointers are validated before dispatch. Any `ERR_PTR` prints
`err: yft_finger_int_as_gpio is error!!!!` and returns literal `-1`. Otherwise
selection return values are ignored and the function returns 0. NULL is not an
error pointer under this test. There is no cached IRQ state and no lock.

## IRQ number and trigger evidence

`yft_finger_get_irqnum()` separately maps index 0 from `/yft_finger`:

```dts
interrupt-parent = <&mt6878_pinctrl>; /* phandle 0x89 */
interrupts = <3 1 3 0>;
```

The first two-cell specifier is EINT/GPIO3, raw type 1
(`IRQ_TYPE_EDGE_RISING`). `fingerprint.ko` does not itself consume the second
specifier.

## Stock consumer

`microarray_fp_tee.ko` calls `yft_finger_set_irq(1)` exactly once at
`.text+0x1c4`, after reset-high and SPI-pinmux selection. Its result is ignored.
The consumer later obtains/registers/manages its own IRQ independently.
