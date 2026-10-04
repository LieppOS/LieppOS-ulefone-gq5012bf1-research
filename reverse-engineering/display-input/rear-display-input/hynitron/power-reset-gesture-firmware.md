# Hynitron sequences, gesture path, firmware boundary, feature blocks

These sequences are read from the reconstructed source. Its 65/65 functions are
byte-identical to stock, so they are the stock sequences. `reset_proc(d)` is:
reset GPIO 32 = 0, `mdelay(20)`, (`hyn_reset_watchdog_proc` is empty), reset
= 1, then `mdelay(d)` if d≠0.

## Probe (`hyn_probe`)

1. `i2c_check_functionality(I2C)`, `kzalloc(584)`, set global `hyn_ts_data`.
2. `hyn_platform_data_init`: `kzalloc` pdata and parse DT (`hynitron,*` GPIOs,
   resolution, keys).
3. `hyn_gpio_configure`: request VDD GPIO 119 → output 1; IRQ GPIO 11 → input;
   reset GPIO 32 → output 1; then reset 0, `mdelay(20)`, reset 1.
4. `hyn_ts_data_init`: config type CST820 (0xB7), main addr 0x15, 340×340.
5. `mdelay(60)`; `hyn_firmware_info` → `cst8xx_firmware_info`: `msleep(100)`,
   read 6 B from 0xA6. If that fails, `hyn_detect_bootloader` →
   `cst8xx_bootloader_enter`: addr → boot addr, for t=6..15: `reset_proc(t)`,
   write 0xA001=0xAB, read 0xA003, success on 0xC1 (2 ms backoff); then restore
   addr 0x15 and `reset_proc(40)`; `mdelay(30)`. A failure aborts probe.
6. `hyn_input_dev_int`: input `hyn_ts`, protocol A, work = `cst8xx_touch_report`,
   singlethread workqueue `hyn_wq`.
7. `hyn_irq_init`: `gpio_to_irq`, flags FALLING|ONESHOT,
   `request_threaded_irq(NULL thread fn → hyn_eint_interrupt_handler)` as
   "Hynitron Touch Int", `enable_irq_wake`.
8. `hyn_irq_disable` (nosync), `hyn_update_firmware_init`: re-read info and
   resolve chip series/product line/boot addr from `hynitron_chip_type_grp`.
   No update is performed.
9. sysfs group (7 nodes), `hyn_gesture_init` (16 key capabilities, gesture
   sysfs, mode=1, active=0).
10. `reset_proc(40)`, `hyn_irq_enable`, `yft_set_touch_device_used("hyn_ts",1)`.

Error unwind: free VDD/reset/IRQ GPIOs, `hyn_gesture_exit`,
`hyn_release_sysfs`, `free_irq(use_irq, NULL)` if nonzero, `kfree` pdata and
ts_data, set the global to NULL. Stock defects preserved: `free_irq` uses
`dev_id` NULL (registered with `hyn_ts_data`); a `hyn_gpio_configure` failure
returns -1 without freeing ts_data/pdata; the gesture-init "fail" message tests
a stale `ret`.

## Runtime report

IRQ handler: `hyn_irq_disable()`, then `queue_work`. The work calls
`pm_wakeup_event(5 s)`. If suspended and gesture armed, it calls
`hyn_gesture_readdata`. It then calls `tpd_touchinfo` (9 B from 0x00),
`tpd_down`/`tpd_up` and `input_sync`, and re-enables the IRQ.

## Display-driven power (only entry points: `tiny_tp_power_contorl`)

| | sequence |
|---|---|
| **suspend** (`enable=0`) | if already suspended: log, return. `suspended=1`; `reset_proc(10)`. If `tiny_tpgesture_status==1`: `hyn_gesture_suspend` and return (IRQ stays enabled). Else `hyn_irq_disable`, `hyn_enter_deep_sleep` = `reset_proc(50)` + write 0xE5=0x03. |
| **resume** (`enable=1`) | if not suspended: return. `suspended=0`; `reset_proc(40)`; release all fingers (`BTN_TOUCH 0`, `mt_sync`); `work_mode=0`. If gesture armed: `hyn_gesture_resume` and return. Else `hyn_irq_enable`. |
| **gesture flag** (`tiny_tp_gesture_contorl`) | sets `tiny_tpgesture_status` 1/0 only; takes effect on the next suspend/resume. |

