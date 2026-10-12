# yft_gpio_keys physical hardware contract

The stock DT and stock implementation jointly prove exactly two GPIO buttons.

| Physical evidence label | DT node | MT6878 GPIO | Polarity | Linux code in DT | Linux input key | IRQ | Requested trigger/flags | Debounce | Wake |
|---|---|---:|---|---:|---|---|---|---|---|
| `customkeyf1` | `/yft-gpio-keys/key-custom1` | 13 | active-low | `0x3b` (59) | `KEY_F1` | dynamic `gpiod_to_irq(GPIO13)` | both edges initially, `IRQF_SHARED`; stock later arms one next edge | 16 ms | yes |
| `customkeyf2` | `/yft-gpio-keys/key-custom2` | 8 | active-low | `0x3c` (60) | `KEY_F2` | dynamic `gpiod_to_irq(GPIO8)` | both edges initially, `IRQF_SHARED`; stock later arms one next edge | 16 ms | yes |

No fixed Linux IRQ numbers are encoded in DT: the child nodes have GPIO specifiers but no `interrupts`; the exact driver calls `gpiod_to_irq()`. A numeric Linux IRQ is controller/runtime allocation and cannot honestly be frozen from this static corpus.

The GPIO active-low descriptor converts physical low to logical state 1 (press) and physical high to state 0 (release). No direction change or output drive occurs; acquisition is `GPIOD_IN`.

The module handles no volume, power, camera, fingerprint or other key. The labels `customkeyf1/f2` are evidence; marketing names are not assigned in this hardware document.
