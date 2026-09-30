# AC020 / InfiRay "vdcmd" transport over UVC — reconstructed wire protocol

Sources of evidence (independent, converging):
1. **OEM stack (this device)** — `libircmd020.so` / `libusbuvccamera020.so` /
   `libdualuvccamera020.so` / `libomniircamera020.so` exports, strings, disassembly
   (`evidence/binaries/symbols/*`, `evidence/binaries/strings/*`, `/tmp/uvc.asm`,
   `/tmp/ircmd.asm`).
2. **Donor RE** — `re/apps/donors/p2pro-viewer` (leodj, independent libusb trace of the
   InfiRay P2 Pro module) which reconstructs the same state machine from a USB capture.

## Layering (VERIFIED from symbol/string evidence)
```
Java  com.energy.ac020library.IrcmdEngine        (typed API, ~441 adv_* wrappers)
  └ native libircmd020.so   ircmd_create_handle / vdcmd.c / standard_cmd_* long_cmd_*
       └ driver abstraction: DriverType = USB(0) SPI(1) MIPI_I2C(2) USB_DUAL(3)
                             MIPI_I2C_DUAL(4) USB_DUAL_NATIVE_CAM(5) USB_OMNI(10)
            └ libusbuvccamera020 / libdualuvccamera020 / libomniircamera020
                 └ bundled libusb fork (…/libusb/libusb/{core,descriptor,io,os/android_usbfs}.c)
                      └ /dev/bus/usb/%hhd/%hhd  (+ legacy /proc/bus/usb/%hhd/%hhd)
```
`libircmd020` itself contains **no** UVC selector constants (`0x1d00/0x1d08/0x1d10/0x9d00/0x9d08`
absent from its disassembly); the packetisation lives in the per-transport libraries. This is a
clean transport/command separation — the AC020 SDK is *not* UVC-specific at the command layer.

## Command framing (EXACT_SYMBOL names from libircmd020)
`vdcmd.c` builds three header kinds, each with a matching error string:
- `vdcmd_std_header`  → `standard_cmd_read`, `standard_cmd_write`,
  `standard_cmd_write_without_read_return_status`
- `vdcmd_short_header` → short command write
- `vdcmd_long_header`  → `long_cmd_read`, `long_cmd_write`
plus `basic_long_time_vdcmd_state_get` (long-command busy polling), `crc16`/`crc8`/`crc32`
helpers (`ircmd_crc16_cal/_cmp`, `ircmd_soft_crc8/16/32`), and `vdcmd_set_polling_wait_time`
(Java: `IrcmdEngine.vdcmdSetPollingWaitTime(long)`).

## UVC control-pipe mapping (corroborated by donor USB trace)
All vendor traffic uses the standard UVC *vendor node* control form, with interface/ETT
`wValue = 0x78` (VS_INPUT_TERMINAL selector base used as vendor slot):
| direction | bmRequestType | bRequest | wValue | wIndex |
|---|---|---|---|---|
| host→device header/data | `0x41` (VENDOR·OUT·IFACE) | `0x45` | `0x78` | selector |
| device→host data/status | `0xC1` (VENDOR·IN·DEVICE) | `0x44` | `0x78` | selector |
| busy/status poll | `0xC1` | `0x44` | `0x78` | `0x200` (1-byte status) |

Selectors observed in the OEM binary too: `uvc.asm` contains 67× `#0x78`, 35× `0x200` and
72 occurrences of `0x44/0x45` — i.e. the identical vendor-request pair and status port.
Donor-derived selector semantics (`p2pro-viewer/P2Pro/P2Pro_cmd.py`):
- `wIndex = 0x1d00` — standard-command **header** write (OUT), payload follows.
- `wIndex = 0x9d00` — long-command header / chunked data write.
- `wIndex = 0x1d08` — short-command payload write; **IN** read of command result.
- `wIndex = 0x9d08` — long payload chunk write (≤ 0x40 per transfer, ≤ 0x100 per command).
- `wIndex = 0x1d10` — long-command result read.
- `wIndex = 0x200`, IN, len 1 — status: ready ⇔ `!(b0&1) && !(b0&2)`; error if `b0 & 0xFC != 0`.

