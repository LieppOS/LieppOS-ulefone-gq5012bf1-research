# `fingerprint.ko` export ABI contract

Stock provider: `fingerprint.ko` SHA256
`f5d4dde1f09ac1d67877c66dddf2839de1f496bb2b6b74f50fbe3cd1693b60dc`.
All prototypes below are fixed by stock CRC/KCFI class, argument use, and stock
consumer call sites. CRCs must arise from source; patching is prohibited.

| symbol | stock CRC | prototype | KCFI | behavior / state / side effects | stock consumer |
|---|---:|---|---:|---|---|
| `yft_finger_probe_isok` | `0x7476a412` | `int yft_finger_probe_isok(bool probe_isok)` | `0xd2a1eef1` | returns the input normalized to one bit; touches no state or hardware | none found |
| `yft_finger_set_power` | `0x1fc1d7b1` | `int yft_finger_set_power(int enable)` | `0x00050794` | ignores `enable`, prints `no need gpio power`, returns 0; no power or GPIO action | none found |
| `yft_finger_power_deinit` | `0xad1b117e` | `void yft_finger_power_deinit(void)` | `0xa540670c` | clears only `yft_finger_power_on/off`; calls `devm_pinctrl_put` if the global pinctrl pointer is non-NULL; does not clear that pointer or other states | none found |
| `yft_finger_set_reset` | `0xcae83e02` | `int yft_finger_set_reset(int value)` | `0x00050794` | validates both reset-state pointers; 0 selects `finger_reset_en0`, 1 selects `finger_reset_en1`, other values do nothing; selector result ignored; returns 0, or -1 if either state is `ERR_PTR` | `microarray_fp_tee` once with 1 |
| `yft_finger_set_irq` | `0x6d125ec3` | `int yft_finger_set_irq(int value)` | `0x00050794` | validates all three EINT state pointers; 0 selects pull-down, 1 pull-up, 2 bias-disable, other values do nothing; no Linux IRQ mask/wake call; returns 0 or -1 | `microarray_fp_tee` once with 1 |
| `yft_finger_get_irqnum` | `0x9cc3cc91` | `int yft_finger_get_irqnum(void)` | `0x837de525` | finds `mediatek,yft_finger` globally and returns `irq_of_parse_and_map(node, 0)`; no cached IRQ and no `of_node_put` | none found |
| `yft_finger_get_irq_gpio` | `0x1a8a2d17` | `int yft_finger_get_irq_gpio(void)` | `0x837de525` | finds the node and returns `of_get_named_gpio_flags(node, "int-gpio", 0, NULL)` | none found |
| `yft_finger_get_reset_gpio` | `0x6f79cc60` | `int yft_finger_get_reset_gpio(void)` | `0x837de525` | finds the node and returns `of_get_named_gpio_flags(node, "reset-gpio", 0, NULL)` | none found |
| `yft_finger_set_spi_mode` | `0x0cf6e61a` | `int yft_finger_set_spi_mode(int mode)` | `0x00050794` | validates all eight SPI pin states; mode 0 selects CLK, CS, MI, MO GPIO states in that order; mode 1 selects CLK, CS, MI, MO SPI states; other values do nothing; returns 0 or -1 | `microarray_fp_tee` twice with 1 |
| `yft_waite_for_finger_dts_paser` | `0x4202702c` | `void yft_waite_for_finger_dts_paser(void)` | `0xa540670c` | waits on `finger_init_waiter` until global `yft_finger_plat` is non-NULL or 750 jiffies expire; no status return | `microarray_fp_tee` once in probe |

## Setter return details

The setter functions return 0 after valid selection even if an individual
`pinctrl_select_state()` fails; its return value is discarded. Invalid argument
values are accepted as no-ops and also return 0. Pointer-validation failure
prints a stock error string and returns literal `-1`, not `PTR_ERR()`.

## Consumer call ordering

Stock `microarray_fp_tee.ko` executes:

```text
wait()
  -> consumer regulator setup
  -> set_reset(1)
  -> set_spi_mode(1)
  -> set_irq(1)
```

It independently calls `set_spi_mode(1)` from `mas_sync` on its userspace-read
path. All four imported-return values are ignored. Exact call offsets and
context are in `phase4-fingerprint-microarray-boundary.md`.

## Consumer census

The project-wide stock intermodule ABI census identifies only four consumer
edges, all from `microarray_fp_tee.ko`. The other six symbols remain required
public provider ABI even though this stock image has no module consumer for
them.
