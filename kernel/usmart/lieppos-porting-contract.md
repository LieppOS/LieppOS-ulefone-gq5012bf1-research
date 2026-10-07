# LieppOS uSmart porting contract

## MUST reproduce for stock compatibility

1. Configure GPIO28 as input and detect both LOW insertion and HIGH removal, including a
   boot-time sample; LOW is inserted.
2. Initialize GPIO152 and GPIO55 LOW.
3. On insertion, execute **power HIGH → route HIGH → physical-status 1 → HOST**.
4. On removal, execute **power LOW → route LOW → physical-status 0 → NONE**.
5. Use the existing single USB2 PHY/MTU3/xHCI fabric; never model a second USB controller.
6. Preserve a readable physical-insertion status for YftSystemUI/FactoryMode if those
   proprietary binaries are retained (`uvc_insert_status`, values `0\n`/`1\n`).
7. Permit usbcore and Android USB-host permission flow; retain the downloadable camera
   app/libs if compatibility with all vendor-specific accessories is required.
8. Keep uSmart and Tiny2-C controls separate.

## SHOULD fix while preserving observable behavior

- use descriptor GPIO APIs and validate every GPIO;
- debounce GPIO28 and add power/route settle delays based on board validation;
- serialize uSmart, Type-C and thermal ownership under one state machine;
- save and re-evaluate external Type-C state on uSmart removal;
- clear GPIO152/55/status and release HOST on shutdown/remove;
- check role-switch completion and roll back power/route on failure;
- expose an event/uevent rather than world-writable sysfs permissions;
- distinguish physical insert, power-good and enumerated-device state;
- enforce current/inrush protection once board rail limits are known.

## CAN simplify

- rename the misleading UVC-only status ABI if proprietary SystemUI/FactoryMode are not
  shipped;
- drop dead `11211000.usb1`, `reverse_charging_level`, SC851x and thermal cross-links;
- omit YftSystemUI install prompt and FactoryMode UI;
- omit AOA/U-Storage/license/vendor camera paths when only documented standard UVC
  compatibility is promised.

## MUST NOT

- conflate GPIO55/152 with thermal GPIO149/191/192;
- route Type-C and uSmart simultaneously;
- assume MT6375 5.25-V/1.8-A settings describe GPIO152;
- use status=1 as proof of enumeration;
- let a Type-C/thermal event silently overwrite active uSmart ownership without a defined
  conflict policy;
- claim analog audio, display output, reverse charging or universal USB-device support
  without new hardware evidence.
