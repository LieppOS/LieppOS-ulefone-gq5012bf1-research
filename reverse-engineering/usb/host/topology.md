# Host (OTG) path

```text
Type-C: phone presents Rp, partner Rd → TCPC ATTACHED_SRC
  ├─ TCPC SOURCE_VBUS(5000 mV)
  │    → extcon set_vbus(on): GPIO 37 otg_gpio_select = 1
  │      MT6375 "usb-otg-vbus" regulator: set_voltage 5.25 V, set_current_limit 1.8 A, enable
  │      (vbus_limit_cur sysfs: 0.5 A limit mode, written by the USB HAL limitPowerTransfer)
  ├─ rt_pd_manager: typec port0 data=host, power=source, vconn=source
  └─ extcon role HOST → extcon_wq → usb_role_switch_set_role(HOST)
        → MTU3 ssusb_mode_sw_work_v2: PHY host props → IPPC force-host
          → populate 11200000.xhci0 (xhci-mtk-hcd-v2)
          → usb1 root hub: 1d6b:0002, USB 2.0, 1 port, 480 Mbit/s
          → GKI class drivers (hub, HID, mass storage/UAS, UVC, snd-usb-audio + usb_offload,
            usbnet/cdc_*/r8152… in system_dlkm, usbserial/ftdi/cdc-acm)
```

| item | value |
|---|---|
| USB2 host | **yes**: one root port, HS/FS/LS through the xHCI USB2 port (TT for FS/LS) |
| USB3 host | **no**: `USB3 root hub has no ports` (hardware capability) |
| root hub layout | `usb1` only, `maxchild = 1`. The same port serves the internal camera (GPIO 55 route) and the external receptacle |
| VBUS source | MT6375 boost through the `usb-otg-vbus` regulator (4.85–5.5 V, 0.5–2.4 A). DT asks for 5.25 V / 1.8 A |
| reverse wired charging | uses the **same** Type-C source role + MT6375 boost (battery → SC8510 bridge → 1S rail → MT6375 boost → VBUS). The USB stack sees an ordinary source-role attach. The charging-side analysis is in power-charging research and is not repeated here |
| OTG transitions | detach: SOURCE_VBUS(0) → GPIO 37 = 0, regulator off, `vbus_cur_inlimit = 0`. TYPEC_STATE→UNATTACHED → role NONE → MTU3 waits 100 ms, depopulates xHCI, powers the port off |
| internal camera host | GPIO 28 low → `detect_cable` → GPIO 152 (camera VBUS) = 1, GPIO 55 (D± route) = 1, `uvc_insert_status = 1`, role HOST. Runtime-proven: 3474:4321 at 1-1, 480 Mbit/s. VBUS for the camera does **not** use the MT6375 OTG regulator: ALPS `set_vbus` was removed from `detect_cable` |
| conflict rule | one MTU3, so the external gadget and the internal camera are mutually exclusive. The UDC goes `not attached` while the camera is hosted (runtime capture) |
