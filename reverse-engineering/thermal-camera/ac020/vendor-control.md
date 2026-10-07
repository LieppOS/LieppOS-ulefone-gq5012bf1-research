# Control channels (summary; detail in `vendor-control-protocol.tsv`)

## UVC standard controls

None. IT 1 and PU 2 advertise `bmControls = 00 00 00`, there is no Extension Unit, and no
stock library calls the libuvc control helpers (`uvc_get_*/uvc_set_*` brightness, gain,
exposure, focus, …) or `uvc_get_ctrl/uvc_set_ctrl`. Only VS probe/commit, the VC error-code
query and SET_INTERFACE are issued.

## Vendor control ("vdcmd") — AC020 USB transport (static, from the stock libraries)

Carried on EP0 as **vendor requests to interface 0 with wValue = wIndex = 0**:

```
command  : OUT  0x41  bRequest 0x20  [header(+payload)]
status   : IN   0xC1  bRequest 0x22  1 byte   1=busy  2=data ready  3=done
response : IN   0xC1  bRequest 0x21  n bytes
```

Read = OUT 0x20 header → status must be 2 → IN 0x21 → status must be 3.
Write = OUT 0x20 header+payload → poll 0x22 every ~2 ms while 1, success on 3.
Reset-type commands use OUT 0x20 without status.

Frame header (libircmd020): byte0 frame type (0x01/0x10 standard 18 B, 0x02 short 12 B,
0x03 long 24 B) · byte1 module · byte2 sub-command (bit7 data phase, bit6 SET) ·
params · u32 offset · u16 chunk length · CRC16(payload) · CRC16(header). Data are
chunked ≤ 0x800 bytes per transfer; the offset field advances per chunk.

**Correction:** the earlier table here (0x41/0x45, wValue 0x0078, wIndex 0x1d00/0x9d00/
0x1d08/0x1d10, status at 0x0200) is the P2-Pro donor protocol. In the stock AC020 SDK it
survives only as the unreachable `iruvc_i2c_usb_*` path; the shipping USB path is the
0x20/0x21/0x22 protocol above. The earlier "u16 command class" reading of header bytes 0–1
is also corrected (byte0 = frame type, byte1 = module).

Stock command use: `vendor-opcodes.tsv` (`stock_caller` column). M170infisens issues
device-info, FFC (manual/auto/params/all-FFC), shutter-tab open, gain set (+ SDK
auto-gain get/set/long-time state), mirror/flip, detail-enhance level, sun-detect,
profession mode, NUC-T bypass, ISP param read, algorithm-parameter read/write,
real-time status and calibration-file reads (`adv_cfg_file_*`); M170infDlp adds
calibration (DPC, RMCover, K-value, TPD 2-point), save/restore, FFC/gain get and the
firmware upgrade path. Parameter meanings beyond the vendor symbol names are not claimed.

## Not used

No UVC XU, no HID, no bulk endpoint, no I2C (8-003c) command channel, no UART, no hidraw,
no kernel ioctl.
