# Can GQ5012BF1 physically operate SuperSpeed USB?

## Verdict

**D: the USB3 path is not present.** This is stronger than "board configured USB2-only". The MT6878 SSUSB controller instance reports from its own hardware capability registers that it has **no USB 3.x port**, on the device side and on the host side. The DT has no U3 PHY. Physical SS wiring is therefore irrelevant to the question.

The upgraded verdict comes from stock kernel messages, which are hardware-register reads and not DT-derived. The source is an existing read-only capture, `slot-b-investigation/boot-chain-compare/vendor-a-on-b-control/last-kmsg-analysis/text/last_kmsg.5.txt`, from the stock GKI `6.1.115-android14-11-g6b18f0b574ab-ab12901745` kernel with the stock vendor modules:

```text
mtu3 11201000.usb0: u2p_dis_msk: 0, u3p_dis_msk: 0        <- DT does NOT mask any U3 port
mtu3 11201000.usb0: usb3-drd: 0                            <- IPPC U3D_SSUSB_IP_DEV_CAP/IP_XHCI_CAP U3 port count
mtu3 11201000.usb0: IP version 0x1008(U2 IP)               <- U3D_SSUSB_IP_TRUNK_VERS + DEV_CAP: u3_capable = 0
mtu3 11201000.usb0: max_speed: high-speed
xhci-mtk 11200000.xhci0: USB3 root hub has no ports        <- xHCI Supported-Protocol capability: 0 USB3 ports
xhci-mtk 11200000.xhci0: hcc params 0x01400f99 hci version 0x110
hub 1-0:1.0: 1 port detected                               <- one USB2 root port
```

What each line proves. The source is the byte-exact `mtu3.ko` / `xhci-mtk-hcd-v2.ko` rebuild, so these code paths are exactly the shipped ones.

| line | code | what is read |
|---|---|---|
| `usb3-drd: 0` | `mtu3_plat.c` `ssusb_u3_drd_check()`: `is_u3_drd = dev_u3p_num && host_u3p_num` | `U3D_SSUSB_IP_DEV_CAP` and `U3D_SSUSB_IP_XHCI_CAP`, **hardware** IPPC registers. With `u3p_dis_msk = 0` the DT did not suppress this |
| `IP version 0x1008(U2 IP)` | `mtu3_core.c` `mtu3_hw_init()`: `u3_capable = !!SSUSB_IP_DEV_U3_PORT_NUM(IP_DEV_CAP)` | hardware: the device MAC has **zero** U3 ports |
| `USB3 root hub has no ports` | KDM `usb_xhci/xhci-mem.c:2499` `xhci_setup_port_arrays()` from the xHCI Extended Capabilities (Supported Protocol, major revision 3) | hardware: the xHCI exposes **no** USB 3.x protocol port. `xhci-mtk` sets `allow_single_roothub`, so only the USB2 HCD (`usb1`) is registered |

Runtime captures agree:
- gadget: `current_speed = maximum_speed = high-speed`, host sees 480M;
- host: only `usb1` at 480 Mbit/s with 1 port, no `usb2` SS bus.

## Layer-by-layer

| layer | finding | class |
|---|---|---|
| MTU3/xHCI driver family | MTU3 and xhci-mtk support USB3 on other MediaTek SoCs, and `phy-mtk-xsphy` has U3 code (`u3_phy_*`) | SOC CAP (family), **not this instance** |
| controller hardware (IPPC/xHCI caps) | **0 U3 ports** (device and host). IP trunk version 0x1008 is a "U2 IP" | **PROVEN, hardware register** |
| DT | `maximum-speed = "high-speed"`, `phys = <&u2port0 PHY_TYPE_USB2>` only, XS-PHY has only `usb2-phy0`, root `/usb-phy` is a disabled FPGA U3 test PHY not linked to MTU3. Identical to MTK ALPS `mt6878.dts` | DT |
| PHY | the XS-PHY `u2_port_base` range only. No U3 register window or U3 efuse (`efuse-tx-imp`/`rx-imp`) | DT |
| Type-C mux | `/soc/typec-mux-switch` (DTBO) registers orientation/mode switches, but no mux/redriver IC driver (`ps5169`, `fusb304`, `ptn36241g`, `usb_dp_selector`) ships or is instantiated. `mtk_typec_{switch,mux}_register` has no caller among the stock modules | DT + module set |
| gadget descriptors | `bcdUSB 0x0200` in `init.mt6878.usb.rc` | userspace (consistent, not proof) |
| board | the BM65_SUB_V1.2 daughterboard photo cannot show SS pairs (unchanged UNKNOWN). **No longer relevant**: there is no SS port at the controller to route | BOARD (moot) |

## Would replacing the USB daughterboard (or editing DT) enable USB3?

**No.** A daughterboard with SS contacts would have nothing to connect to, because the MT6878 USB controller instance has no SuperSpeed port. A DT edit (`maximum-speed`, a U3 PHY child) cannot create MAC/xHCI U3 ports that the capability registers report as absent.

USB3 would need **all** of the following, none of which exists:

1. a SuperSpeed-capable USB MAC/xHCI. MT6878's is U2-only, so this would be an external USB3 controller, e.g. a PCIe xHCI if MT6878 even exposes a usable PCIe root port on this board (unproven);
2. a SuperSpeed PHY with its lanes and calibration;
3. mainboard SS TX/RX differential pairs, board-to-board connector pins, daughterboard traces and receptacle A2/A3/A10/A11/B2/B3/B10/B11 contacts;
4. an orientation mux or redriver (Type-C flip) and SS-rated ESD parts;
5. DT, kernel and HAL enablement.

That amounts to a different phone design, not a part swap.

## Relation to the existing BLOCKED/USB3-FEASIBILITY verdict

The earlier verdict, "UNKNOWN: need PCB evidence", treated SoC capability as unknown ("A. SoC supports USB3? UNKNOWN, strongly disfavored"). The kernel log above, read through the now byte-exact driver source, settles A: the SoC USB instance is **U2-only**. That makes the PCB question (D, E, F) moot for USB3 enablement.
