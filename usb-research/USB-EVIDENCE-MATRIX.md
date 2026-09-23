# USB evidence matrix

Confidence vocabulary is defined in `README.md`. “DISPROVEN” is scoped to the stated implementation/observation, not broader silicon possibilities.

| Layer | Current conclusion | Evidence | Confidence | Missing evidence |
|---|---|---|---|---|
| MT6878 USB controller IP | one MTU3 dual-role instance with xHCI child | NothingOSS `mt6878.dts`; stock DT | PROVEN for public implementation | confidential silicon manual |
| MT6878 USB3 capability | no public production U3 path; transistor-level capability unresolved | `MT6878-DONOR-COMPARISON.md`; secondary PhoneDB conflict | UNKNOWN, strongly disfavored | primary datasheet/register manual/package map |
| MT6878 USB3 PHY capability | no production U3 node/register/calibration in public MT6878 source | NothingOSS source; sibling MT6897 control | UNKNOWN at silicon level; DISPROVEN in public DT | primary PHY manual/package map |
| GQ5012BF1 controller configuration | OTG, High-Speed ceiling, one USB2 PHY | `/soc/usb0@11201000` | PROVEN | none for stock config |
| `11201000.usb0` identity | MediaTek MTU3 gadget/DRD core | compatible, registers, live `mtu3` binding | PROVEN | none |
| external USB-C controller path | MTU3 UDC through shared USB2 route | endpoint graph; host ADB enumeration | PROVEN | physical switch netlist |
| external USB2 PHY | MT6878 XS-PHY at `11f40000` | DT + `mtk-xsphy` live binding | PROVEN | schematic not needed for function |
| external USB3 PHY | no enabled/referenced production U3 PHY | effective DT, donor source, runtime root hub | DISPROVEN in stock software | silicon/package/PCB evidence for dormant path |
| internal thermal USB controller | same MTU3 child `11200000.xhci0` | root-hub serial and live binding | PROVEN | none |
| internal thermal USB speed | 480 Mbit/s High-Speed | kernel enumeration and sysfs | PROVEN | none |
| internal thermal USB device | direct UVC 1.10 `3474:4321` at `1-1` | controlled capture | PROVEN | full descriptor dump/alternate-setting catalog |
| internal USB hub | none in observed path | direct `1-1` topology | DISPROVEN for tested path | hidden unpowered topology not indicated |
| Type-C controller | MT6375 TCPC `type_c_port0` | DT, `tcpc_mt6375`, runtime class | PROVEN | none |
| orientation handling | MT6375 CC polarity + software mux callback | driver `set_polarity`; endpoint graph; `mux_switch` imports | PROVEN in software | physical SS mux/netlist |
| physical USB3 orientation mux | no identified device/control edge | DT/module/board-photo search | UNKNOWN, no positive evidence | both PCB sides, schematic, part markings |
| USB role switch | `extcon-mtk-usb` endpoint to MTU3 | DT graph, sysfs, thermal transition | PROVEN | none |
| VBUS control | MT6375 `usb-otg-vbus`, GPIO 37 selection | DT, reconstructed control flow | PROVEN | board net name |
| VCONN control | MT6375 TCPC power/protection registers | `tcpc_mt6375` `set_vconn` | PROVEN | live sourced-VCONN measurement |
| PD support | MT6375 TCPC + TCPC class + PD manager/adapter | modules, DT, Type-C sysfs | PROVEN | analyzer trace for specific charger |
| PPS support | charger framework PD_PPS path | power-supply types, stock module strings | PROVEN software support | live PPS negotiation trace |
| UFCS support | policy searches for `ufcs_adapter`, but no provider was found | all 471 modules + GKI + DT registration audit; baseline-state disassembly | PROVEN policy awareness; operational support UNKNOWN/strongly disfavored | actual provider or live UFCS analyzer trace |
| OTG support | MTU3 host + MT6375 source VBUS | DT, extcon contract, stock behavior | PROVEN | new external peripheral capture optional |
| reverse charging | external Type-C source at ~5.25 V × 1.8 A, consistent with 10 W | official spec + exact extcon/regulator path | STRONGLY_SUPPORTED | inline USB power measurement |
| 120-W charging | official and backed by PD/PPS policy plus dual pumps; exact protocol unmeasured | official spec; charger inventory | PROVEN product capability | live protocol/pump trace at 120 W |
| mainboard SuperSpeed routing | not established | no schematic/continuity/X-ray | UNKNOWN | mainboard photos and continuity/X-ray |
| board-to-board connector SS lanes | connector visible; net assignment unknown | `EDA006599748` photo | UNKNOWN | exact pinout/continuity |
| daughterboard SS routing | top side insufficient; no positive SS evidence | replacement-board photo | UNKNOWN | underside, X-ray, continuity |
| USB-C receptacle SS routing | contact population not visible | replacement-board photo | UNKNOWN | connector footprint/continuity |
| SuperSpeed runtime enumeration | neither external nor internal path enumerated above 480 Mbit/s; no SS host root hub | UDC/host captures | DISPROVEN in stock tests | certified cable/orientation test for corroboration |
| stock kernel SS support for this instance | generic drivers capable; instance lacks U3 PHY/config | DT, module, runtime | DISPROVEN for instance | valid U3 hardware description would be prerequisite |
| DisplayPort Alt Mode | generic capability metadata only; no operational DP path | TCPC DT vs absent PHY/bridge/mux control | UNKNOWN / no operational evidence | DP PHY, schematic, live alt-mode trace |
| daughterboard-only USB3 upgrade | cannot be established; likely insufficient | missing SoC/mainboard lane evidence | UNKNOWN, unlikely | prove SS pairs at board connector first |
| kernel/DT-only USB3 upgrade | no valid U3 PHY description/register source | stock/donor comparison | UNKNOWN at silicon level, currently implausible | primary SoC docs plus physical lane proof |
