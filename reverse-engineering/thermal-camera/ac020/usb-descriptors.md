# 3474:4321 descriptor tree (Tiny2-C firmware 00.00.04.07)

**Primary source F:** the descriptor tables embedded in the stock-shipped module firmware
`firmware_EXT.bin` (sha256 `111e20d822f991eae42b08084f403bf6c75188dc5002869d19e404d20792a8a4`, 701 644 B, md5 `b62475d9…7d02` = the value in
`whole_package.json`), decoded field-by-field by `scripts/parse_fw_usb_desc.py`; full output
in `firmware-descriptor-dump.txt` (descriptor fields only — no firmware bytes are stored).
**S** = stock unit sysfs/logcat capture; **P** = public `lsusb -v` of an identical-identity
unit. Every field below is from F unless marked; S and P agree wherever they report.

```
Device  12 01  bcdUSB 2.00  EF/02/01  MPS0 64  3474:4321  bcdDevice 2.00  iMfr 1 iProd 2 iSer 3
Qualifier 0A 06  bcdUSB 2.00  EF/02/01  MPS0 64
Configuration 1 (header built at run time)  wTotalLength 0x00DF = 9 + 214     [P: 0x00DF, self-powered, 100 mA]
 └ IAD  first 0  count 2  class 0E/03/00 (VIDEO / INTERFACE_COLLECTION)  iFunction 2
 ├ Interface 0  alt 0  0E/01/00 VideoControl  1 EP  iInterface 2 "Camera"
 │   VC_HEADER        bcdUVC 1.10  wTotalLength 53  dwClockFrequency 15 000 000  streaming if [1]
 │   VC_INPUT_TERMINAL  id 1  ITT_CAMERA 0x0201  bControlSize 3  bmControls 00 00 00
 │   VC_PROCESSING_UNIT id 2  source 1  wMaxMultiplier 0  bControlSize 3  bmControls 00 00 00  bmVideoStandards 0
 │   VC_OUTPUT_TERMINAL id 3  TT_STREAMING 0x0101  source 2
 │   (no VC_EXTENSION_UNIT, no selector unit)
 │   EP 0x83 IN interrupt  wMaxPacketSize 64  bInterval 6 (4 ms)
 │     CS_ENDPOINT EP_INTERRUPT  wMaxTransferSize 64
 └ Interface 1  0E/02/00 VideoStreaming  iInterface 0
     alt 0: 0 EP
       VS_INPUT_HEADER  bNumFormats 1  wTotalLength 107  bEndpointAddress 0x81  bmInfo 0
                        bTerminalLink 3  still 0  trigger 0/0  bmaControls[1] 00
       VS_FORMAT_UNCOMPRESSED  index 1  2 frames  GUID 32595559-0000-0010-8000-00AA00389B71 (YUY2)
                               bBitsPerPixel 16  default frame 1  aspect 0:0  progressive  no copy-protect
       VS_FRAME_UNCOMPRESSED   index 1  256×194  bitrate 11 919 360–23 838 720
                               dwMaxVideoFrameBufferSize 99 328   interval 400 000 ×100 ns (25 Hz, discrete, 1 entry)
       VS_FRAME_UNCOMPRESSED   index 2  256×386  bitrate 23 715 840–47 431 680
                               dwMaxVideoFrameBufferSize 197 632  interval 400 000 ×100 ns (25 Hz, discrete, 1 entry)
       VS_COLORFORMAT  primaries 1 (BT.709)  transfer 1 (BT.709)  matrix 4 (SMPTE 170M)
     alt 1: 1 EP
       EP 0x81 IN isochronous asynchronous  wMaxPacketSize 0x0400 (1024 B, 1 transaction/µframe)  bInterval 1
```

Size check: 8 (IAD) + 9 + 53 + 7 + 5 (VC) + 9 + 107 (VS alt 0 + class) + 9 + 7 (alt 1 + EP)
= 214; + 9-byte configuration header = 223 = 0x00DF (P: `wTotalLength 0x00df`).

Firmware-side details (not visible on the bus): the firmware keeps three descriptor blocks
(VC, VS-alt-1, VS-alt-0+class) and patches interface numbers and `bNumConfigurations` at
run time (templates hold 0; the unit enumerates as if1 / 1 configuration — S).

Counts (S, stock unit, 2026-09-23): `1-1:1.0` bInterfaceClass 0e/01, bNumEndpoints 1;
`1-1:1.1` 0e/02, bAlternateSetting 1, bNumEndpoints 1 — matches F.

Bandwidth: alt 1 reserves 1024 B × 8000 µframes/s = 8.19 MB/s; the 256×386 frame stream needs
197 632 B × 25 = 4.94 MB/s (+ 2–12 B UVC payload header per transfer).
