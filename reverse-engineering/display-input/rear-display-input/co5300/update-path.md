# CO5300 rear panel: pixel/update path

## Classification (proven)

This is not DRM and not fbdev. The module registers only a misc device
(`/dev/tiny_lcd_miscdev`, dynamic minor) plus five driver sysfs attributes. It
imports no DRM, fb, dma-buf or ION symbols. The panel is a GRAM-based
controller: the host pushes a full frame into GRAM with RAMWR, and the panel
self-refreshes.

## Geometry and format

| item | value | evidence |
|---|---|---|
| native window | 340×340 | CASET/RASET `0x0000..0x0153` in init and frame path |
| alternate window | 320×320, offset (10,10) | CASET/RASET `0x000a..0x0149` |
| pixel format | RGB565, 2 bytes/pixel | `3A 55`; sizes 231200 = 340·340·2 and 204800 = 320·320·2 |
| stride | width × 2, no padding | single contiguous transfer of `len` bytes |
| byte order | as supplied by userspace | no swap in kernel |
| buffer | `gImage_logo[231200]` (global, `.data`) | ioctl copies user frames into it |

`framesize` (`{int width, height}`, default `{340, 340}`) is set by
`TINY_LCM_IOC_FRAME_SIZE`. Only the width selects the transfer length
(320 → 204800, else 231200). The height is only logged.

## Write paths

1. **Immediate.** `TINY_LCM_IOC_WRITE_FRAME`, when `frame_send_enable == 1` and
   `frame_send_end == 0` (AOD/"send now" mode): `copy_from_user(gImage_logo,
   arg, 231200)`, then `spidev_sync_write_multi_data(gImage_logo, 231200)`, then
   `write_frame_status = 1`.
2. **TE-synchronised.** When `frame_send_end == 1` (normal), the ioctl copies
   the frame and sets `write_frame_status = 3`. The TE falling-edge IRQ
   (GPIO 31, `IRQF_TRIGGER_FALLING`, IRQ name `tiny_lcd_te`) runs
   `schedule_delayed_work(&tiny_lcd_te_work, 0)` whenever
   `frame_send_enable == 1`. The work handler sends only if the status is 3 and
   `frame_send_enable == 1 && frame_send_end`, using the width-selected length.
   It then sets the status back to 1.
3. **Disabled.** When `frame_send_enable == 0`, the ioctl logs
   "ignore, in recovery" and only sets the status to 3.
4. **sysfs** `tiny_lcd_write_frame` (any value): copies `gImage_logo` to
   `pic_from_user`, sends `gImage_logo`, then post-processes the status.
5. **Probe splash.** `showpic()` sends the built-in `gImage_logo` once
   (`backlight_step = 255` first), timed with `ktime_get_boottime()`.

`TINY_LCM_IOC_FRAME_STATUS` returns the 64-bit status to userspace; the HAL
polls it. A partial `copy_from_user` zeroes the tail of `gImage_logo`, sets the
status to 3 and returns -1.

## SPI segmentation

Each frame is one `spi_message` with a single `spi_transfer` of `len` bytes at
52 MHz. It goes from a temporary `vmalloc(len)` copy (231200 bytes) and is
serialized by `buf_lock`. There is no chunking in the driver; segmentation and
DMA are the MediaTek SPI controller driver's business. The `vmalloc` buffer is
not DMA-coherent, so the controller maps it. At 52 MHz a full frame is about
35.6 ms of wire time, so the upper bound is about 28 fps with TE pacing.

There are no dirty rectangles and no partial updates beyond the fixed 320×320
centred window.

## Locking and stock defects

- `buf_lock` is a zero-filled `struct mutex` in `.bss` that is **never
  initialized** (stock has no `mutex_init`/`DEFINE_MUTEX`). The uncontended
  fast path works; contention would hit an uninitialized wait list.
- Frame data in `gImage_logo` is written by the ioctl and read by the TE work
  without a lock.
- The 32-bit HAL's ioctl encodings (`0x40046b3b` …) are not translated by
  `compat_ioctl`, so 32-bit callers fall into the "Error ID" default.
