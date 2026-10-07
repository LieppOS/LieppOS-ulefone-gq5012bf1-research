# Internal thermal USB — hardware / logical path

```
Tiny2-C module (Raytron/InfiRay TC2-C; its own ASIC is the USB device, no bridge)
  rails: VDDIO 3.3 V ← GPIO 149, VDD 3.3 V ← GPIO 191, VDD 1.8 V ← GPIO 192   (yft_tiny2c_usb)
         VDD 5 V: optional DT slot `tiny2c_usb_vdd_5v` absent → not software-switched
  I2C side: i2c-8 / 0x3c (ID 0x4c59, boot-only)                           (FM78100-COMPANION)
  USB side: D+/D− (USB 2.0 HS)
      │  board routing — no software-controlled thermal mux (see below)
      ▼
  MT6878 XS-PHY u2port0 (usb2-phy0@11f40000, the only USB PHY port)
      ▼
  MTU3 11201000.usb0 (dr_mode otg, usb-role-switch, force-vbus)  ← role from extcon-mtk-usb
      ▼ (populated only in HOST role)
  xHCI 11200000.xhci0 (xhci-mtk) → root hub usb1 1d6b:0002 (480 Mbit/s, single USB2 root hub)
      ▼ port 1 (no hub)
  usb 1-1 = 3474:4321 "Thermal Cam Co.,Ltd" "Camera", high-speed, UVC 1.10      (AC020-UVC)
```

| element | fact | class |
|---|---|---|
| controller | the one MTU3/xHCI pair; no second controller (`11211000.usb1` has no live DT controller; its `mode` chmod in init.yft.rc is a dead legacy line) | PROVEN (DT, capture) |
| topology | `1-1` directly on root port 1, no hub | PROVEN (capture) |
| speed | 480 Mbit/s; no SS root hub, no USB3 PHY (USB kernel stack DONE) | PROVEN |
| thermal-specific mux GPIO | **none**. The only route/power GPIOs in the USB DT node are `uvc_switch_gpio` 55, `uvc_vbus_gpio` 152 (uSmart, GPIO 28 ID path), `otg_gpio_select` 37 (Type-C OTG VBUS). In the captured thermal session `uvc_insert_status=0`, which is set together with GPIO 55/152 = 1 and only by the GPIO 28 path → GPIO 55/152 were low while the camera streamed | PROVEN |
| what selects the thermal D+/D− | not any software-visible signal other than the module rails; the board either wires the module to the shared pair or switches it with logic tied to the rails/USB power state | BOARD-ONLY (part/net not visible; does not affect software behaviour) |
| VBUS to the module | none from the phone's Type-C path: thermal start does not touch GPIO 37 / MT6375 `usb-otg-vbus`; the module runs from its own rails; MTU3 uses `force-vbus`, so host/device logic does not need VBUS sensing | PROVEN (code + capture: no Type-C partner, power_role sink) |
| coexistence with external data | impossible in software: one PHY port, one role switch; thermal start forces HOST and the external gadget drops (`external-usb-interaction.md`) | PROVEN |
