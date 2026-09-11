# yft_tiny2c_usb USB contract

## Direct module interaction matrix

| subsystem | direct import/call/phandle? | stock behavior |
|---|---|---|
| USB core | no | no USB-device/interface/host APIs |
| USB role switch | no | handled by separate extcon driver |
| extcon | no | paired only by userspace writes |
| Type-C / TCPC | no | no TCPC notifier or Type-C API |
| VBUS / OTG regulator | no | no regulator/charger call; platform 5-V GPIO absent |
| USB PHY / DPDM | indirect data flag only | `yft_usb_flag` makes MT6375 charger avoid ordinary PHY/BC1.2 transition |
| gadget | no | none |
| host mode | no direct call | extcon/USB1 establishes the host route separately |
| UVC | no kernel implementation | AC020 UVC handled by USBMonitor/libusb userspace |
| camera reset | no distinct reset | three populated rail enables are toggled together |
| port selection/mux | no direct GPIO/API | extcon `tiny2c_mode` owns route work |

There are **no direct USB-core imports** among the module's 22 undefined ELF symbols.
The word `usb` names the powered endpoint and cross-driver exclusion state: the low-voltage
rails make the internal USB thermal module available, while the provider flag prevents
MT6375 charger BC1.2 PHY handling from colliding with that route.

## State transitions

- Probe: rails raw-high; dynamic I2C registration/chip-ID probe; rails raw-low. The provider
  flag is not changed during probe.
- Store 1: io3v3, optional 5v slot, 3v3, 1v8 raw-high; then `yft_usb_flag=1`.
- Store 0 or unparsable input: same order raw-low; then `yft_usb_flag=0`.
- Store other integer: no rail/USB-flag change; log failure; return full count.

No call in this module enables VBUS, OTG, reverse charging, Type-C source mode, a USB role,
or a gadget. Those effects, when needed for thermal enumeration, are caused by the separate
userspace write to `/sys/class/yft_extcon/tiny2c_mode` and are outside this module's ABI.
