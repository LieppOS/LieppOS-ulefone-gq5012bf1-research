# External OTG host mode

```text
external Type-C device presents Rd
  → MT6375 TCPC ATTACHED_SRC
    ├─ TYPEC_STATE → extcon role HOST
    │    → EXTCON_USB_HOST=1 → usb_role_switch_set_role(HOST)
    │      → MTU3 PHY_MODE_USB_HOST, force IDDIG host
    │      → populate xHCI 11200000.xhci0
    │      → usb1 root hub 1d6b:0002, one USB2 port, 480 Mbit/s
    └─ SOURCE_VBUS(mv!=0) → GPIO37=1
         → MT6375 `usb-otg-vbus`: 5.25 V, 1.8 A, enable
```

The Type-C role and SOURCE_VBUS are separate notifier events. VBUS is fixed by DT at
5.25 V (the notifier voltage is reduced to on/off), so host source output is 5-V-class
only; PD source-voltage escalation is not implemented in this extcon path. The USB HAL's
`limitPowerTransfer` toggles the current limit between 0.5 A and 1.8 A while boost is on.

On detach, SOURCE_VBUS(0) drives GPIO37 low and disables the boost; TYPEC_STATE queues
NONE. MTU3 leaves host, waits 100 ms for device removal (USB-audio accommodation),
depopulates xHCI, powers the U2 port down and switches to OFF.

## Enumeration ownership and class support

xHCI/usbcore enumerate the device; generic Linux drivers bind. Android system_server's
USB host monitor/`UsbHostManager` exposes attach/detach and permissions to apps. There is
no VID/PID allow-list in extcon, MTU3 or xHCI; Android app permissions and feature policy
are above enumeration.

Stock modules/config visibly support the usual USB2 classes without enumerating every
generic driver: hubs, HID, mass storage/UAS, UVC cameras, digital USB audio (including
MediaTek ADSP offload), CDC ACM/USB serial, and Ethernet (`usbnet`, CDC variants, r8152,
ASIX). Performance is bounded by High-Speed; FS/LS devices work through the U2 root port
(and hub transaction translators where applicable).

Passive analog Type-C audio is unsupported. A digital USB Audio Class adapter/headset is
an ordinary host device and is supported. Android Open Accessory mode is the opposite
role—the phone is a gadget/device—and is described in `device-mode.md`.
