# thermal-camera — STATUS

| component | status | summary |
|---|---|---|
| FM78100-COMPANION (8-003c) | **DONE (static)** | identity resolved (module ASIC I2C slave, FM78100 retracted); full I2C map (2 reads); role = boot ID; power/USB sequence; `yft_tiny2c_usb.ko` 11/12 functions byte-identical, data/ABI/strings exact, B1==B2 |
| AC020-UVC | **DONE (static)** | 3474:4321 UVC 1.10, descriptors decoded from stock module firmware 00.00.04.07 (if0 VC + 0x83 int, if1 VS alt1 0x81 iso 1024 B; YUY2 256×194/256×386 @25 Hz; no XU, no PU/IT controls); stock negotiates 256×386 = image + 2 info lines + u16 temperature; GKI uvcvideo → usbfs, no custom driver; vendor EP0 protocol 0x41/0x20 cmd, 0xC1/0x22 status, 0xC1/0x21 data (donor 0x45/0x78 path unreachable); command header table with stock callers |
| INTERNAL-THERMAL-USB | **DONE (static)** | integration: boot rails 149→191→192 + 400 ms + I2C ID 0x4c59 + rails off; runtime `tiny2c_usb_mode`=1 (rails, `yft_usb_flag`=1) → `tiny2c_mode`=1 (role HOST) → 3474:4321 on 1-1 after ~0.73 s → uvcvideo → usbfs claim; stop rails-off → role NONE; GPIO 55/152 = uSmart; single fabric, external role not restored (`internal-usb/`) |
| THERMOVUE-T2 transport boundary | mapped (see `ac020/`) | open transport = UVC/usbfs + vdcmd (closed in AC020-UVC); proprietary = radiometry/processing libs + MNN SR |
