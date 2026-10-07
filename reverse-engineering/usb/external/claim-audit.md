# Existing EXTERNAL-USB pack claim audit

The five original workspace files were read before this closure.

| old claim | source | class now | disposition |
|---|---|---|---|
| external interface is USB-C, USB2 High-Speed | README | PROVEN | controller hardware, DT, UDC and host capture agree |
| stock runtime, gadget state and host enumeration are proven | README | PROVEN | ADB gadget capture is 0e8d:201c at 480 Mbit/s; xHCI host topology is captured |
| "all role transitions and replacement runtime validation" remain required | README/status row | SUPERSEDED | exact extcon/MTU3/TCPC source closes role transitions; replacement runtime is implementation validation, not reverse engineering |
| controller, PHY, Type-C and extcon were closed on 2026-10-05 | README | PROVEN | owning DONE packs and parent USB proof |
| external question includes "OTG/UVC/host mode" as one path | README | STALE | external Type-C, uSmart and internal thermal are three initiators sharing one fabric; UVC is a class, not the external role mechanism |
| AIDL IUsb and IUsbGadget v1 services and names | USB-ANDROID-STACK | PROVEN | stock VINTF, binaries, rc and live binder capture |
| configfs g1 at UDC 11201000.usb0; VID 0e8d; bcdUSB 0200; listed functions | USB-ANDROID-STACK | PROVEN | stock init rc and configfs capture |
| captured composition was ADB-only, PID 201c | both notes | PROVEN | host descriptor and stock properties |
| USB HAL "coordinates" normal Type-C role selection | USB-ANDROID-STACK | SUPERSEDED/REFINED | HAL exposes/query/request APIs; automatic attach roles are selected in TCPC + charger + extcon, not by the HAL |
| GPIO55/152 and writable tiny2c nodes are one thermal-camera route | USB-ANDROID-STACK | STALE | GPIO55/152/28 are uSmart; Tiny2-C uses 149/191/192 + `tiny2c_mode` |
| SELinux specifically labels `tiny2c_mode` `sysfs_yft_file` | USB-ANDROID-STACK | STALE | no specific stock context for that node; observed writes and init permissions remain valid |
| deleting YFT controls can break thermal external-role recovery | USB-ANDROID-STACK | PROVEN (refined) | thermal uses `tiny2c_*`; uSmart uses GPIO path; both affect the shared role |
| UDC/controller/extcon/runtime values in USB-STOCK-RUNTIME | runtime note | PROVEN | retained as primary runtime evidence |
| captured Type-C state was device + sink, preferred sink | runtime note | PROVEN | brackets in typec sysfs identify active values |
| xHCI is absent in gadget mode and appears in host mode | runtime note | PROVEN | capture + exact MTU3 source |
| thermal takes external ADB down and replug restores it | runtime note | PROVEN | stock transition capture |
| no-runtime-proof of dormant U3 IP, SS traces, connector contacts, cable orientations, or board-mod USB3 | runtime note | SUPERSEDED | hardware registers now prove zero device/host U3 ports; board traces/contacts are moot and a daughterboard/DT change cannot create a controller port |
| exact physical switch identity/netlist | old unknown | UNKNOWN, NON-BLOCKING | software-visible route and behavior are proven; part number is board-only |
| evidence/provenance paths and hashes | EVIDENCE-INDEX / PROVENANCE | PROVEN | files resolve; closure adds current canonical files |

**Remaining blocker after classification: none.** The only UNKNOWN is physical component
identity/netlist, not the external software/integration behavior.