Header layouts (donor-derived, matching the OEM `*_cmd_*` naming):
```
standard write : OUT 0x1d00 ← struct "<H"(cmd LE) + ">I"(param BE) [+ 2 pad]   [then payload via 0x1d08/0x9d08]
standard read  : OUT 0x1d00 ← "<H"(cmd) + ">I"(param BE) + ">H"(len) ; then IN 0x1d08 ×len
long write     : OUT 0x9d00 ← "<H"(cmd) + ">H"(p1) + ">I"(p2) ; OUT 0x1d08 ← ">I"(p3)+">I"(p4)
long read      : OUT 0x9d00 ← same ; OUT 0x1d08 ← ">I"(p3)+">I"(len) ; then IN 0x1d10 ×len
```
After **every** control transfer the host polls `0x200` until ready (`_block_until_camera_ready`,
1 ms spin, 5 s timeout) — matching OEM `polling_time = %d` / `vdcmd_set_polling_wait_time`.

## Command space (confidence-tagged)
- `CmdDir`: `GET = 0x0000`, `SET = 0x4000` (bit 14 = write). Donor-derived, but exactly the
  pattern implied by the OEM's `_get`/`_set` symbol pairs.
- Confirmed-from-donor P2 Pro codes (Mini-series, **likely** common to AC020 family — INFERENCE,
  needs device capture to confirm for AC020): `spi_transfer 0x8201`, `get_device_info 0x8405`,
  `pseudo_color 0x8409`, `shutter_vtemp 0x840c`, `prop_tpd_params 0x8514`,
  `cur_vtemp 0x8b0d`, `y16_preview_start 0x010a`, `preview_start 0xc10f`,
  `…_stop` = same low byte with SET bit cleared, `sys_reset_to_rom 0x0805`.
- OEM-side semantic surface that must map onto these opcodes is the exported `adv_*`/`basic_*`
  set in `libircmd020.so` (441 symbols: FFC/shutter, gain, palette, DPC, RMVC-over-temp,
  env-correction TA/TU/TA/EMS, TNR/DDE/edge/gamma, zoom, cursor, ISO-line, ddr/log, flash
  `adv_cfg_file_*`, `flash_read`, `xmem_init`, `test_flash_*`).
- Device-state enums (Java `CommonParams`, EXACT): `DeviceStatus =
  BASIC_STARTUP(0)/PREVIEW(1)/VIDEO_OUT(2)/UPDATE(3)/ERROR(4)`; `UpgradeMode =
  WHOLE_PACKAGE_ZIP(0)/UPDATE_PACKAGE_ZIP(1)/SINGLE_FIRMWARE_FILE(2)/SYSTEM_CONFIG_FILE(3)`;
  `FirmwareUpgradeCode` spans `RESET_ROOM(2) … FINISH_UPGRADE_WHOLE_DATA(6)`; the
  `fail to switch to rom status!` string pairs with `sys_reset_to_rom = 0x0805`.

## Image plane
Stream is ordinary UVC video: `iruvc start preview`, `do_streams_ioctl`, altsetting select,
`FrameOutputFormat = YUYV(0) | NV12(1) | NV12_AND_TEMP(2) | YUYV_AND_TEMP(3)`; Y16/radiometric
path enabled by `y16_preview_start`-class command (donor) and `ADV_*_SOURCE_MODE` taps.
Sensor geometry recovered from `M170infDlp` `Const`: `IR_SENSOR_WIDTH=256`,
`IR_SENSOR_HEIGHT=386` (= 384 + `IR_SENSOR_LINE_HEIGHT=2` metadata lines), `IR_SENSOR_FPS=25`
⇒ the *cellular* variant ships 256×192-class panels while `WN640/USB_WN_640_512` families
exist for 640×512 modules; the OEM build carries **all** families (see DeviceType).
Frame integrity check string: `broken frame!:format=%d,actual_bytes=%d/%d(...)` ⇒ frames are
validated by expected byte count per format, which is how YUYV vs Y16(+temp) is disambiguated.

## DFU/upgrade side-channel
`libAC020sdk.so` also exports a full `dfu_*`/`dfuse_*` engine + `cJSON` package parser
(`update.json`, `whole_package.json`, `update_package.json`, `split_package.json`,
`dataread.bin`, `EXT.bin`) and `check_status_before_upgrade_package_function/_zip`.
`iruvc_usb_device_open is_dfu = %d, vid = %d, pid = %d, …, format_type = %d` shows the *same*
opening routine handles normal and DFU (ROM) enumeration ⇒ entering `sys_reset_to_rom`
re-enumerates the module and the SDK re-opens it in DFU mode. **Do not exercise without
explicit authorization** (flashing bricks the module).

## Still unproven (needs device-side capture; explicitly NOT attempted)
- Exact AC020 opcode values for each `adv_*` call (only the P2 Pro subset is known).
- The actual `chip_id`/`sensor_id` value and VID:PID of the Armor 29P module.
- Whether `libdualuvccamera020` (dual-lens P2L/X3-style) is used at all on this single-module
  phone (it is shipped, not proven active).
