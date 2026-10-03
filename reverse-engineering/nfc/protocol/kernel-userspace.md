# st21nfc kernel ↔ userspace contract

Source of truth: reconstructed `st21nfc.c` / `st21nfc.h` v2.2.0.19
(`../reconstruction/source/`), which rebuilds to the shipped module with
22/24 functions byte-identical (`../kernel/parity/st21nfc.parity.txt`).

Device: `/dev/st21nfc`, misc char device, `MISC_DYNAMIC_MINOR`, parent = the I²C
client device. Permissions `0660 nfc radio` (`ueventd.rc`), SELinux type
`st21nfc_device`.

## File operations

| op | behaviour |
|---|---|
| `open` | fails with `-EBUSY` (and `pr_err "device already opened ret= %d"`) if `device_open` is already set; otherwise marks the device open. Single-opener device. |
| `release` | clears `device_open`, disables the IRQ (`st21nfc_disable_irq_inline`), resets `r_state_current` bookkeeping. |
| `read(count)` | `count==0` → 0; clamped to `MAX_BUFFER_SIZE`. **If the IRQ GPIO reads 0 there is no pending NCI frame: the driver fills the user buffer with `0x7E` filler and returns `count` instead of blocking.** Otherwise it takes `read_mutex` and does one `i2c_master_recv(count)`. Negative I²C result → `pr_err "i2c_master_recv returned %d"` and the errno is returned; a result larger than the request → `pr_err "received too many bytes from i2c (%d)"`. |
| `write(count)` | `memdup_user` (failure → `pr_err "memdup_user failed"`, `-EFAULT`), then one `i2c_master_send`. Non-matching length → `pr_err "i2c_master_send returned %d"`. |
| `poll` | `poll_wait` on `read_wq`, then samples the IRQ GPIO: high → returns `POLLIN|POLLRDNORM` **and disables the IRQ** (level-triggered line, so it must be masked while data is pending); low → re-enables the IRQ and returns 0. This is the only place the IRQ is re-armed in normal operation. |
| `unlocked_ioctl` / `compat_ioctl` | same handler, see below. |

Framing: the driver is a transparent NCI byte pipe. It tracks `r_state_current`
(`ST21NFC_HEADER` / payload) only for the optional power-statistics filter,
which is compiled out of the shipped build (`ST54J_PWRSTATS` undefined, and the
board has no `pidle-gpios`).

## IRQ handling

- `devm_request_irq(client->irq, st21nfc_dev_irq_handler, polarity_mode, client->name, dev)`.
- Default `polarity_mode` comes from the DT/driver default and is changed only via ioctl.
- The handler disables the IRQ (`st21nfc_disable_irq_inline`), reports a wakeup
  event (`pm_wakeup_ws_event` on the registered `st21nfc` wakeup source) and
  wakes `read_wq`. Re-arming happens in `poll`.
- `irq_enabled`/`irq_is_attached` are tracked so that recovery can detach and
  reattach the handler safely; `irq_enabled_lock` is a spinlock, `irq_dir_mutex`
  serialises direction changes between `poll`, `ioctl` and recovery.

## ioctl interface

`ST21NFC_MAGIC = 0xEA`. Both the modern `_IO()` encodings and the legacy
`_IOR()` encodings are accepted for every command (the driver matches both case
labels), so old and new HAL builds work against the same node.

| command | encoding | value | semantics |
|---|---|---|---|
| `ST21NFC_GET_WAKEUP` | `_IO(0xEA,1)` | `0xEA01` | returns the IRQ GPIO level normalised to 0/1 (used by the HAL to decide whether a frame is pending) |
| `ST21NFC_PULSE_RESET` | `_IO(0xEA,2)` | `0xEA02` | **double pulse reset**: RESET low 20 ms → high 10–11 ms → low 20 ms → high. Notifies the ST54-SPI callback with `RESET_START`/`RESET_END` around the sequence and resets the read state machine. |
| `ST21NFC_SET_POLARITY_RISING` | `_IO(0xEA,3)` | `0xEA03` | re-requests the IRQ with `IRQF_TRIGGER_RISING` |
| `ST21NFC_SET_POLARITY_HIGH` | `_IO(0xEA,5)` | `0xEA05` | re-requests the IRQ with `IRQF_TRIGGER_HIGH` (the mode the board actually uses — live `/proc/interrupts` shows `Level`) |
| `ST21NFC_GET_POLARITY` | `_IO(0xEA,7)` | `0xEA07` | returns the current `polarity_mode` |
| `ST21NFC_RECOVERY` | `_IO(0xEA,8)` | `0xEA08` | ST21NFCD recovery sequence, see [`recovery.md`](recovery.md) |
| `ST21NFC_USE_ESE` | `_IOW(0xEA,9,unsigned int)` | — | `__get_user()` the flag and forward `ST54SPI_CB_ESE_USED` / `ST54SPI_CB_ESE_NOT_USED` to the registered ST54-SPI callback (arbitration between the CLF and an SPI secure element). On this board no ST54-SPI driver is loaded, so the callback is NULL and the call is a no-op that still returns 0. |
| legacy aliases | `_IOR(0xEA,n,unsigned int)` | `0xEA01..0xEA08` with size/dir bits | identical behaviour |
| anything else | — | — | `pr_err "%s bad ioctl %u"`, `-EINVAL`; wrong magic → `-ENOTTY` |

Access checking is done once at entry from `_IOC_DIR`/`_IOC_SIZE` (`access_ok`),
not per command.

`st21nfc_loc_set_polaritymode()` (used by the two polarity ioctls) frees the
current IRQ, re-reads `irq-gpios` as input, stores the new trigger type, and
re-requests the IRQ under `irq_dir_mutex`; failures print
`gpiod_direction_input failed` / `devm_request_irq failed`.

## Exported kernel API (for an ST54-SPI secure-element driver)

```c
void st21nfc_register_st54spi_cb(void (*cb)(int, void *), void *data);
void st21nfc_unregister_st54spi_cb(void);
```

Callback reason codes: `ST54SPI_CB_RESET_END 0`, `ST54SPI_CB_RESET_START 1`,
`ST54SPI_CB_ESE_NOT_USED 2`, `ST54SPI_CB_ESE_USED 3`.
The shipped module exports **0** symbols via `__ksymtab` (the two functions are
plain globals, not `EXPORT_SYMBOL`), and no module on this device registers a
callback — `st54spi.ko` is not shipped.

## Power management

`SET_SYSTEM_SLEEP_PM_OPS(st21nfc_suspend, st21nfc_resume)`:

- **suspend**: if the IRQ is enabled, `enable_irq_wake(client->irq)` and record
  `irq_wake_up`; sample the pidle GPIO if one exists (it does not on this board).
  The device is therefore a **wake source** — card emulation/RF events can wake
  the AP (live suspend log contains an `st21nfc` wake-source entry).
- **resume**: `disable_irq_wake()` if it was armed; if a pidle GPIO exists and
  its level changed, queue the power-state work. Inert here.

No runtime-PM, no regulator or clock handling in the driver: the CLF is powered
from an always-on rail and clocked from the SRCLKEN-RC `nfc` XO buffer (BBCK4).

## sysfs

Attribute group on the I²C device (`sysfs_create_group`):

| attribute | access | content |
|---|---|---|
| `i2c_addr` | rw | current I²C slave address (decimal/hex), writable for bring-up |
| `version` | r | driver version string `2.2.0.19` |
| `power_stats` | r | per-state (IDLE/ACTIVE/ACTIVE_RW) counts, durations, last entry/exit and the error counters. Created only when a pidle GPIO exists — **not present on this board**. |
