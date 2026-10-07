# Stale / corrected external-USB claims

| # | stale claim | correction / proof |
|---|---|---|
| 1 | USB3 might be dormant and need a certified cable/PCB inspection | controller hardware reports zero U3 device and host ports, trunk 0x1008 U2 IP; xHCI has no USB3 protocol port |
| 2 | replacing only the USB daughterboard or editing DT could enable USB3 | impossible without a different controller + U3 PHY + full lane/mux board design |
| 3 | board SS traces/contact population remain a blocker | moot: there is no controller U3 port to route |
| 4 | GPIO55/152 are the internal thermal camera route/power | they are uSmart GPIO28 accessory route/power; Tiny2-C rails are GPIO149/191/192 |
| 5 | `tiny2c_mode` is a D+/D− mux | it only queues MTU3 HOST/NONE; it has no GPIO or VBUS side effect and reads 0 due a stock bug |
| 6 | internal thermal USB and external Type-C are independent | they share one U2 PHY/MTU3 role; thermal steals HOST and suppresses external events |
| 7 | returning from thermal automatically restores the prior PC/device state | stock forces NONE and does not replay the attached sink state; replug is usually required |
| 8 | Type-C sink attachment directly selects DEVICE in extcon | DT sets `bypss-typec-sink=1`; DEVICE comes from MT6375 power-supply classification (SDP/CDP, unknown TYPE=USB, PD-as-CDP) |
| 9 | data role, power role and VBUS are one atomic role | separate Type-C/extcon notifications and state machines; PR_SWAP does not directly change data role |
| 10 | MTU3 sources host VBUS | MTU3 has force-vbus and no vbus supply; extcon controls GPIO37 + MT6375 `usb-otg-vbus` |
| 11 | uSmart uses MT6375 OTG boost | uSmart uses separate GPIO152 power and GPIO55 route; Type-C boost is independent |
| 12 | passive analog USB-C audio is available because TCPC detects audio accessory | detection exists, but there is no analog switch/codec route; only digital USB Audio Class host works |
| 13 | template DisplayPort node means DP Alt Mode works | no DP transmitter/PHY, lane mux/redriver or SS lanes; DP is nonfunctional |
| 14 | USB-C can carry Thunderbolt/PCIe/SuperSpeed video | no U3/DP/tunneling fabric exists |
| 15 | `/soc/11211000.usb1` is a second external/accessory controller | no such live DT platform device; init chmod is dead; all paths use 11201000.usb0 |
| 16 | USB HAL performs normal attach-role decisions | kernel TCPC/charger/extcon does automatic selection; HAL queries status and handles explicit requests/data enable |
| 17 | every built gadget function is externally exposed | only init-linked compositions are exposed; HID is created but never linked, UVC/ECM/EEM are kernel-available but unconfigured |
| 18 | captured ADB-only gadget is the immutable/default user composition | it is one runtime state; production is `user`, ADB depends on framework/developer/persisted config |
| 19 | Android Open Accessory and uSmart are the same "accessory mode" | AOA is a gadget protocol with the phone as USB device; uSmart is a physical GPIO-routed host accessory |
| 20 | exact bootloader fastboot details follow from Android/recovery config | only recovery/fastbootd properties are recovered; pre-Android bootloader descriptors remain bounded, not assumed |
| 21 | `TYPEC_PROTECTION` necessarily queues extcon role NONE | only `rt_pd_manager` handles the new protection state as unattached; exact extcon has no explicit branch, so it needs a separate UNATTACHED/role event for data cleanup |

Legacy parent reports may retain GPIO55/152 "internal camera" wording. The authoritative
correction is INTERNAL-THERMAL-USB plus this file; the closed low-level reports were not
rewritten during this surgical integration pass.