The GPIO VDD rail is never switched after probe. Power-off is the
controller's deep-sleep command. "Display power off" means touch deep sleep, or
gesture-armed sleep with the IRQ wake-capable. CO5300 owns ordering (see
`../integration.md`).

## Gesture

- **arm:** write 0xEC=1, `msleep(10)`, read back ≤3 retries; `msleep(2)`; write
  0xE5=1, `msleep(10)`, read back ≤3 retries; `active=1`; IRQ type →
  FALLING|NO_SUSPEND (disable/set/enable).
- **read:** read 8 B from 0x01, gesture id = byte 0. `hyn_check_gesture` maps
  the ID to keys, then reports the key down/sync/up/sync. Stock defect: the
  coordinate loop indexes `buf[10..13]`, which the 8-byte read never fills, so
  coordinates are always 0.
- **disarm:** `active=0`, IRQ type back to `pdata->irq_gpio_flags`. There is no
  register write for SEL_CAP. The chip leaves gesture mode on the
  `reset_proc(40)` that precedes it.

## Firmware boundary (payload private)

| image | section/offset | size | SHA-256 | table entry |
|---|---|---:|---|---|
| `cst8xx_fw` | `.data` (symbol) | 15419 | `0566ea7799d6f8bbce026639d9dbb89f0e629ab533d1d90e4901c81d5611e1d8` | [0] CST816D module 0x04; [2] CST820 module 0xFF |
| `cst816t_fw` | `.data` (symbol) | 15410 | `0d02fde67223c1e7aa6c4ce1d1e522bcbe79d4d58decf1aa79b865cb2e504de3` | [1] CST816T module 0x04 |

Only `hyn_boot_update_fw` consumes them. It is called from sysfs
`hynfwupdate` (store) and `hyntprwreg` opcode `0x34`, never from probe
(`HYN_EN_AUTO_UPDATE=0`). For SEL_CAP it selects an index: 0 if
`chip_ic_type==0`, else `hyn_find_fw_idx(0,1)` (module-id match). It stores
name, pointer and length, disables the IRQ, and sets `work_mode=UPDATE`. In the
`CST8XX` case it calls only `cst8xx_firmware_info`, because
`cst8xx_boot_update_fw` is compiled out (`HYN_EN_AUTO_UPDATE_CST78xx=0`). It
then re-enables the IRQ and sets NORMAL.

**Proven:** the images are dead payload linked by the vendor's default
`hynitron_fw_grp` table. A pointer is selected, but no byte is ever transmitted.
The stock ELF has no erase/program/verify routine for any family.

## Feature blocks

| block | status | evidence |
|---|---|---|
| firmware table + selection | STOCK PRESENT | `hynitron_fw_grp`, `hyn_find_fw_idx`, `hyn_boot_update_fw` |
| firmware programming (all families) | COMPILED OUT | `HYN_EN_AUTO_UPDATE_*=0` |
| auto/boot update at probe | COMPILED OUT | `hyn_update_firmware_init` body |
| chip-ID variants table (33) | STOCK PRESENT | `hynitron_chip_type_grp` 198 B |
| ROM/bootloader detect (7 families) | STOCK PRESENT (CST8XX reachable) | `hyn_detect_bootloader` 1952 B |
| mutual-cap (cst3xx) report/info | STOCK PRESENT, unreachable for CST820 | `cst3xx_touch_report`, `cst3xx_firmware_info` |
| debug sysfs (fwver/rwreg/fwupdate/fwupgradeapp/factorytest) | STOCK PRESENT | 7 attrs |
| factory test | STUB (sysfs only) | `HYN_AUTO_FACTORY_TEST_EN=0` |
| procfs / APK tool | COMPILED OUT | `ANDROID_TOOL_SURPORT=0` |
| gesture | STOCK PRESENT | |
| touchkeys | STOCK PRESENT, inactive (`have_key` from DT; 0 keys) | `cst3xx_touch_report` key strings |
| ESD | COMPILED OUT (empty object) | |
| proximity | COMPILED OUT (empty object) | |
| charger mode / glove / palm | STOCK ABSENT (glove field layout-only) | no code/strings |
| I2C recovery / retries | STOCK PRESENT (helper retries + error logs) | `hyn_i2c_*` |
| suspend/resume (display-driven) | STOCK PRESENT | exports |
| earlysuspend / FB / DRM notifier | COMPILED OUT | no imports |
| rawdata/diff/baseline/self-test/calibration | STOCK ABSENT (only via raw `hyntprwreg`) | no code |
| software watchdog reset | COMPILED OUT | 4-byte stub |
