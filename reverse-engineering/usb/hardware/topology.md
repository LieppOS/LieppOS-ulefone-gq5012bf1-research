# GQ5012BF1 USB hardware topology

Sources:
- the live DT (`live-dt-usb-nodes.txt` here, taken from the existing read-only `/sys/firmware/devicetree` capture);
- the effective stock DT (base vendor_boot DTB plus DTBO, `usb-research/evidence/stock-usb-dt-nodes.txt`);
- the donor MTK ALPS `5e415e059253` `mt6878.dts`;
- the existing read-only runtime captures in `usb-research/evidence/`.

Classes used in the tables:
- **SOC CAP**: what the IP/driver family can do.
- **DT**: what the stock DT instantiates.
- **BOARD**: physical wiring, where proven.
- **RUNTIME**: what was observed on the device.

## Block diagram

```text
                        MT6878 SoC
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ SSUSB IP (power domain MT6878_POWER_DOMAIN_SSUSB = 5)                      │
 │  ┌───────────────────────────────┐   IPPC 0x11203e00/0x100                │
 │  │ MTU3 device MAC 0x11201000    │◄─ usb_role_switch "11201000.usb0-role-switch"
 │  │  /soc/usb0@11201000           │   IRQ SPI 384 (Linux 416), dr_mode=otg  │
 │  │  maximum-speed = high-speed   │   clocks: TOP USB_TOP_SEL (sys_ck),     │
 │  │                               │   TOP USB_XHCI_SEL (host_ck),           │
 │  │  child: xHCI 0x11200000/0x1000│   PERAO SSUSB0_FRMCNT (frmcnt_ck)       │
 │  │  /soc/usb0@11201000/xhci0     │   vusb33 = MT6369 VUSB (always-on)      │
 │  │  IRQ SPI 385, sys_ck = clk26m │   wakeup: pericfg_ao 0x214 bit 105      │
 │  └──────────────┬────────────────┘                                        │
 │                 │ phys = <&u2port0 PHY_TYPE_USB2(3)>   (no USB3 entry)     │
 │  ┌──────────────▼────────────────┐                                        │
 │  │ XS-PHY 0x11f40000/0x400       │  only child: usb2-phy0 (u2_port_base)  │
 │  │  ref = clk26m, efuse intr/term│  no u3 child, no u3 register range     │
 │  └──────────────┬────────────────┘                                        │
 └─────────────────┼────────────────────────────────────────────────────────┘
                   │ D+/D− (USB 2.0 HS pair)
     ┌─────────────┴──────────────────────┐  GPIO 55 uvc_switch_gpio (route select)
     │ board D+/D− route (switch)         │  GPIO 152 uvc_vbus_gpio (camera VBUS/power)
     ├──────────────┬─────────────────────┘
     │              │
  Type-C receptacle   internal ThermoVue UVC camera (3474:4321, HS, root port 1)
  (BM65_SUB_V1.2      rails via yft_tiny2c_usb GPIO 192/191/149
   daughterboard)

 MT6375 PMIC/charger @ I2C 0x11280000 addr 0x34
   tcpc (type_c_port0, IRQ pd_evt)  ── CC/VCONN/SBU(WD) ── Type-C receptacle
   chg/otg regulator "usb-otg-vbus" 4.85–5.5 V, 0.5–2.4 A ── VBUS
   chg uses usb2-phy (BC1.2) and usb = <&ssusb>
```

## MTU3 controller (`/soc/usb0@11201000`)

| item | value | class |
|---|---|---|
| compatible | `mediatek,mtu3` → `mtu3.ko` (`mtu3_plat.c`) | DT |
| MMIO | `mac` 0x11201000/0x2e00, `ippc` 0x11203e00/0x100 | DT, RUNTIME (`/proc/iomem`) |
| IRQ | GIC SPI 384 level-high (Linux virq 416) | DT, RUNTIME |
| clocks | `sys_ck` TOP USB_TOP_SEL, `host_ck` TOP USB_XHCI_SEL, `frmcnt_ck` PERAO SSUSB0_FRMCNT | DT (identical to donor) |
| power domain | scpsys SSUSB (5) | DT |
| regulator | `vusb33-supply` = MT6369 `vusb` (always-on) | DT |
| resets | none in DT. IP soft reset happens through IPPC `ip_pw_ctr0` in the driver | DT, source |
| role | `dr_mode = "otg"`, `usb-role-switch`, graph endpoint ↔ `/extcon-usb` | DT |
| speed | `maximum-speed = "high-speed"` | DT, RUNTIME (UDC `maximum_speed=high-speed`) |
| vendor flags | `mediatek,force-vbus`, `mediatek,clk-mgr` (selects `ssusb_mode_sw_work_v2`), `mediatek,noise-still-tr`, `mediatek,hwrscs-vers = 1`, `mediatek,syscon-wakeup`, `wakeup-source`, `cdp-block` | DT |
| VBUS sense | `force-vbus`: the MAC is told VBUS is valid by software. There is no `vbus-supply` on the MTU3 node, so `ssusb_set_vbus()` is a no-op. Real VBUS comes from MT6375 (see role-switching) | DT, source |

