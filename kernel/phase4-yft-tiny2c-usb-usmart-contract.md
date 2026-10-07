# yft_tiny2c_usb relation to uSmart (corrected)

## Classification

**Distinct clients of one USB fabric.** `yft_tiny2c_usb` is not a uSmart controller and
shares no uSmart GPIO or userspace ABI.

| concern | internal Tiny2-C thermal | uSmart external accessory |
|---|---|---|
| physical device | built-in Raytron/InfiRay module | proprietary expansion connector + attached camera/accessory |
| detection | boot I2C 8-003c ID 0x4c59 | GPIO28 LOW/HIGH |
| power | GPIO149/191/192 via `tiny2c_usb_mode` | GPIO152 automatic output |
| route control | board path; no thermal GPIO55 operation | GPIO55 LOW external / HIGH uSmart |
| role | userspace `tiny2c_mode` HOST/NONE | GPIO28 worker HOST/NONE |
| status | `sensor_id`; USB attach | `uvc_insert_status` physical insert |
| userspace | ThermoVue packages/libs | YftSystemUI, FactoryMode, optional `com.endoscope.otgcamera` |

Both reach the single `usb2-phy0`/MTU3/xHCI fabric, so they conflict. There is no live
second USB controller.

`yft_usb_flag` belongs to thermal ownership. In the uSmart worker it is checked only after
GPIO152, GPIO55 and `uvc_insert_status` have already changed; it suppresses the final
HOST/NONE request, not the physical route/power operation. Therefore it is not safe
mutual exclusion.

SC851x is unrelated to both paths. MT6375/GPIO37 source VBUS belongs to external Type-C;
the uSmart ID worker controls only GPIO152 and does not invoke that regulator path.
