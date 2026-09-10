# yft_gpio_keys state and structure layout

The stock ELF has no DWARF/BTF. Layout is recovered from stock AArch64 disassembly and the exact-GKI definitions; final `.text` is byte-identical, proving the reconstruction uses the same accessed offsets.

## `struct gpio_keys_button` (56 bytes, stride `0x38`)

| Offset | Field |
|---:|---|
| `0x00` | `u32 code` |
| `0x04` | `int gpio` |
| `0x08` | `int active_low` |
| `0x10` | `const char *desc` |
| `0x18` | `u32 type` |
| `0x1c` | `int wakeup` |
| `0x20` | `int wakeup_event_action` |
| `0x24` | `int debounce_interval` |
| `0x28` | `bool can_disable` |
| `0x2c` | `int value` |
| `0x30` | `u32 irq` |

Probe advances DT buttons by `0x38`; allocation is `0x30 + n*0x38`, proving both size and platform-data header size.

## `struct gpio_keys_platform_data` (48 bytes, `0x30`)

`buttons@0x00`, `nbuttons@0x08`, `poll_interval@0x0c`, `rep` bitfield allocation at `0x10`, `enable@0x18`, `disable@0x20`, `name@0x28`.

## `struct gpio_keys_drvdata` (72-byte header, `data@0x48`)

`pdata@0x00`, `input@0x08`, `disable_lock@0x10` (48 bytes), `keymap@0x40`, flexible `data[]@0x48`. Stock probe allocates `0x48 + nbuttons*0x158`.

## `struct gpio_button_data` (344 bytes, `0x158`)

| Offset | Field |
|---:|---|
| `0x00` | button pointer |
| `0x08` | input pointer |
| `0x10` | GPIO descriptor |
| `0x18` | keycode pointer |
| `0x20` | release hrtimer |
| `0x68` | release delay |
| `0x70` | delayed work |
| `0xf8` | debounce hrtimer |
| `0x140` | software debounce ms |
| `0x144` | IRQ |
| `0x148` | wakeup trigger type |
| `0x14c` | spinlock |
| `0x150` | disabled |
| `0x151` | key_pressed |
| `0x152` | suspended |
| `0x153` | debounce_use_hrtimer |
| `0x154..0x157` | tail padding |

The stock source has no extra YFT press counter, long-press state, custom work, per-key wake object or hidden fields. Long/multi-press policy is userspace, not this structure.
