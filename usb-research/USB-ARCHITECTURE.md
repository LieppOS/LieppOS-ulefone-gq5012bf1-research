# GQ5012BF1 USB architecture

Legend:

- `──▶` proven connection/control/data path;
- `- -▶` inferred physical continuation not backed by schematic/continuity;
- `[?]` unknown physical element.

## 1. External data path

```text
Android configfs / USB gadget HAL
             │
             ├──▶ mtu3.ko / UDC 11201000.usb0
             │         │
             │         └──▶ MT6878 XS-PHY USB2 @ 11f40000
             │                     │
             │                     - -▶ [GPIO55-controlled route/switch]
             │                                  │
             │                                  - -▶ BM65_SUB_V1.2 daughterboard
             │                                               │
             │                                               └──▶ USB-C D+/D−
             │                                                        │
             └────────────────────────────────────────────────────────└──▶ PC
                                                                        480 Mbit/s
```

Controller/PHY/configuration and 480-Mbit/s endpoints are proven. The exact switch IC and PCB nets are inferred/unknown.

## 2. Internal thermal-camera path

```text
yft_tiny2c_usb.ko ──▶ GPIO rails 1.8 V / 3.3 V / I/O 3.3 V
          │
          └──▶ yft_usb_flag ──▶ MT6375 BC1.2 exclusion

ThermoVue Pro ──▶ tiny2c controls ──▶ shared-route transition
                                      │
11201000.usb0 ──▶ 11200000.xhci0 ──▶ usb1 root hub, 480 Mbit/s
                                              │
                                              └──▶ port 1 / 3474:4321
                                                   UVC 1.10 thermal camera
                                                   USB2 High-Speed
                                              │
                                              └──▶ usbfs/libusb/libuvc
                                                   AC020 processing/radiometry
```

Every controller, root-hub, device and speed edge in this diagram was observed. GPIO-to-switch copper remains unproven.

## 3. Type-C / PD path

```text
USB-C CC1/CC2
     │
     - -▶ daughterboard/mainboard interconnect
                │
                └──▶ MT6375 TCPC @ I2C 11280000/0x34
                         ├──▶ tcpc_mt6375.ko
                         ├──▶ tcpc_class.ko / TCPM
                         ├──▶ rt_pd_manager.ko
                         ├──▶ mtk_pd_adapter.ko
                         ├──▶ CC polarity / power role / data role
                         ├──▶ VCONN control + protection
                         └──▶ extcon-mtk-usb notifier
                                   └──▶ MTU3 usb_role_switch
```

A linked `typec-mux-switch` software node distributes orientation/mode callbacks. No physical SS mux/redriver control is identified.

## 4. Charging path

```text
USB-C VBUS + CC negotiation
          │
          ├──▶ MT6375 TCPC: PD / PPS messaging
          │
          └──▶ MT6375 primary charger / BC1.2 / power-path
                         │
                         ├──▶ MediaTek charger framework
                         │      ├──▶ PD/PPS adapter/provider path
                         │      └──▶ UFCS-aware policy [provider not found]
                         │
                         ├──▶ SC8571 master pump @ 11-0066
                         ├──▶ SC8571 slave pump  @ 6-0067
                         ├──▶ SC8510 config/IRQ shim @ 6-0069
                         ├──▶ SH366003 gauge     @ 9-0055
                         └──▶ battery / system rails

Official sink capability: 120 W
```

The PD/PPS path, UFCS-aware policy and hardware inventory are proven. No operational UFCS provider was found in the extracted kernel/module set. The exact 120-W live protocol and pump state sequence remains unmeasured.

## 5. External host / OTG / reverse-power path

```text
MT6375 TCPC source-role event
          │
          └──▶ extcon-mtk-usb
                 ├──▶ GPIO37 otg_gpio_select
                 ├──▶ MT6375 usb-otg-vbus: 5.25 V, 1.8 A
                 └──▶ usb_role_switch = host
                              │
                              └──▶ 11200000.xhci0
                                         │
                                         └──▶ XS-PHY USB2
                                                   │
                                                   - -▶ route/switch + daughterboard
                                                              │
                                                              └──▶ external USB-C peripheral

Official reverse-power rating: 10 W; configured source request ≈9.45 W
```

## Shared-resource result

The external gadget, external host and internal thermal camera are modes/routes of one MTU3/XS-PHY USB2 fabric. The controlled thermal test proves that xHCI host activation detaches the external UDC/ADB path.

There is no operational second USB controller and no operational SuperSpeed PHY in stock.

## Physical boundary

Software can prove everything through:

- controller and PHY registers;
- role-switch endpoint graph;
- GPIO ownership;
- root-hub/device identity;
- negotiated speed.

Software cannot prove the copper beyond the GPIO-controlled route, board connector or receptacle. That boundary is intentionally dashed in the diagrams.
