# Host-role path for the internal thermal camera

```
app GPIOUtils.powerControl2("tiny2c_mode", 1)   (FileWriter, "1\n")
  → /sys/class/yft_extcon/tiny2c_mode  store_tiny2c_mode()        [extcon-mtk-usb, class "yft_extcon", 0664 → chmod 0666]
      sscanf %d; 1 → mtk_usb_extcon_set_role(yft_extcon, USB_ROLE_HOST); other → USB_ROLE_NONE
  → kzalloc usb_role_info, queue_delayed_work(extcon_wq, update_role, 0)
  → mtk_usb_extcon_update_role(): cur c_role → HOST
      NONE→HOST:   extcon_set_state_sync(EXTCON_USB_HOST, 1)
      DEVICE→HOST: EXTCON_USB = 0, EXTCON_USB_HOST = 1
      usb_role_switch_set_role(11201000.usb0-role-switch, HOST); c_role = HOST
  → mtu3 role switch → ssusb host mode → xhci-mtk registered on 11200000 → root hub usb1
  → module (already powered) connects → enumeration (enumeration.md)
```

| question | answer | class |
|---|---|---|
| who writes `tiny2c_mode` | M170infisens `com.energy.tc2c` / M170infDlp `com.energy.tc2c.sop` `GPIOUtils`, FactoryMode `InfirayEcoTest` (onCreate 1 / onDestroy & error 0), `services.jar` crash cleanup (0) | PROVEN |
| when | immediately after `tiny2c_usb_mode` = 1 (start) / after `tiny2c_usb_mode` = 0 (stop) | PROVEN |
| values | 1 = HOST, anything else = NONE; read always returns `0` (`yft_tiny2c_status` is never assigned — stock bug) | PROVEN |
| gated by `yft_usb_flag`? | **no** — the store always queues the role. The flag gates only the *other* role sources (TCPC notifier, power-supply detector, GPIO 28 detect work) | PROVEN |
| does it touch VBUS / GPIOs | no: no GPIO 37/55/152 change, no `usb-otg-vbus` regulator call | PROVEN |
| MT6375 boost | not used for the internal camera (OTG VBUS is only driven by the TCPC `SOURCE_VBUS` event) | PROVEN |
| camera power source | its own rails GPIO 149/191/192 (`yft_tiny2c_usb`), independent of Type-C VBUS | PROVEN |
| `yft_usb_flag` effect while 1 | extcon: Type-C SRC/SNK attach, plug-out and DR_SWAP role changes ignored ("yft_drv ignore usb func"); psy detector ignored; GPIO 28 detect work returns before role change. mt6375-charger: `mt6375_chg_set_usbsw` does not switch the USB2 PHY into BC1.2 mode; PD `PE_READY_SNK*` requeues BC1.2 work | PROVEN (exact sources) |
| not gated | `TCP_NOTIFY_SOURCE_VBUS` (OTG VBUS on/off, GPIO 37) still runs; `tiny2c_mode` itself | PROVEN |
