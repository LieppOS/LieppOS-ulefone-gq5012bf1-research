# yft_gpio_keys mandatory RED

## Unchanged donor build

The exact donor `common/drivers/input/keyboard/gpio_keys.c` at `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` was copied unchanged into `lieppos/yft-gpio-keys-donor-red/gpio_keys.c`. Only `Makefile`/`BUILD.bazel` external-module harness files were added.

Build: `./tools/bazel build //lieppos/yft-gpio-keys-donor-red:gpio_keys_donor_red`

- BUILD_RC: 0
- compiler warnings: 0
- modpost warnings: 0
- unresolved symbols: 0
- artifact: `workspace/phase4-yft-gpio-keys/donor-red/gpio_keys.ko`
- artifact SHA-256: `a2f58ed25199a17fe3c7c72e1b2267bb76db21a08cd0b9129eeb8130dda90c86`

## RED delta

| Area | Stock | Untouched donor | RED |
|---|---|---|---|
| Function set | 23 | 23 | set matches |
| Function sizes | 23/23 | 23/23 | sizes match |
| Byte-identical functions | 23 target | 16/23 | **FAIL** (7 code ranges differ after layout/address effects) |
| Imports/MODVERSIONs | 65 | 63 | **FAIL**: donor lacks `_printk`, `disable_irq_nosync` and their CRC entries |
| Module basename/name | `yft_gpio_keys` | `gpio_keys` | **FAIL** |
| Driver name | `yft-gpio-keys` | `gpio-keys` | **FAIL** |
| OF compatible | `yft-gpio-keys` | `gpio-keys` | **FAIL** |
| Missing debounce default | 16 ms | 5 ms | **FAIL** |
| GPIO ISR | disables IRQ before debounce | leaves IRQ enabled | **FAIL** |
| Debounce completion | reports/syncs, relaxes, enables IRQ | reports/syncs, relaxes | **FAIL** |
| Report completion | logs state and changes IRQ to next edge | no logging/type change | **FAIL** |
| DT parsing/input/PM/lifecycle base | same | same | pass as framework base |

Raw donor `.text` is 5752 bytes versus stock 5900 bytes. The mandatory RED therefore proves the public exact-GKI source was not stock-identical before behavior changes.

The complete recovered delta is in `phase4-yft-gpio-keys-yft-delta.md`; final parity is in the function/object/import parity TSVs.
