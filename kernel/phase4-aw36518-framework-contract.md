# GQ5012BF1 — AW36518 kernel-framework contract (Phase 7 + Phase 9)

The stock module implements **two** frameworks simultaneously:

1. a V4L2 flash sub-device (`v4l2_subdev` + `v4l2_ctrl_handler`), and
2. the MediaTek flashlight core (`flashlight_operations`, registered by device
   id from DT).

It implements no LED-class device and no custom character device.

## 1. MediaTek flashlight core

Registration: `flashlight_dev_register_by_device_id(&flash->flash_dev_id[0],
&aw36518_flash_ops)` from `aw36518_parse_dt`, guarded by
`is_yft_cts_board()` (see below).

`aw36518_flash_ops` (`.data+0x150`, 40 bytes, byte-identical in the
reconstruction) uses the positional initialiser form:

| Slot | Function | Behaviour |
|---|---|---|
| `flashlight_open` | `aw36518_flash_open` | `return 0` (8-byte function) |
| `flashlight_release` | `aw36518_flash_release` | `return 0` (8-byte function) |
| `flashlight_ioctl` | `aw36518_ioctl` | see table below |
| `flashlight_strobe_store` | `aw36518_strobe_store` | timed torch pulse |
| `flashlight_set_driver` | `aw36518_set_driver` | reference-counted init/uninit |

### ioctl surface

`aw36518_ioctl(unsigned int cmd, unsigned long arg)` with
`arg = (struct flashlight_dev_arg *){ int channel; int arg; }`.

| cmd | value | handled |
|---|---|---|
| `FLASH_IOC_SET_ONOFF` | `0x80045373` (`_IOR('S', 115, int)`) | yes |
| anything else | — | logs `No such command and arg(%d): (%d, %d)` and returns **`-ENOTTY` (-25)** |

`FLASH_IOC_SET_ONOFF` semantics (exact stock order):

* `arg != 0` (on):
  1. `aw36518_torch_brt_ctrl(flash, channel, 250000)` — fixed 250 000 µA torch
     current (register 0x05 ← `(250000-750)/1510 = 165 = 0xa5`), subject to the
     thermal clamp;
  2. `led_mode = V4L2_FLASH_LED_MODE_TORCH`; `mode_ctrl` → `0x01[3:2] = 0b10`;
  3. `enable_ctrl(true)` → `flashlight_kicker_pbm(1)` then `0x01[1:0] = 0b11`.
* `arg == 0` (off), only if `led_mode != NONE`:
  1. `led_mode = NONE`; `mode_ctrl` → `0x01[3:2] = 0b00`;
  2. `enable_ctrl(false)` → `flashlight_kicker_pbm(0)` then `0x01[1:0] = 0b00`.

Return value is 0 for the handled command.

### `flashlight_strobe_store(struct flashlight_arg arg)`

```
log "%s %d" (arg.channel)
set_driver(1)                      /* first user runs aw36518_init() */
torch_brt_ctrl(flash, arg.channel, arg.level * 25000)   /* 25 000 µA per level */
enable_ctrl(flash, arg.channel, true)
led_mode = TORCH; mode_ctrl()
msleep(arg.dur)
led_mode = NONE;  mode_ctrl()
enable_ctrl(flash, arg.channel, false)
set_driver(0)                      /* last user runs aw36518_uninit() */
return 0
```

### `flashlight_set_driver(int set)`

Reference count in `use_count` (`.bss+0x10`):

* `set != 0`: if `use_count == 0` call `aw36518_init(flash)`; `use_count++`;
  log `Set driver: %d`.
* `set == 0`: `use_count--`; when it reaches 0 call `aw36518_uninit(flash)`
  (which only drives the external GPIO low); clamp negative counts to 0; log
  `Unset driver: %d`.
* Always returns 0 (the init/uninit return value is discarded — stock quirk).

### Ulefone modification in the core (`flashlight.ko`)

`fl_enable()` inside the stock `flashlight.ko` compares the registered device
name with `strncmp(name, "aw36518-led0", 12)` and
`strncmp(name, "aw36518_v2-led0", 15)`; on a match it **bypasses the
low-battery/over-current (PT) disable path** and only logs.  This is why the
AW36518 driver itself never calls `flashlight_pt_is_low()` even though the
public Motorola donor does: the decision was moved into the core and is keyed on
the exact device-name string.  `"aw36518-led0"` is therefore ABI and must not be
renamed.

## 2. V4L2 flash sub-device

`aw36518_init_controls()` (inlined into probe) creates, on handler size 8:

| Control | Type | min | max | step | default |
|---|---|---|---|---|---|
| `V4L2_CID_FLASH_LED_MODE` | menu | — | 2 (`TORCH`) | mask `~0x7` | 0 (`NONE`) |
| `V4L2_CID_FLASH_STROBE_SOURCE` | menu | — | 1 (`EXTERNAL`) | mask `~0x3` | 0 (`SOFTWARE`) |
| `V4L2_CID_FLASH_STROBE` | button | 0 | 0 | 0 | 0 |
| `V4L2_CID_FLASH_STROBE_STOP` | button | 0 | 0 | 0 | 0 |
| `V4L2_CID_FLASH_TIMEOUT` | int | 40 | `pdata->max_flash_timeout` = **1600** | 40 | 1600 |
| `V4L2_CID_FLASH_INTENSITY` | int | 2940 | **1499790** | 5870 | 1499790 |
| `V4L2_CID_FLASH_TORCH_INTENSITY` | int | 750 | **385800** | 1510 | 385800 |
| `V4L2_CID_FLASH_FAULT` | int (volatile) | 0 | 15 | 0 | 0 |

