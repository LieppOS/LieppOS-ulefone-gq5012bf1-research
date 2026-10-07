# GQ5012BF1 USB data/role stack: static reverse engineering

This work was offline and static only: no adb, no cable or role changes, no VBUS, no PD. Existing read-only captures were used.

## Result

All **13** shipped MediaTek USB data/role vendor kernel modules rebuild from MTK ALPS MT6878 `5e415e059253`, plus two reconstructed GQ5012BF1 patches. Every one is byte-identical to stock in every section except `.note.gnu.build-id`. The one exception is `rt_pd_manager`, whose `.modinfo` `srcversion` hash also differs: it is a source-text MD4, and the code is exact.

| group | module | functions | data | delta |
|---|---|---|---|---|
| controller | `mtu3.ko` | 209/209 | 176/176 | none |
| controller | `xhci-mtk-hcd-v2.ko` | 357/357 | 440/440 | none |
| controller | `usb_boost.ko` | 50/50 | 54/54 | none |
| controller | `usb_logger.ko` | 35/35 | 46/46 | none |
| host/audio | `usb_offload.ko` | 73/73 | 61/61 | none |
| PHY | `phy-mtk-xsphy.ko` | 63/63 | 35/35 | none |
| role | `extcon-mtk-usb.ko` | 22/22 | 28/28 | **YFT OTG/UVC patch** |
| Type-C | `rt_pd_manager.ko` | 11/11 | 19/20 (srcversion) | **TCPC 2.0.31 + vendor** |
| Type-C | `tcpci_late_sync.ko` | 2/2 | 13/13 | none |
| Type-C | `mux_switch.ko` | 17/17 | 19/19 | none |
| gadget | `usb_meta.ko` | 51/51 | 90/90 | none |
| gadget | `mtk_u_ether.ko` | 35/35 | 97/97 | none |
| gadget | `mtk_usb_f_rndis.ko` | 50/50 | 82/82 | none |
| **total** | 13 | **975/975** | **1160/1161** | |

Across all 13 modules: 947/947 import CRCs, 975/975 KCFI type IDs, 18 635/18 635 relocations, and B1==B2 (file-identical) for every module.

**USB3 verdict: D, the path is not present.** The MT6878 SSUSB instance reports 0 USB3 ports from its own capability registers (`usb3-drd: 0`, `IP version 0x1008(U2 IP)`, `USB3 root hub has no ports`). See [`hardware/usb2-vs-usb3.md`](hardware/usb2-vs-usb3.md).

## Map

| topic | document |
|---|---|
| hardware topology, live DT | [`hardware/topology.md`](hardware/topology.md), [`hardware/live-dt-usb-nodes.txt`](hardware/live-dt-usb-nodes.txt) |
| USB2 vs USB3 | [`hardware/usb2-vs-usb3.md`](hardware/usb2-vs-usb3.md) |
| inventory / source map / proof | [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv), [`kernel/source-map.tsv`](kernel/source-map.tsv), [`kernel/parity/full-module-proof.txt`](kernel/parity/full-module-proof.txt) |
| controller | [`controller/`](controller/) |
| PHY + tuning + classification audit | [`phy/`](phy/) |
| extcon / role bridge | [`extcon/`](extcon/) |
| Type-C role path, TCPC boundary | [`typec/`](typec/) |
| host path | [`host/topology.md`](host/topology.md) |
| gadget / configfs / functions | [`gadget/`](gadget/) |
| external USB-C integration closure | [`external/`](external/) |
| init/property flow, USB HAL | [`userspace/`](userspace/) |
| accessories / alt modes | [`binary-analysis/accessory-altmode.md`](binary-analysis/accessory-altmode.md) |
| board deltas | [`yft-usb-deltas.md`](yft-usb-deltas.md) |
| reproduction | [`reconstruction/`](reconstruction/), [`scripts/`](scripts/) |

The earlier USB research in `../../usb-research/` (runtime captures, DT extraction, the thermal-camera transition, the daughterboard photo) is the evidence base and is not duplicated here.
