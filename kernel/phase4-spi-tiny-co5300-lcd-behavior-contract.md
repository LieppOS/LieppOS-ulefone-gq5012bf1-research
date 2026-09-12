# Phase 4 `spi_tiny_co5300_lcd` behavioral contract

## Evidence and scope

This contract is reconstructed statically from the frozen stock ELF
`workspace/phase4-spi-tiny-co5300-lcd/oracle/spi_tiny_co5300_lcd.stock.ko`,
its relocation-aware disassembly, the stock DT, and the 32/64-bit stock
`tinylcd.default.so` implementations. It requires no live device operation.

## Controller and geometry

The executable behavior identifies a CO5300-class 340x340 RGB565 panel:

- full address window: columns/rows `0x0000..0x0153` (340 pixels);
- alternate frame window: columns/rows `0x000a..0x0149` (320 pixels,
  centered by ten pixels);
- full frame: `340 * 340 * 2 = 231200` bytes;
- alternate frame: `320 * 320 * 2 = 204800` bytes;
- pixel format command `0x3a` carries `0x55` (RGB565);
- controller identity is read with commands `0xda` and `0xdb`;
- accepted primary ID is `0xda == 0x33`;
- `0xdb == 0x11` selects `tiny_lcm_number = 1`, while `0xdb == 0x10`
  selects `tiny_lcm_number = 2`.

The module-description text `SSD1317 96*96 OLED` is stale copied metadata. It
is incompatible with the executable 340x340 RGB565 data path and must not be
used as the runtime geometry/controller oracle.

## Exact initialization stream

`init_setting` is exactly 44 records of 28 bytes. Each record is:

```c
struct init_record {
    u32 command;
    u8 count;
    u8 parameters[23];
};
```

Command `0xfffc` is a delay pseudo-command; `count` is milliseconds. Other
records send one command byte and `count` data bytes. The binary table is
frozen at:

- `workspace/phase4-spi-tiny-co5300-lcd/tables/init_setting.bin`
- length: 1232 bytes
- SHA256: `908e91b61b0e1e5cdb1f618bc3f605bb08ec39608902de27f7aa6a5fb23fd0ff`

The decoded table is in
`kernel/phase4-spi-tiny-co5300-lcd-register-map.tsv`. Reconstruction must
preserve the table byte-for-byte, including delays and page-switch/unlock
writes.

## SPI transfer contract

- DT controller: MT6989 SPI at `0x11010000`, chip select 0.
- DT maximum frequency: 60 MHz.
- Stock sets mode 3 and 8 bits per word.
- Command/data/frame writes set transfer speed to exactly 52 MHz.
- Register reads set transfer speed to exactly 1 MHz.
- DC is driven low for commands/reads and high for parameter/frame data.
- A register read is one full-duplex two-byte transfer `{command, 0}` and
  returns RX byte 1.
- A command or one-byte parameter is one one-byte SPI transfer.
- A frame is copied into a temporary `vmalloc(len)` buffer and submitted as
  one SPI transfer; stock performs no RGB565 byte swap or chunking.
- `spidev_sync_write_multi_data()` serializes frame transfers with a mutex.
- The first transfer for a new source pointer writes command `0x51`, the low
  byte of the cached brightness, then command `0x2c`.
- A changed frame width reprograms `0x2a`/`0x2b`, sends `0x2c`, and caches the
  width. Only `(320, 204800)` and `(340, 231200)` receive known windows.

## TE and frame state machine

`write_frame_status` is a 64-bit value initialized to 1:

- `1`: idle/completed;
- `3`: a frame is pending for the next TE work item;
- `0` and `2`: legacy/debug results used by the sysfs frame trigger path.

The TE GPIO uses a falling-edge hard IRQ. The IRQ schedules
`tiny_lcd_te_work` immediately on `system_wq` using
`queue_delayed_work_on(WORK_CPU_UNBOUND, ..., 0)` when the panel-power flag is
1. Work sends only when status is 3 and both `frame_send_enable == 1` and
`frame_send_end != 0`; it then always returns status to 1. Width 320 sends
204800 bytes, otherwise it sends 231200 bytes.

`TINY_LCM_IOC_WRITE_FRAME` first sets status 2. When frame sending is enabled,
it copies exactly 231200 bytes from userspace to `gImage_logo`. A partial copy
zeros the uncopied tail, sets status 3, and returns `-1`. A complete copy sends
immediately only when `frame_send_end == 0`; otherwise it sets status 3 for TE
work. When frame sending is disabled it does not copy and sets status 3.

`TINY_LCM_IOC_FRAME_SIZE` copies two 32-bit dimensions. The stock default is
`{340, 340}`. Width controls the 320/340 transfer length choice; the height is
reported and cached but does not independently size the transfer.

The embedded mutable frame buffer `gImage_logo` is exactly 231200 bytes,
SHA256 `c1a917c583dd698be389e7bf7bbc638dafc58fbdb0e04dd44644a459b37761cf`.

## Power state machine

Power state is guarded by a one-byte panel flag.

Power-off from state 1:

1. disable TE IRQ once and remember that it was disabled;
2. clear cached brightness transfer identity;
3. send display-off `0x28`; delay 20 ms;
4. send sleep-in `0x10`; delay 220 ms;
5. reset GPIO low; delay 20 ms;
6. 2.8 V enable low; delay 20 ms;
7. 1.8 V enable low; delay 20 ms;
8. select MOSI/MISO/CLK/CS GPIO pinctrl states;
9. clear the panel-power flag.

Power-on from state 0:

1. select MOSI/MISO/CLK/CS SPI pinctrl states;
2. delay 20 ms;
3. 1.8 V enable high; delay 20 ms;
4. 2.8 V enable high; delay 20 ms;
5. reset high 15 ms, low 30 ms, high 120 ms;
6. replay the exact 44-entry initialization table;
7. set power flag and `frame_send_end` to 1;
8. if the off path disabled TE IRQ, re-enable it and clear that marker.

A nonzero request while already powered does not reinitialize the panel; it
sets `frame_send_end = 1`. The ioctl AOD path calls the same nonzero power-on
entry and then sets `frame_send_end = 0`.

## Probe and lifecycle

Probe obtains six GPIOs (reset, 1.8 V, DC, 2.8 V, backlight-control, TE), all
eight SPI/GPIO pinctrl states, two 4096-byte transfer buffers, and the named
IIO channel `tiny_lcd_adc`. It checks the ADC processed value is in
`451..999` mV, performs the controller ID reads, maps the TE GPIO to an IRQ,
requests the falling-edge IRQ, replays initialization, initializes delayed
work, creates five SPI-driver attributes, and registers `tiny_lcd_miscdev`.
It then marks the panel used with:

```c
yft_set_tinylcd_device_used("spi_tiny_lcd_co5300", 1);
```

The five driver attributes are mode 0644:

- `tiny_lcd_power_enable`
- `tiny_lcd_bl_enable`
- `tiny_lcd_backlight_control`
- `tiny_lcd_write_frame`
- `tiny_lcd_tp_control`

Remove only logs and deregisters the misc device; stock does not symmetrically
remove attributes, cancel work, free IRQ/GPIO/buffers, or power down.

Module init first calls `yft_tinylcd_device_add(&spi_tiny_lcd_driver, 0)`. It
reads `atag,boot` under `/chosen@0` or `/chosen`; boot modes 1, 5, 6, 8, and 9
skip SPI-driver registration. Missing boot-tag data and all other modes proceed
with registration. Module exit unregisters the SPI driver.