`V4L2_CID_FLASH_FAULT` is marked `V4L2_CTRL_FLAG_VOLATILE`; the max value 15 is
the OR of `OVER_VOLTAGE|TIMEOUT|OVER_TEMPERATURE|SHORT_CIRCUIT`.

`s_ctrl` (`aw36518_led0_set_ctrl`) dispatch, under `mutex_lock(&flash->lock)`:

| Control | Action |
|---|---|
| `LED_MODE` | log `enter V4L2_CID_FLASH_LED_MODE`; `led_mode = val`; if `val != FLASH` run `mode_ctrl()`; then `NONE → enable_ctrl(false)`, `TORCH → enable_ctrl(true)`; `FLASH` alone only stores the mode and returns 0 |
| `STROBE_SOURCE` | `SOFTWARE` → `0x01[5:2] = 0b0011` (`mask 0x2C`, value `0x0C`), log `sw ctrl`; `EXTERNAL` → `0x01[5:2] = 0b1000` (value `0x20`), log `hw trigger`, then `enable_ctrl(true)` |
| `STROBE` | if `led_mode != FLASH` → `-EBUSY`; else `mode_ctrl()`, `enable_ctrl(true)`, then **drive the external GPIO high** |
| `STROBE_STOP` | if `led_mode != FLASH` → `-EBUSY`; else `enable_ctrl(false)`, `led_mode = NONE`, `mode_ctrl()` |
| `TIMEOUT` | `flash_tout_ctrl(val)` → `0x08[3:0] = val / 40` |
| `INTENSITY` | `flash_brt_ctrl(val)` → `0x03[7:0] = (val-2940)/5870` (thermal clamp applies) |
| `TORCH_INTENSITY` | `torch_brt_ctrl(val)` → `0x05[7:0] = (val-750)/1510` (thermal clamp applies) |
| default | `-EINVAL` (rval initialised to -22) |

`g_volatile_ctrl` (`aw36518_led0_get_ctrl`) handles only
`V4L2_CID_FLASH_FAULT`: it reads register `0x0A` and maps

| Register bit | V4L2 fault flag |
|---|---|
| bit 0 | `V4L2_FLASH_FAULT_TIMEOUT` (0x02) |
| bit 2 | `V4L2_FLASH_FAULT_OVER_TEMPERATURE` (0x04) |
| bit 4 **or** bit 5 | `V4L2_FLASH_FAULT_SHORT_CIRCUIT` (0x08) |

Anything else returns `-EINVAL`; a failing `regmap_read` propagates its error.
Faults are therefore **polled on demand only** (no IRQ, no worker, no timer);
register `0x0A` is additionally read once at the end of `aw36518_init()`, which
clears the latch before a new session.

`v4l2_subdev_internal_ops`:

* `.open` → `pm_runtime_get_sync()`, on error `pm_runtime_put_noidle()` and
  propagate (stock does **not** log here);
* `.close` → `pm_runtime_put()` only (the donor's extra `REG_FLAG2` write is
  **not** present in stock).

## Init / teardown sequencing

`aw36518_init(flash)` (called by `set_driver(1)` on the 0→1 edge and by
runtime-PM resume):

```
log "%s %d" (__func__, 0)
gpio_set(0)                                   /* external strobe low */
flash_tout_ctrl(400)      -> 0x08[3:0] = 0x0A
led_mode = NONE; mode_ctrl() -> 0x01[3:2] = 0b00
0x05 &= ~0x80
0x03 &= ~0x80
regmap_read(0x0A)                             /* clear/refresh fault latch */
```

Every step returns early on a negative regmap status; an out-of-range
`led_mode` yields `-EINVAL`.

`aw36518_remove()`: `thermal_cooling_device_unregister()` →
`v4l2_device_unregister_subdev()` → `v4l2_ctrl_handler_free()` →
`pm_runtime_disable()` → `pm_runtime_set_suspended()`.  Stock has **no**
`media_entity_cleanup()` and **no** `.shutdown` callback.

`aw36518_suspend()`: logs, drives the external GPIO low, returns 0 — it does
**not** touch the chip over I²C.  `aw36518_resume()`: logs and re-runs
`aw36518_init()`.

## `yft_devinfo` coupling

`aw36518_parse_dt()` calls `is_yft_cts_board()` (exported by `yft_devinfo.ko`,
CRC `0xad70697b`) for every DT child *after* the `Parse dt (...)` log and
*before* `flashlight_dev_register_by_device_id()`:

* non-zero (CTS board) → the child is skipped without registering and without
  advancing the channel index, so on a CTS unit the AW36518 never appears in the
  MediaTek flashlight device list (the V4L2 sub-device is still registered);
* zero → normal registration; a non-zero return from the registration aborts
  `parse_dt` with that value.

This single call is the only difference in the exported-symbol set between
`aw36518.ko` and `aw36518_v2.ko`.
