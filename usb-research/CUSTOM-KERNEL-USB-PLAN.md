# Custom-kernel USB plan

## Objective

Preserve the complete stock function set before any USB3 experiment:

- ADB, MTP/PTP and configfs gadget modes;
- external host/OTG and 10-W reverse power;
- Type-C orientation, data/power-role swap and VCONN;
- PD, PPS, UFCS and 120-W charging;
- internal `3474:4321` thermal-camera enumeration, streaming and radiometry;
- recovery/factory/META modes;
- USB audio/offload/boost/logger consumers.

## Component matrix

| Component | Stock implementation | Driver / DT node | Built-in/module | Source available | Donor source | Firmware dependency | SELinux dependency | Android dependency | Can rebuild? | Risk | USB2 req. | USB3 req. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| USB core/configfs/FunctionFS | Android GKI | generic core | built-in/GKI | YES | Android common 6.1 | no | configfs/FunctionFS policy | gadget HAL/init | YES | medium ABI/config risk | YES | YES |
| MTU3 DRD | MediaTek vendor module | `mtu3`; `/soc/usb0@11201000` | module | YES | NothingOSS MT6878 `drivers/usb/mtu3` | no | UDC/mode labels | both USB HALs | YES | high; all paths share it | YES | YES |
| xHCI host | MediaTek `-v2` module | `xhci-mtk`; child `11200000.xhci0` | module | YES donor counterpart | NothingOSS `usb_xhci` | no | root-hub/device labels | host framework/thermal app | YES after parity | high | YES | YES |
| MT6878 XS-PHY | MediaTek module | `mtk-xsphy`; `11f40000` | module | YES | NothingOSS `phy-mtk-xsphy.c` | efuse/nvmem calibration | sysfs only | indirect | YES | very high signal-integrity risk | YES | U2 part only |
| U3 PHY | absent production path | none | none | NO target source | sibling SoCs only, not valid donor | unknown efuse/firmware | unknown | unknown | NO current basis | critical | no | YES |
| role/extcon | Ulefone-modified MediaTek | `mtk-extcon-usb`; `/extcon-usb` | module | YES reconstructed | NothingOSS base + GQ patches | no | extcon/YFT sysfs labels | USB HAL/YFT apps | YES | very high GPIO/VBUS risk | YES | YES |
| TCPC framework | MediaTek/Richtek | `tcpc_class` | module | YES reconstructed/public family | NothingOSS | PD policy data | Type-C sysfs | USB HAL/charger | YES with ABI gates | high | YES | YES |
| MT6375 TCPC | MediaTek | `tcpc_mt6375`; MT6375 `tcpc` | module | YES reconstructed/donor | NothingOSS `tcpc_mt6375.c` | no external blob known | Type-C sysfs | USB HAL/PD stack | YES | high PD/VCONN risk | YES | YES |
| Type-C mux callback | MediaTek | `mux_switch`; `/soc/typec-mux-switch` | module | binary + reconstructable behavior | MediaTek family | no | proc/sysfs if retained | TCPC callbacks | likely | medium | orientation notify | physical mux still needed |
| MT6375 charger/OTG | MediaTek + YFT delta | `mt6375-charger`; `chg/otg` | module | donor source; exact GQ delta partial | NothingOSS `mt6375-charger.c` | no external blob known | charger/extcon sysfs | charger service | YES after YFT parity | critical charging risk | YES | YES |
| PD manager/adapter | MediaTek | `rt_pd_manager`, `mtk_pd_adapter`, `mtk_pd_charging` | modules | donor/public family partial | NothingOSS | adapter/charger policy | power-supply sysfs | charger framework | likely | critical fast-charge risk | charging | charging |
| charger framework/algorithms | MediaTek | charger class, PE/PD/PPS/UFCS policy | modules | donor source expected; exact parity needed | NothingOSS | charger IC behavior | power-supply policy | vendor charger stack | staged | critical 120-W risk | charging | unrelated to SS |
| SC8571 pumps | vendor | master/slave modules | modules | public-family source may exist; exact stock not established | none approved | IC registers | power-supply | charger framework | uncertain | critical battery/thermal | 120 W | no |
| SC851x path | vendor/Ulefone | `sc851x_charger` | module | reconstructed evidence, exact source uncertain | none approved | IC registers | sysfs if exposed | charger framework | uncertain | high | charging only | no |
| YFT thermal rails | Ulefone-specific | `yft_tiny2c_usb`; `/yft_tiny2c_usb` | `vendor_dlkm` module | YES reconstructed | GQ clean-room source | no | `sysfs_yft_file` | ThermoVue Pro | YES | critical thermal regression | YES for thermal | no |
| thermal userspace | proprietary AC020/libusb/libuvc | `com.energy.tc2c` | APK/JNI | binary only | none | calibration assets | USB permission/domain | ThermoVue Pro | retain stock | critical functionality | YES | no current benefit |
| USB offload/boost/logger/META | MediaTek modules | several platform nodes | modules | donor source for major pieces | NothingOSS | audio DSP for offload | vendor policy | audio/factory services | staged | medium/high | stock parity | maybe |
| Android USB HALs | MediaTek AIDL binaries | `IUsb`, `IUsbGadget` default | userspace | binary stock / AOSP interfaces | stock blobs initially | no | HAL domains | framework/init | retain first | high boot/ADB risk | YES | YES |
| init/VINTF/SELinux | stock vendor configuration | rc/xml/cil/contexts | userspace config | YES extracted | stock | no | intrinsic | framework | YES | high if incomplete | YES | YES |

