# Stale / corrected uSmart claims

| # | stale claim | correction |
|---:|---|---|
| 1 | uSmart and Tiny2-C/FM78100 are one physical module | uSmart is an external connector/accessory family; Tiny2-C is the internal thermal module; no FM78100 is fitted |
| 2 | GPIO55/152 belong to thermal | GPIO55 route and GPIO152 power belong to uSmart; thermal rails are 149/191/192 |
| 3 | `tiny2c_usb_mode`/`tiny2c_mode` are uSmart interfaces | thermal-only; uSmart hardware transitions are automatic from GPIO28 |
| 4 | YftSuperScreen is a `tiny2c_*` writer/uSmart controller | false: strings are in a bundled framework stub; app-owned code does not access them |
| 5 | M170infisens/M170infDlp control uSmart | they control internal thermal only |
| 6 | `uvc_insert_status=1` proves UVC enumeration | it is assigned directly from GPIO28 before HOST/enumeration and remains 1 on failure/unsupported devices |
| 7 | uSmart ID work exits before GPIO changes when thermal flag is set | gate is after GPIO152, GPIO55 and status; only the role request is skipped |
| 8 | uSmart removal during thermal leaves power/route/status stale | removal clears all three, but leaves role HOST due the flag |
| 9 | thermal flag suppresses Type-C SOURCE_VBUS | it suppresses selected role/BC1.2 paths, not SOURCE_VBUS |
| 10 | MT6375 OTG regulator directly powers uSmart | no regulator call occurs in ID work; only GPIO152 is proven; MT6375/GPIO37 is external Type-C source VBUS |
| 11 | GPIO152 voltage/current is 5.25 V/1.8 A | those DT values belong to MT6375 Type-C boost; uSmart rail rating is unknown |
| 12 | SC851x owns uSmart/reverse power | no import, DT phandle or userspace edge; unrelated |
| 13 | live `11211000.usb1` controller carries uSmart | dead legacy path; uSmart uses shared USB0/MTU3/U2/xHCI |
| 14 | uSmart and external Type-C can be active independently | one GPIO55 route and one role; no simultaneous data |
| 15 | uSmart-specific gate protects its HOST role from Type-C | none exists; later Type-C event can override the role while route stays uSmart |
| 16 | all uSmart accessories are generic UVC | stock app supports UVC plus Sonix/NS108x/U-Storage proprietary paths; exact product mapping is uncaptured |
| 17 | uSmart camera uses Android V4L2 | stock app passes UsbManager fd into bundled libusb/libuvc over usbfs; no `/dev/video` path |
| 18 | uSmart supports display output because of YftSuperScreen | no display/DP path; YftSuperScreen is unrelated screenshot/screen recording |
| 19 | uSmart has analog audio | no analog route/pins proven; generic digital USB Audio is only a host-stack capability |
| 20 | Android Open Accessory filter proves uSmart AOA | AOA requires the phone's gadget/device role; uSmart unconditionally makes the phone HOST |
| 21 | userspace must enable uSmart at boot | probe samples GPIO28 and performs power/route/HOST autonomously |
| 22 | removal restores the previous external USB state | removal forces NONE and does not re-evaluate Type-C; replug/event may be required |