## xHCI child (`/soc/usb0@11201000/xhci0@11200000`)

| item | value | class |
|---|---|---|
| compatible | `mediatek,mtk-xhci` → `xhci-mtk-hcd-v2.ko` | DT |
| MMIO / IRQ | 0x11200000/0x1000, SPI 385 | DT |
| binding | populated/depopulated by MTU3 on host/device role changes (`ssusb_host_register`) | source, RUNTIME (unbound in gadget mode) |
| root hubs | **one**: `usb1` (`1d6b:0002`, 480 Mbit/s, serial `11200000.xhci0`). No SuperSpeed `usb2` root hub | RUNTIME (thermal-camera capture) |
| offload | `mediatek,usb-offload` → `/soc/usb-offload` (ADSP USB-audio offload, SRAM v3, `audio-xhci-sram` 0x11065000) | DT |

The single root hub matters. `xhci-mtk` sets `allow_single_roothub` and creates the shared (USB3) HCD only when the xHCI Supported-Protocol capability reports USB 3.x ports (`xhci_has_one_roothub`). That capability is read from controller hardware registers, not from DT. See [`usb2-vs-usb3.md`](usb2-vs-usb3.md).

## PHY (`/soc/usb-phy0@11f40000`)

| item | value | class |
|---|---|---|
| compatible | `mediatek,xsphy`, `mediatek,mt6878-xsphy` → `phy-mtk-xsphy.ko` | DT |
| children | **only** `usb2-phy0@11f40000` (`u2_port_base`, ref = clk26m) | DT |
| calibration | nvmem `intr_cal`/`term_cal` (masks 0x3f / 0xf00), `efuse-intr = 0x23` fallback | DT |
| tuning | `eye-vrt = 2`, `eye-vrt-host = 2`, `discth = 9`, `tx-chirpk-capable`, `usb2jtag`, `usb2uart` | DT (identical to donor) |
| U3 | no `usb3-phy` child, no U3 register range. Root `/usb-phy` is `mediatek,fpga-u3phy`, `status = "disabled"`, an FPGA I2C test PHY that is not connected to MTU3 | DT |

## Type-C, role, VBUS

| element | node / module | role |
|---|---|---|
| Type-C port controller | MT6375 `tcpc` (`tcpc_mt6375.ko`, `tcpc_class.ko`), `type_c_port0`, `role-def = 5` (Try.SNK DRP), `rp-level = 1` (1.5 A), `vconn-supply = 1` (always), water detection (`en-wd`), cable-type detection (`en-ctd`) | CC detection, PD, VCONN |
| Type-C class port | `/rt-pd-manager` (`rt_pd_manager.ko`) | `/sys/class/typec/port0`, partner/altmodes, orientation/mux forwarding |
| USB role bridge | `/extcon-usb` (`extcon-mtk-usb.ko`) | TCPC notifier → `usb_role_switch_set_role(usb0)`, OTG VBUS regulator, GPIO glue |
| VBUS source (OTG) | MT6375 `chg/otg` regulator `usb-otg-vbus` (4.85–5.50 V, 0.5–2.4 A) | `vbus-voltage = 5.25 V`, `vbus-current = 1.8 A`, `vbus-limit-current = 0.5 A` |
| ID / accessory pin | GPIO 28 `id-gpios`, edge IRQ `extcon-usb` | internal accessory (thermal camera) insert/remove |
| OTG select | GPIO 37 `otg_gpio_select`, high while extcon drives VBUS | board VBUS-path select |
| UVC route | GPIO 55 `uvc_switch_gpio` | D+/D− route to the internal camera |
| UVC power | GPIO 152 `uvc_vbus_gpio` | internal camera VBUS |
| mux | `/soc/typec-mux-switch` (DTBO-added, `orientation-switch`, `mode-switch`, `accessory`), endpoint ↔ tcpc | `mux_switch.ko`. No mux/redriver IC driver below it |
| SBU | sensed by MT6375 ADC (`io-channels` SBU1/SBU2) for water detection only | no SBU data mux |

## DP/DM and SS routing

- **D+/D−** go from the SoC USB2 PHY to a board switch (GPIO 55), which selects the Type-C receptacle or the internal camera. The internal path is runtime-proven: the camera enumerates on root port 1 at 480 Mbit/s with no hub. The switch part number is not known.
- **SS TX/RX**: there is no SS PHY in DT, no SS root hub, and no redriver/retimer/mux IC driver. Physical routing is unproven either way (see `usb2-vs-usb3.md`).
- **CC/SBU/VCONN** terminate on the MT6375 TCPC.
