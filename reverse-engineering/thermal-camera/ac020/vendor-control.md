# Control channels

## UVC standard controls

None of substance: IT and PU advertise `bmControls = 0` and there is no Extension Unit (P).
Standard requests used are only the UVC VS probe/commit negotiation and SET_INTERFACE
(alt 1) performed by the bundled libuvc.

## Vendor control protocol ("vdcmd")

Carried on EP0 with **vendor-type** requests addressed to the VideoControl interface, not to a
UVC unit (this is why no XU is needed). Established in
`qwen_hardware/qwen-thermal/re/protocol/vdcmd-uvc-transport.md`:

| direction | bmRequestType | bRequest | wValue | wIndex |
|---|---|---|---|---|
| OUT header/data | 0x41 | 0x45 | 0x0078 | selector (0x1d00 std header, 0x9d00 long header, 0x1d08 short/payload, 0x9d08 long payload) |
| IN data | 0xC1 | 0x44 | 0x0078 | 0x1d08 (std result) / 0x1d10 (long result) |
| IN status | 0xC1 | 0x44 | 0x0078 | 0x0200, 1 byte, ready ⇔ !(b0 & 3), error ⇔ b0 & 0xFC |

OEM evidence: `libusbuvccamera020.so` holds 67× `#0x78`, 35× `0x200` and the 0x44/0x45 pair;
`libircmd020.so` builds std/short/long headers (`vdcmd_*_header`), CRC helpers and exports
~441 `adv_*`/`basic_*` commands (FFC/shutter, gain, palette, DPC, RMVC, env correction,
TNR/DDE/gamma, zoom, flash/config file, `sys_reset_to_rom`).

### OEM command headers (new, static, from the stock `libircmd020.so`)

`scripts/extract_vdcmd_headers.py` walks every exported `adv_*`/`basic_*`/`sys_*`/`spi_*`/
`test_*` function of FactoryMode's `libircmd020.so` (sha256 `0aa7d5c7…81ad`) and records the
immediate header bytes stored into the buffer passed as `x1` to
`standard_cmd_read/write`, `short_cmd_*`, `long_cmd_*`. Result: `vendor-opcodes.tsv`,
257 call sites in 217 functions, 250 with a complete header (7 reuse a previous header).

Header layout (AC020 encoding, differs from the P2 Pro donor):

| offset | field | observation |
|---|---|---|
| +0 | u16 LE command class | 37 classes; most used 0x0410 (45), 0x1110 (35), 0x1010 (29), 0x0310 (24), 0x0101 device (14), 0x0710 (11), 0x0210 FFC/shutter (10) |
| +2 | u8 sub-command | bits[7:6]: `01` = SET (all 126+10 standard writes), `10` = GET (93/95 standard reads), `11` = control (e.g. `basic_preview_stop` 0xC2, 7 writes) |
| +4.. | u8/u16 parameters | e.g. `adv_shutter_tab_open/close` 0x0F01/0x45 with +4 = 1/0 |

Examples: `basic_device_info_get` 0x0101/0x81; `basic_reset_to_rom` 0x0101/0x42 (no status read);
`basic_ffc_update` 0x0210/0x43; `adv_ffc_without_shutter` 0x1001/0x52; `adv_shutter_status_get/set`
0x0210/0x83 / 0x44; `basic_gain_get/set` 0x2F01/0x81 / 0x41; `basic_palette_idx_get/set` 0x0310/0x85 / 0x45;
`basic_preview_stop` 0x3001/0xC2.

The donor P2 Pro opcodes (`0x8405`, `0xc10f`, …) are therefore **not** the AC020 values;
only the EP0 framing (0x41/0x45, 0xC1/0x44, wValue 0x78, selectors) is shared. What stays
open: mapping the selector/wIndex sequence each `*_cmd_*` emits inside
`libusbuvccamera020.so` for this header format, and parameter/response layouts per command.

## Not used

No I2C (8-003c) command channel, no UART, no hidraw, no custom kernel ioctl.
