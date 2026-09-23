# Final USB subsystem report — GQ5012BF1

Overall USB3 verdict: **UNKNOWN — NEED PCB EVIDENCE**, with the shipped design **likely hardware-limited** and stock software conclusively USB2-only.

1. **Exact identity of `11201000.usb0`:** `/soc/usb0@11201000`, `compatible = "mediatek,mtu3"`, the sole operational MTU3 dual-role controller. MAC `0x11201000/0x2e00`, IPPC `0x11203e00/0x100`, device IRQ 384. See `USB-CONTROLLER.md`.

2. **Exact stock controller driver:** platform driver `mtu3` from `mtu3.ko`; dynamic host child `11200000.xhci0` binds `xhci-mtk` from `xhci-mtk-hcd-v2.ko`.

3. **Exact PHY driver(s):** `mtk-xsphy` from `phy-mtk-xsphy.ko`, binding `/soc/usb-phy0@11f40000`; only its `usb2-phy0` child is referenced.

4. **Does MT6878T have USB3 controller capability?** No public production MT6878 implementation was found. The generic MTU3 driver family can support USB3, but exact silicon/package capability is **UNKNOWN and strongly disfavored** by the OEM-published MT6878 source.

5. **Does MT6878T have a USB3 PHY?** No production U3 PHY exists in the public MT6878 source or GQ DT. A disabled FPGA placeholder is not a phone PHY. Undocumented silicon capability remains **UNKNOWN**.

6. **Does GQ5012BF1 enable a USB3 PHY?** **No — DISPROVEN.** MTU3 references one USB2 PHY and has `maximum-speed = "high-speed"`.

7. **Multiple USB controllers/ports?** One MTU3 instance, one xHCI child and one production USB2 PHY/root-port path. `11211000.usb1` is a dead userspace pathname, not a live controller.

8. **Internal thermal-camera controller/path:** the same MTU3 fabric switched to host, through `11200000.xhci0`; camera is direct root-port device `1-1`, no internal hub.

9. **Internal thermal-camera speed:** **480 Mbit/s High-Speed**, UVC 1.10, VID:PID `3474:4321`, manufacturer `Thermal Cam Co.,Ltd`.

10. **External Type-C controller/path:** MTU3 UDC `11201000.usb0` through the USB2 XS-PHY and Ulefone route/daughterboard to Type-C D+/D−.

11. **Exact Type-C/TCPC/PD implementation:** MT6375 TCPC at I2C controller `11280000`, address `0x34`, driven by `tcpc_mt6375.ko` + `tcpc_class.ko`, `rt_pd_manager.ko`, `mtk_pd_adapter.ko` and charging policy modules.

12. **Orientation switching:** MT6375 detects CC polarity and programs `TCPC_CTRL.PLUG_ORIENT`; the linked `mux_switch.ko` distributes Linux Type-C mode/orientation callbacks. It is not itself a physical redriver/mux and has no hardware-bus imports. Physical SS orientation routing remains unknown.

13. **VBUS/VCONN control:** external source VBUS uses MT6375 `usb-otg-vbus` plus GPIO 37; internal accessory power uses GPIO 152. MT6375 TCPC directly controls protected VCONN through its power/VCONN registers.

14. **PD/PPS/UFCS integration:** PD/PPS use MT6375 TCPC, TCPC policy, adapter class and charger framework. UFCS is a separate charger-framework adapter path. These negotiate power and do not imply USB3 data.

15. **OTG/reverse charging:** TCPC source-role event → `extcon-mtk-usb` → GPIO 37 + MT6375 regulator at 5.25 V/1.8 A → MTU3 host/xHCI. Approximately 9.45 W matches the official 10-W reverse rating.

16. **Stock external USB speed:** UDC current and maximum are High-Speed; Linux host sees `0e8d:201c`, `bcdUSB 2.00`, at **480 Mbit/s**.

17. **Kernel/DT SuperSpeed support:** generic drivers support USB3-capable sibling SoCs, but this target instance has no U3 PHY description/reference/root hub. Target support is **DISPROVEN**.

18. **Mainboard SuperSpeed routing proven?** **No — UNKNOWN.** No schematic, boardview, continuity or X-ray evidence.

19. **Daughterboard SuperSpeed routing proven?** **No — UNKNOWN.** A top-side `BM65_SUB_V1.2` photo is archived, but contacts, underside and inner layers are unresolved.

20. **Can daughterboard replacement alone plausibly enable USB3?** Not on present evidence. It works only if all SS pairs already reach the board connector (Case 3), which is unproven and currently unlikely.

21. **Can kernel/DT alone enable USB3?** Currently implausible. Required MT6878 U3 registers, clocks, resets, calibration, driver binding and physical lanes are all unidentified.

22. **What must a custom LieppOS kernel implement?** MTU3 gadget/DRD, MediaTek xHCI, calibrated XS-PHY, MT6375 TCPC/VCONN/PD, extcon role/VBUS/GPIO sequencing, charger/BC1.2/PPS/UFCS integration, YFT rail/flag behavior, Android HAL/configfs/VINTF/SELinux and all offload/boost/factory consumers. See `CUSTOM-KERNEL-USB-PLAN.md`.

23. **What could break the thermal camera?** MTU3/xHCI creation, USB2 PHY tuning, resets/clocks/power domains, autosuspend, DMA/IOMMU, role-switch/GPIO order, BC1.2 arbitration, USB boost and userspace interface claiming. Thermal enumeration, video, radiometry, calibration and return to ADB are mandatory regression gates.

24. **What remains UNKNOWN?** MT6878 transistor/package U3 capability; PCB SS lanes; receptacle contact population; board-connector pinout; physical mux/redriver; exact UFCS provider; exact 120-W protocol/pump sequence; operational DP Alt Mode.

25. **Single highest-value next experiment:** on a spare `BM65_SUB_V1.2` and mating mainboard, battery disconnected, continuity-map all eight Type-C SS contacts through the daughterboard and board connector toward the SoC side. This directly tests whether a daughterboard-only path exists without risking the sealed in-service phone.

## Evidence boundary

Software has now closed controller identity, PHY configuration, role topology, external speed and internal camera path. It has **not** closed PCB routing. Any report claiming electrical impossibility from DT/runtime alone is rejected.