## Recommended implementation sequence

### Stage 0 — freeze the stock oracle

Retain the exact DT/DTBO, module hashes, load order, init rc, VINTF, policy and runtime captures in this repository. The evidence under `usb-research/` is the initial oracle.

### Stage 1 — build without behavior changes

Build the exact GKI release/ABI and the NothingOSS MT6878 MTU3, xHCI and XS-PHY sources as modules. Verify:

- module names/aliases/dependencies;
- imported/exported symbols and CRCs;
- struct/KCFI compatibility;
- DT matches and probe names;
- no new warnings or fallback paths.

Do not change speed, role or PHY tuning.

### Stage 2 — preserve Type-C and charger stack

Bring up TCPC class, MT6375 TCPC, PD manager/adapter and MT6375 charger with exact stock ABI. Preserve VCONN/fault behavior, BC1.2 and source-VBUS sequencing before replacing `extcon-mtk-usb`.

### Stage 3 — apply GQ-specific control edges

Use the existing clean-room `extcon-mtk-usb` and `yft_tiny2c_usb` work to preserve:

- GPIO 28 accessory detection;
- GPIO 37 external OTG source selection;
- GPIO 55 UVC route;
- GPIO 152 accessory power;
- `yft_usb_flag` charger exclusion;
- exact thermal rail order and sensor-ID ABI.

### Stage 4 — Android integration

Keep the stock MediaTek AIDL HALs initially. Reproduce rc permissions, VINTF and SELinux exactly. Verify all configfs function combinations used by the product.

### Stage 5 — regression gates

Run, in order:

1. boot with A active/recoverable and no USB write beyond normal runtime controls;
2. ADB gadget at 480 Mbit/s, disconnect/reconnect and suspend/resume;
3. MTP/PTP and at least one network gadget mode;
4. Type-C cable flip in both orientations;
5. host OTG enumeration and removal;
6. 5-V source output, current limit and shutdown cleanup;
7. PD fixed PDO, PPS and UFCS charger tests with analyzer;
8. thermal camera `3474:4321` direct-port enumeration;
9. thermal image, 25-Hz streaming, radiometry and calibration checks;
10. return from thermal mode to external ADB without reboot;
11. USB audio/offload if supported;
12. recovery/fastboot/META behavior.

Any thermal or charging regression is a release blocker.

## USB3 research gate

Do not add a U3 PHY node or set `super-speed` until all of these exist:

- primary MT6878 U3 register/clock/reset/efuse documentation;
- verified source support for that exact PHY;
- mainboard and daughterboard SS continuity;
- identified orientation/mux path;
- an isolated rollback-safe test design.

Without those inputs, a USB3 patch is fabrication, not reconstruction.

## Internal thermal-camera risk

The camera shares controller, USB2 PHY, power domain, clocks and xHCI stack with external USB. Changes to MTU3 reset timing, xHCI creation, PHY tuning, autosuspend, DMA/IOMMU, USB boost, role-switch ordering or BC1.2 arbitration can break:

- camera enumeration;
- USB interface claiming;
- 25-Hz thermal video;
- AC020 commands/radiometry;
- calibration access;
- return to external ADB.

The controlled stock capture in `USB-INTERNAL-THERMAL-CAMERA.md` must be repeated as a mandatory regression test.
