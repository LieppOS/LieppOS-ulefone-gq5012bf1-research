# Accessory protocol, audio and video boundary

## Connector/kernel protocol verdict

There is **no proprietary uSmart bus protocol** in the kernel. The complete phone-side
board protocol is:

1. active-low digital insertion detect;
2. active-high accessory power gate;
3. active-high USB2 route select;
4. standard USB HOST enumeration.

No I2C/SPI/UART commands, authentication, accessory ID resistance table, VID/PID gate or
uSmart-specific ioctl is present.

## Userspace accessory protocols

The downloadable stock camera app supports more than plain UVC:

| path | evidence | verdict |
|---|---|---|
| generic UVC | `UsbManager` fd → `libusb100` + `libuvc` + `libUVCCamera`; class-14 filters and UVC controls | standard USB/UVC over usbfs; no V4L2 |
| Sonix ASIC | Java control transfers request types 33/161, requests 1/129, index 768 for register read/write | proprietary accessory command layer |
| NS108x | `libns108x-lib.so`, `com.norelsys.ns108x*` API | proprietary optional device path |
| U-Storage | `libUStorageDeviceFS.so`, bulk/control handling, AOA filter for i4season U-Storage | proprietary optional app path; AOA itself cannot use uSmart HOST route |
| license data | USB bulk/license parser exists, but build-time `LICENSE_CHECK=false` | dormant policy path |

Thus proprietary protocols **remain inside optional camera/accessory app support**, not in
the uSmart connector or kernel contract. Without a captured E01/E02/E03/C01 descriptor,
which accessories require them is unknown. Retaining the stock APK/libs preserves those
paths; a clean LieppOS implementation may support standard UVC first and explicitly bound
vendor compatibility.

## Audio

No analog-audio switch, codec route or dedicated audio pin is visible. Generic USB Audio
Class can enumerate through the USB2 host stack. The camera app records audio with Android
`AudioRecord` and marks 0c45:6366 as needing recording, but this does not prove analog
uSmart audio or a dedicated accessory audio contract.

## Display/video

uSmart is camera **input**: UVC/vendor frames are previewed and recorded locally. There is
no display-output, DP, HDMI or screen-casting transport through the connector.
`YftSuperScreen` is an unrelated screenshot/screen-record utility; its name is not evidence
of uSmart display support.
