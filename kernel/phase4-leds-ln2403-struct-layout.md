# LN2403 recovered state layout

The single heap object is 280 bytes (`kzalloc(0x118, GFP_KERNEL)`), globally
published as `ln2403_chip_data`. Rebuilt offsets were compiler-dumped and each
hardware/state offset below was cross-checked against stock instructions.

| offset | size | recovered field |
|---:|---:|---|
| 0x00 | 48 | `struct mutex lock` |
| 0x30 | 8 | SOS/gate low interval (`ktime_t`) |
| 0x38 | 8 | SOS/gate high interval (`ktime_t`) |
| 0x40 | 4 | SOS transition count |
| 0x44 | 4 | gate-control GPIO number (GPIO91) |
| 0x48 | 4 | camping mode |
| 0x4c | 4 | LN2403 enable GPIO number |
| 0x50 | 4 | LN2403 power GPIO number |
| 0x54 | 4 | warning-light common-power GPIO number |
| 0x58 | 4 | red GPIO number |
| 0x5c | 4 | blue GPIO number |
| 0x60 | 4 | simple red/blue flash state |
| 0x64 | 4 | warning-light mode |
| 0x68 | 72 | red/blue `struct hrtimer` |
| 0xb0 | 8 | red/blue wakeup-source pointer |
| 0xb8 | 1 | gate-timer enabled flag |
| 0xb9 | 1 | PWM enabled flag |
| 0xba | 6 | alignment/padding |
| 0xc0 | 8 | current gate callback interval (`ktime_t`) |
| 0xc8 | 72 | camping gate `struct hrtimer` |
| 0x110 | 8 | camping wakeup-source pointer |

Other globals: four pinctrl pointers; signed `red_blue_flash_state`; signed
`camplight_duty`; exact mode string tables; three device attributes; and the stock reverse-cleanup attribute-pointer array. The field layout is closed from the allocation
immediate and stock access offsets, not guessed names.
