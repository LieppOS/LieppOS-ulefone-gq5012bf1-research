# 3474:4321 descriptors

Two sources, kept separate:

- **S** = this GQ5012BF1 unit, stock, read-only sysfs capture
  (`usb-research/evidence/thermal-camera-transition-sysfs.txt`, `thermal-camera-enumeration-log.txt`).
- **P** = public `lsusb -v` of a different unit with the identical identity
  (VID/PID, bcdDevice 2.00, strings incl. serial "202206223"):
  <https://github.com/leswright1977/PyThermalCamera/issues/22> (Tiny2-C based TC001-class camera).
  Used only where S is silent; marked accordingly.

| field | value | source |
|---|---|---|
| bcdUSB / speed | 2.00 / high-speed (480) | S |
| idVendor:idProduct / bcdDevice | 3474:4321 / 2.00 | S |
| strings | Mfr 1 "Thermal Cam Co.,Ltd", Product 2 "Camera", Serial 3 "202206223" | S |
| device class | EF/02/01 (IAD) | S |
| bMaxPacketSize0 | 64 | P |
| configuration | 1 config, wTotalLength 0x00DF, 2 interfaces, self-powered, MaxPower 100 mA | P |
| IAD | first 0, count 2, class 0E/03 | P |
| if 0 | VideoControl 0E/01, alt 0, 1 EP | S (EP count), P (details) |
| VC header | UVC 1.10, dwClockFrequency 15 MHz | S (1.10), P |
| VC units | IT 1 (camera sensor, bmControls 0), PU 2 (bmControls 0), OT 3 (USB streaming); **no Extension Unit** | P |
| VC endpoint | 0x83 interrupt IN, 64 B, bInterval 6 | P |
| if 1 | VideoStreaming 0E/02; alt 0 = 0 EP, alt 1 = 1 EP | S |
| VS input header | 1 format, bEndpointAddress 0x81, bTerminalLink 3 | P |
| format 1 | uncompressed, GUID `32595559-…` (YUY2), 16 bpp | P |
| frame 1 | 256×194, 400000 ×100 ns (25 Hz), max buffer 99328 | P |
| frame 2 | 256×386, 25 Hz, max buffer 197632 | P |
| color matching | BT.709 / BT.709 / SMPTE 170M | P |
| streaming EP | 0x81 isochronous asynchronous IN, 1×1024 B, bInterval 1 (alt 1) | P (S confirms 1 EP in alt 1) |

Cross-checks from stock software (S-side, static): M170infDlp
`IR_SENSOR_WIDTH 256`, `IR_SENSOR_HEIGHT 386`, `IR_SENSOR_LINE_HEIGHT 2`, `IR_SENSOR_FPS 25`,
`IR_SENSOR_BANDWIDTH 1.0`; FactoryMode 256×384 YUYV+temperature. Frame 2 = 192 image lines +
192 temperature (Y16) lines + 2 metadata lines; frame 1 = image + 2 lines.

Not captured on this unit (would need a passive `lsusb -v`/descriptor read after stock
power-up): bMaxPacketSize0, raw config bytes, frame list. Everything else above is
consistent between S and P.
