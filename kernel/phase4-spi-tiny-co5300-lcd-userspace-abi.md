# Phase 4 `spi_tiny_co5300_lcd` userspace ABI

## Device and callers

The kernel endpoint is `/dev/tiny_lcd_miscdev` (`MISC_DYNAMIC_MINOR`). Stock
callers are both `vendor/lib/hw/tinylcd.default.so` and
`vendor/lib64/hw/tinylcd.default.so`, reached through
`vendor.yft.hardware.tinylcd@1.0-service`.

The file operations are open, release, unlocked ioctl, and compat ioctl. Open
and release return zero. Compat ioctl forwards the compat userspace pointer to
the same implementation.

## Native 64-bit ioctl values

| Request | Value | Argument/behavior |
|---|---:|---|
| `TINY_LCM_IOC_POWER_ENABLE` | `0x00006b37` | no argument; panel power on |
| `TINY_LCM_IOC_POWER_DISABLE` | `0x00006b38` | no argument; panel power off |
| `TINY_LCM_IOC_BL_ENABLE` | `0x00006b39` | no argument; nonzero power entry |
| `TINY_LCM_IOC_BL_DISABLE` | `0x00006b3a` | no argument; power off |
| `TINY_LCM_IOC_BL_CONTROL` | `0x40086b3b` | input `u64`; cache brightness only |
| `TINY_LCM_IOC_WRITE_FRAME` | `0x40086b3c` | input pointer to exactly 231200 bytes |
| `TINY_LCM_IOC_FRAME_STATUS` | `0xc0086b3d` | output `u64` status |
| `TINY_LCM_IOC_TP_GESTURE_ENABLE` | `0x00006b3e` | calls Hynitron power/gesture providers |
| `TINY_LCM_IOC_TP_GESTURE_DISABLE` | `0x00006b3f` | disables Hynitron gesture path |
| `TINY_LCM_IOC_POWER_AOD` | `0x00006b40` | powers on, then allows immediate frame send |
| `TINY_LCM_IOC_FRAME_SIZE` | `0x40086b41` | input `{u32 width, u32 height}` |

Unknown requests log and return zero, matching stock.

## Compat values

The 32-bit HAL emits the same raw no-argument request values and 4-byte ioctl
encodings for pointer-sized macros:

- `0x40046b3b` brightness;
- `0x40046b3c` frame pointer;
- `0xc0046b3d` frame status;
- `0x40046b41` frame size.

The stock kernel's compat forwarding does not translate native command values
or structures. This leaves the 32-bit encodings unmatched by the native
switch. This is a stock quirk, not an ABI to silently redesign.

## Service methods

The stock TinyLCD HAL/service exposes operations corresponding to power,
backlight enable, brightness, frame writes, frame size, gesture enable, and
frame-status polling. Frame data is RGB565 bytes passed unchanged to the
kernel and SPI controller.
