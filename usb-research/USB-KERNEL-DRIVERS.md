# Stock kernel USB-driver inventory

## Evidence

- `evidence/stock-module-metadata.txt`: SHA-256, vermagic, names, dependencies and aliases.
- `evidence/stock-module-symbols.tsv`: complete undefined-import and `__ksymtab` export inventory.
- `evidence/stock-usb-modules.txt`: live loaded-module set.
- stock load order: `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/modules.load` and `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/modules.load`.

All inspected modules use stock vermagic `6.1.115-android14-11-g945dff7bc1bf ... aarch64` unless otherwise recorded in the metadata file.

## Core data path

| Module | Stock location | Live driver / role | Imports / exports | Source classification |
|---|---|---|---:|---|
| `mtu3.ko` | vendor ramdisk | `mtu3`; MTU3 dual-role gadget core at `11201000.usb0` | 164 / 14 | **ANDROID COMMON** counterpart present at `common/drivers/usb/mtu3`; stock vendor-module build may carry MediaTek deltas |
| `xhci-mtk-hcd-v2.ko` | vendor ramdisk | `xhci-mtk`; host child at `11200000.xhci0` | 201 / 47 | **MEDIATEK MODIFIED**; Android-common `xhci-mtk` is the upstream counterpart, but the stock `-v2` module is not source-identical evidence |
| `phy-mtk-xsphy.ko` | vendor ramdisk | `mtk-xsphy`; USB2 PHY at `11f40000` | 59 / 0 | **ANDROID COMMON** counterpart `common/drivers/phy/mediatek/phy-mtk-xsphy.c` |
| `extcon-mtk-usb.ko` | vendor ramdisk | `mtk-extcon-usb`; role/VBUS/UVC routing | 63 / 0 | **ULEFONE-SPECIFIC** delta over a MediaTek donor; clean-room reconstruction and stock oracle already in `kernel/phase4-extcon-mtk-usb-*` |
| `mux_switch.ko` | vendor ramdisk | `mtk-typec-mux-switch`; Type-C switch/mux callback fan-out | 32 / 4 | **MEDIATEK MODIFIED**; exact stock source absent locally |
| `usb_offload.ko` | `vendor_dlkm` | audio USB offload | 73 / 8 | **MEDIATEK MODIFIED** |
| `usb_boost.ko` | vendor ramdisk | USB performance/DVFS boost | 47 / 1 | **MEDIATEK MODIFIED** |
| `usb_logger.ko` | vendor ramdisk | MTU3/xHCI event logging | 44 / 0 | **MEDIATEK MODIFIED** |
| `usb_meta.ko` | vendor ramdisk | META/factory UDC support | 71 / 0 | **MEDIATEK MODIFIED** |

`mtu3.ko` advertises `MediaTek USB3 DRD Controller Driver`, but the description identifies the driver family, not the configured speed of this instance. The effective DT references only the USB2 XS-PHY and caps the instance at `high-speed`.

The stock `mux_switch.ko` exports only callback registration APIs (`mtk_typec_mux_register/unregister`, `mtk_typec_switch_register/unregister`) and imports Type-C core registration helpers. It has no I2C, GPIO or regmap imports. Therefore this module is a software notifier/fan-out layer, not evidence of a physical SS mux/redriver IC.

## Type-C, PD and charger bridge

| Module | Role | Imports / exports | Classification |
|---|---|---:|---|
| `tcpc_class.ko` | MediaTek/Richtek TCPC/TCPM policy and PD class | 101 / 204 | **MEDIATEK OPEN SOURCE** family with stock modifications; reconstructed locally in prior Phase 4 work |
| `tcpc_mt6375.ko` | MT6375 TCPC hardware driver | 62 / 0 | **MEDIATEK MODIFIED**; stock-equivalent reconstruction documented in `kernel/phase4-tcpc-mt6375*` |
| `tcpci_late_sync.ko` | late TCPC synchronization | 4 / 0 | **MEDIATEK MODIFIED** |
| `rt_pd_manager.ko` | Type-C class/PD role manager | 40 / 0 | **MEDIATEK MODIFIED** |
| `mtk_pd_adapter.ko` | exposes PD adapter operations to charger framework | 32 / 0 | **MEDIATEK MODIFIED** |
| `mt6375-charger.ko` | primary charger, BC1.2/USB2-PHY integration, OTG regulator provider | 79 / 1 | **MEDIATEK MODIFIED** with Ulefone `yft_usb_flag` export |
| `sc8571_charger.ko` | master/slave charge-pump driver | 41 / 0 | **PROPRIETARY MODULE** / public family counterparts not exact stock source |
| `sc851x_charger.ko` | SC8510 additional conversion path | 29 / 0 | **PROPRIETARY MODULE**; prior reconstruction proves no USB data/role API |

The key cross-module edges are:

```text
MT6375 TCPC -> tcpc_class -> rt_pd_manager / mtk_pd_adapter
                              |
                              +-> extcon-mtk-usb -> usb_role_switch -> MTU3
MT6375 charger -> usb-otg-vbus regulator -> extcon-mtk-usb
MT6375 charger -> shared USB2 PHY for BC1.2
```

`extcon-mtk-usb.ko` depends on `tcpc_class` and `mt6375-charger`. `mt6375-charger.ko` exports `yft_usb_flag`; that Ulefone-specific flag coordinates charger/BC1.2 behavior with the internal thermal path.

## Internal thermal glue

| Module | Location | Role | Imports / exports | Classification |
|---|---|---|---:|---|
| `yft_tiny2c_usb.ko` | `vendor_dlkm` | rail sequencing, sensor ID and charger-exclusion flag | 22 / 0 | **ULEFONE-SPECIFIC** |

The module has no USB-core, host-controller, UVC or interface-management imports. Runtime proves that image transport instead enumerates below `xhci-mtk` and is claimed through `usbfs` by the stock app.

## Load order and built-in boundary

`phy-mtk-xsphy.ko`, `xhci-mtk-hcd-v2.ko`, and `mtu3.ko` are consecutive early vendor-ramdisk entries. TCPC/PD and `extcon-mtk-usb.ko` load later from the same ramdisk. `yft_tiny2c_usb.ko` and `usb_offload.ko` live in `vendor_dlkm`.

Generic USB core, gadget/configfs, Type-C core, USB role-switch core and other GKI APIs are built into or supplied by the GKI/system module set; the MediaTek platform integration above is vendor modular.

## Custom-kernel implications

A source replacement must preserve:

1. MTU3 gadget and dynamic xHCI-child creation;
2. XS-PHY USB2 tuning/calibration and `#phy-cells` argument semantics;
3. MT6375 TCPC ABI and PD notifier behavior;
4. extcon endpoint/role-switch semantics plus GPIOs 28/37/55/152;
5. `usb-otg-vbus` voltage/current behavior;
6. `yft_usb_flag` coordination;
7. thermal-camera transition from UDC to xHCI host and back;
8. MediaTek USB boost/logger/offload consumers or explicit, tested removal.

Replacing only the upstream-looking core drivers without the MediaTek/Ulefone control edges can break charging-role detection, OTG VBUS, the thermal camera, audio offload or gadget recovery.
