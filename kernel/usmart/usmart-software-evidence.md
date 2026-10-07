# uSmart software evidence ledger (corrected 2026-10-07)

Canonical closure: [`README.md`](README.md).

## Exact kernel/DT evidence

- DT `/extcon-usb`: `id-gpios` GPIO28, `uvc_switch_gpio` GPIO55,
  `uvc_vbus_gpio` GPIO152, flags 0.
- Exact `extcon-mtk-usb` source: output defaults LOW; GPIO28 LOW sets
  152→55→status=1→HOST, HIGH sets 152→55→status=0→NONE.
- IRQ: both edges, threaded ONESHOT, zero-delay work, no debounce.
- `uvc_insert_status`: 0444, `%d\n`, no store; init chmod 0777; SELinux
  `yft_fmt_device`.
- Existing USB closure: the one USB2 route is `usb2-phy0`/MTU3/xHCI; legacy
  `11211000.usb1` init/fstab text is dead.

## Complete userspace literal/caller audit

Raw stock scan finds the `uvc_insert_status` literal in YftSystemUI, init and SELinux.
FactoryMode's split/decompiled `EndoscopeCustomTest` implements the corresponding reader
and is declared in its manifest.

| artifact | exact behavior |
|---|---|
| YftSystemUI `SystemUIService` | on USB attach/detach, read status; if 1, not FactoryMode and any UsbManager device exists, prompt only when `com.endoscope.otgcamera` is missing |
| FactoryMode `EndoscopeCustomTest` | after USB attach, require status 1 + non-empty device list; show first VID/PID; detach clears UI |
| FactoryMode `EndoscopeTest` | launches `com.endoscope.otgcamera/.initframe.ListenPopupActivity` |
| `uSmartCamera.apk` | downloadable resource, package `com.endoscope.otgcamera`; consumes Android USB broadcasts/fd, not status sysfs |
| YftSuperScreen | no genuine uSmart/tiny2c caller; prior match was bundled framework stub code |
| ThermoVue apps/services | tiny2c thermal only, not uSmart |

## Camera-app evidence

SHA256 `359d150a291b92d493feb2df78fbc27d9e487ed6bfff6ebee358ecd8c31d93da`,
version 1.0.081. It bundles arm64 `libusb100`, `libuvc`, `libUVCCamera`,
`libns108x-lib` and `libUStorageDeviceFS`. `UVCCamera.open` passes the
`UsbDeviceConnection` fd/bus/device to native libusb; no `/dev/video` or V4L2 literal is
present. Device filters and vendor paths are inventoried in `accessory-enumeration.md` and
`accessory-protocol.md`.

## Correct negative boundaries

- SC851x has no uSmart control/power edge.
- `reverse_charging_level` has no driver node.
- `tiny2c_*`, sensor ID and GPIO149/191/192 are thermal only.
- MT6375 `vbus-supply` belongs to the same driver's Type-C SOURCE_VBUS path, but the
  uSmart ID worker does not invoke it. Only GPIO152 is proven for uSmart power.
- No uSmart display output, analog audio, I2C/SPI/UART or dedicated daemon/HAL exists.
