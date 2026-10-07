# Accessory enumeration and supported-device boundary

No existing device capture identifies the descriptors of an E01/E02/E03/C01 attached to
this phone. The kernel state machine accepts any USB2 device; support must be separated
into three levels.

## 1. Kernel capability

Once HOST, xHCI/usbcore can enumerate standard USB2 classes. This does not mean every
class is a supported uSmart product.

## 2. Factory acceptance

`FactoryMode.EndoscopeCustomTest` waits for `USB_DEVICE_ATTACHED`, requires
`uvc_insert_status == 1`, then accepts **any non-empty UsbManager device list** and shows
the first device's VID/PID. It does not check class, VID/PID, UVC interfaces or stream.
The separate `EndoscopeTest` launches
`com.endoscope.otgcamera/.initframe.ListenPopupActivity`.

## 3. Stock downloadable camera app

`system/media/resource/Download/uSmartCamera.apk`:

- package `com.endoscope.otgcamera`, version 1.0.081;
- not installed under `/system/app` or `/system/priv-app`; no automatic installer
  reference was found;
- Android USB host attach filter accepts class 14 (UVC) and broad additional classes;
- generic camera path is Serenegiant UVCCamera: `UsbManager.openDevice` fd →
  `libusb100`/`libuvc`/`libUVCCamera` over usbfs; no `/dev/video*`/V4L2 path;
- optional native/vendor stacks include NS108x and U-Storage plus Java Sonix ASIC
  control transfers.

Static device-filter entries (expected app support, **not observed uSmart descriptors**):

| type | entries |
|---|---|
| class filters | 0xEF/2, UVC 0x0E/9 and 0x0E any, communications 0x02/0, still image 0x06, class 0x27 |
| filter values encoded decimal (shown here in hex) | 2565:12e4, 046d:08b5, 0581:0280, 240c:0102, 1b71:3002 |
| hexadecimal entries | 05e1:0408, eb1a:2861, 1c88:0007/003c/003d/003e/003f/1001 |
| product-name recognition | `inskam-101`…`108`, `201`…`204`, `302`, `312`, `315`, `316`, `USB2.0 PC CAMERA`, `USB 2.0 Camera`, `USB Composite Device` |

The app's license gate is statically disabled. One 0c45:6366 case enables audio
recording behavior, but that does not prove a dedicated uSmart audio product.

**Supported conclusion:** stock integration is intentionally camera/endoscope-oriented
and supports generic UVC plus several vendor device families. HID, storage, serial and
USB audio may enumerate generically, but no stock uSmart UI contract for arbitrary such
devices is proven. AOA accessory filters in the app are a separate Type-C/device-role
path and cannot run through uSmart's phone-HOST route.
