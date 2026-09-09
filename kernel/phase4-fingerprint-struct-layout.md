# `fingerprint.ko` private state and object layout

There is no allocated private structure. Stock uses independent static/global
objects. Semantic assignments below are backed by named symbols and relocation
accesses; there are no inferred anonymous fields.

## `.bss` globals

| offset | size | symbol | meaning |
|---:|---:|---|---|
| `0x00` | 8 | `yft_finger_pinctrl` | global `struct pinctrl *` |
| `0x08` | 8 | `yft_finger_reset_high` | reset-high state |
| `0x10` | 8 | `yft_finger_reset_low` | reset-low state |
| `0x18` | 8 | `yft_finger_spi0_mi_as_spi0_mi` | MI SPI state |
| `0x20` | 8 | `yft_finger_spi0_mi_as_gpio` | MI GPIO state |
| `0x28` | 8 | `yft_finger_spi0_mo_as_spi0_mo` | MO SPI state |
| `0x30` | 8 | `yft_finger_spi0_mo_as_gpio` | MO GPIO state |
| `0x38` | 8 | `yft_finger_spi0_clk_as_spi0_clk` | CLK SPI state |
| `0x40` | 8 | `yft_finger_spi0_clk_as_gpio` | CLK GPIO state |
| `0x48` | 8 | `yft_finger_spi0_cs_as_spi0_cs` | CS SPI state |
| `0x50` | 8 | `yft_finger_spi0_cs_as_gpio` | CS GPIO state |
| `0x58` | 8 | `yft_finger_eint_pull_down` | IRQ pull-down state |
| `0x60` | 8 | `yft_finger_eint_pull_up` | IRQ pull-up state |
| `0x68` | 8 | `yft_finger_eint_pull_dis` | IRQ bias-disable state |
| `0x70` | 8 | `yft_finger_power_on` | unused power-on pointer; cleared by deinit |
| `0x78` | 8 | `yft_finger_power_off` | unused power-off pointer; cleared by deinit |
| `0x80` | 8 | `yft_finger_plat` (local) | published `struct platform_device *`; wait condition |

All are initially zero. There are no cached GPIO numbers, IRQ number, boolean
parse flag, power/reset/SPI software state, or provider-state allocation.

## `.data` objects

| offset | size | object | layout/status |
|---:|---:|---|---|
| `0x00` | 24 | `finger_init_waiter` | `wait_queue_head_t`; lock at +0, self-linked list head pointers at +8/+16 |
| `0x18` | 400 | `yft_finger_match` | two 200-byte `of_device_id` entries; one compatible plus zero terminator |
| `0x1a8` | 248 | `yft_finger_pdrv` | platform driver; probe +0, remove +8, driver name at +0x30, owner +0x40, OF table +0x58 |

## Synchronization

The only synchronization primitive is the wait queue's embedded spinlock.
There is no completion, standalone mutex, rwlock, atomic flag, or lock around
pinctrl globals. Multi-state setter transitions can interleave.

Full compiler/linker objects, including module metadata and OF alias storage,
are inventoried in `phase4-fingerprint-objects.tsv`.
