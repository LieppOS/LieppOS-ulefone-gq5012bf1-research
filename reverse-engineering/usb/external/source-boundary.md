# Source ownership boundary

| layer | owner/artifact | state / where closed |
|---|---|---|
| receptacle/board D+/D− route | BM65_SUB_V1.2 + GPIO55-controlled board route | behavior mapped; switch part/netlist board-only |
| CC, Type-C state, VCONN, water/cable detect | `tcpc_mt6375.ko`, `tcpc_class.ko`, `tcpci_late_sync.ko` | DONE/TCPC-MT6375, DONE/TCPC-CLASS, parent USB Type-C proof |
| Linux Type-C class / HAL role requests | exact `rt_pd_manager.ko` | DONE/USB-TYPEC (code exact; srcversion text-only residual) |
| power negotiation | `mtk_pd_adapter`, charger framework, MT6375 charger | power-charging / USB-CHARGER-INTEGRATION; algorithms not duplicated |
| BC1.2 and USB PHY handoff | exact `mt6375-charger.ko` + exact `phy-mtk-xsphy.ko` | power-charging + DONE/USB-PHY |
| automatic USB role + OTG VBUS + uSmart glue | exact `extcon-mtk-usb.ko` (22/22) | DONE/EXTCON-MTK-USB |
| MTU3 UDC/role and dynamic xHCI | exact `mtu3.ko`, `xhci-mtk-hcd-v2.ko` | DONE/MTU3-SSUSB |
| USB2 PHY | exact `phy-mtk-xsphy.ko` | DONE/USB-PHY |
| gadget core / FunctionFS / standard functions | GKI libcomposite/configfs | generic GKI |
| vendor RNDIS / legacy META | exact `mtk_usb_f_rndis.ko`, `mtk_u_ether.ko`, `usb_meta.ko` | DONE/MTU3-SSUSB gadget proof |
| C2K rawbulk | `c2k_usb*.ko` | modem component (DONE); only composition referenced here |
| host class drivers | GKI/system_dlkm usbcore class modules | generic; inventory in parent USB reports |
| framework USB policy | system_server `UsbService`: UsbPortManager/UsbDeviceManager/UsbHostManager | interface boundary only; unrelated framework internals out of scope |
| USB port HAL | MediaTek AIDL `android.hardware.usb.IUsb/default` v1 | proprietary thin binary; sysfs/API boundary mapped |
| gadget HAL | MediaTek AIDL `android.hardware.usb.gadget.IUsbGadget/default` v1 | proprietary thin binary; configfs/property/FFS boundary mapped |
| composition scripts | AOSP `init.usb*.rc`, MTK `init.mt6878.usb.rc` | complete stock source text; contract mapped |
| thermal takeover | `yft_tiny2c_usb.ko`, extcon `tiny2c_mode`, ThermoVue apps | DONE/INTERNAL-THERMAL-USB; referenced only |
| uSmart takeover | GPIO28/55/152 additions in exact extcon source | uSmart component boundary; shared USB behavior mapped here |
| recovery/fastbootd | stock recovery ramdisk properties/init + AOSP recovery gadget | static boundary mapped; bootloader binary not present |

No kernel source needs reconstruction or parity work for EXTERNAL-USB. This pack is an
integration map over already-closed owners.
