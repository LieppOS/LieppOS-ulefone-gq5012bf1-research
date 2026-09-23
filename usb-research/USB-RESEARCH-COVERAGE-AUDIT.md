# USB research phase-coverage audit

This audit compares the durable research set against the original 24 investigation phases. It distinguishes a completed analysis from a question that remains unresolved because decisive evidence does not exist locally.

Status meanings:

- **COMPLETE** — requested analysis and durable evidence exist;
- **COMPLETE_WITH_UNKNOWN** — the phase was performed and the correct result is an explicitly bounded unknown;
- **PARTIAL** — meaningful evidence exists, but a requested test or exhaustive inventory remains outstanding;
- **NOT_DONE** — no adequate work exists.

| Phase | Status | Durable result | Remaining work or limitation |
|---|---|---|---|
| 0. Preserve existing research | COMPLETE | `README.md` records reused kernel/uSmart/thermal research and stock provenance. | None. |
| 1. Full source/binary inventory | COMPLETE | DT, stock partitions, Android services/init/VINTF/policy and all 471 extracted modules were searched; 42 USB/Type-C/charging/factory modules now have location/hash/vermagic/dependency/alias/import/export/string inventories. | Generic built-in GKI behavior remains represented by source/config rather than separate `.ko` rows. |
| 2. Device-tree USB topology | COMPLETE | `USB-DEVICE-TREE.md` follows controller, PHY, role, TCPC, extcon and thermal phandles from merged base DT + slot-A DTBO. | Electrical nets after GPIO controls remain outside DT's proof boundary. |
| 3. USB3 in DT | COMPLETE | Production U3 PHY absent; disabled FPGA placeholder; MTU3 references one U2 PHY and is capped at High-Speed. | None for stock software. |
| 4. Map `11201000.usb0` | COMPLETE | Sole operational MTU3 DRD instance; `mtu3.ko`; dynamic `11200000.xhci0` host child. | Confidential IP manual is unnecessary for stock identity but needed for transistor-level capability. |
| 5. Internal thermal topology | COMPLETE_WITH_UNKNOWN | Controlled capture proves direct xHCI port `1-1`, `3474:4321`, UVC 1.10, 480 Mbit/s, no observed hub, shared controller/route and I2C/power separation. | Full USB descriptors/proprietary interfaces were blocked by usbfs permissions; exact FM78100 register role remains unknown. |
| 6. Stock runtime forensics | COMPLETE | Slot-A/boot gate, UDC, role, extcon, Type-C, configfs, bindings, modules, interrupts, I/O ranges and device topology are archived. | A live high-voltage charging contract was deliberately not exercised. |
| 7. External controlled test | PARTIAL | Linux xHCI host observed `0e8d:201c` at 480 Mbit/s and `bcdUSB 2.00`. | Cable was not independently certified and both Type-C orientations were not separately archived. This does not affect the independent stock DT/UDC High-Speed conclusion. |
| 8. Type-C/CC/PD controller | COMPLETE | MT6375 TCPC, CC/polarity, VCONN, role notifications and PD software chain are mapped. | Physical SS mux existence and live analyzer traces remain unknown. |
| 9. PD/charger relationship | COMPLETE_WITH_UNKNOWN | MT6375, SC8571 master/slave, SC8510 shim, SH366003, RT6160, PD/PPS policy and MT6375 OTG are separated from USB data. A 471-module/GKI/DT audit found UFCS policy consumers but no provider and proved `ufcs_type:1` is initialized baseline state. | Exact 120-W live protocol/pump sequence still requires analyzer/register evidence. |
| 10. Kernel-driver reconstruction | COMPLETE | Core and indirect charger algorithms, generic serial/networking, MediaTek gadget networking, C2K factory, offload/boost/logger and thermal dependencies have durable 42-module ABI metadata. | Rebuilding still requires per-module source parity; inventory itself is closed. |
| 11. MT6878 SoC capability | COMPLETE_WITH_UNKNOWN | OEM-published MT6878 kernel source implements only a production U2 path; sibling MT6897 source demonstrates the expected U3 delta. | No primary MT6878 datasheet/package map was found, so silicon/package U3 capability cannot responsibly be made binary. |
| 12. MT6878 donor comparison | COMPLETE | GQ stock and NothingOSS MT6878 match on address, MTU3, one U2 PHY and High-Speed cap; sibling control is documented. | None with current public source. |
| 13. Physical USB3 routing | COMPLETE_WITH_UNKNOWN | Path is split into SoC, mainboard, connector, daughterboard and receptacle layers, each independently classified. | Schematic, continuity, X-ray or high-resolution two-sided boards are required. |
| 14. PCB/daughterboard investigation | PARTIAL | Exact-model `BM65_SUB_V1.2` listing/photo and FCC filing metadata were located and archived with provenance. | No usable teardown, FCC internal-photo exhibit, underside image, boardview or schematic was obtained. |
| 15. Daughterboard replacement | COMPLETE_WITH_UNKNOWN | All five cases are evaluated; daughterboard-only upgrade requires proven SS pairs at the board connector. | Physical continuity decides Cases 2 vs 3. |
| 16. USB-C orientation | COMPLETE_WITH_UNKNOWN | MT6375 CC polarity and software mux callback path are proven; `mux_switch.ko` is not itself a hardware bus controller. | Physical SS lane mux/integrated switching remains unknown. |
| 17. DisplayPort Alt Mode | COMPLETE_WITH_UNKNOWN | Generic TCPC capability metadata exists, but no operational DP PHY/bridge/mux/service path was found. | Hardware schematic or live alt-mode trace would be needed. |
| 18. Android USB stack | COMPLETE | AIDL HALs, configfs, properties, functions, init, VINTF and SELinux integration are mapped. | Only ADB mode was dynamically captured; all declared gadget combinations were not individually exercised. |
| 19. Custom-kernel requirements | COMPLETE | `CUSTOM-KERNEL-USB-PLAN.md` contains the required component/dependency/risk table and staged plan. | Exact parity work is implementation, not research completion. |
| 20. Thermal regression risk | COMPLETE | Shared controller/PHY/xHCI/role resources and mandatory regression gates are documented. | Must be rerun for every candidate kernel. |
| 21. Evidence matrix | COMPLETE | Required rows plus additional charging, DP and feasibility rows are present. | Update as physical evidence appears. |
| 22. Architecture document | COMPLETE | Five requested diagrams use solid proven and dashed inferred edges. | Copper remains dashed by design. |
| 23. USB3 feasibility verdict | COMPLETE_WITH_UNKNOWN | `UNKNOWN — NEED PCB EVIDENCE`; stock software USB2-only; current hardware likely limited but not declared physically impossible. | Physical and primary silicon evidence remain decisive. |
| 24. Decisive evidence plan | COMPLETE | Non-destructive continuity/X-ray/photo plan and exact SS contact targets are documented. | Requires spare hardware. |

## Honest completion statement

The topology reconstruction is substantially complete, but the overall request is **not closed as a physical USB3 yes/no**. Phases 7 and 14 contain real, specifically identified evidence acquisition still outstanding. Phases marked `COMPLETE_WITH_UNKNOWN` have been investigated; their unknowns cannot be resolved by additional interpretation of the same software evidence.

## Highest-priority follow-up order

1. Acquire two-sided spare-board imagery or continuity evidence.
2. If a certified cable/host is available, archive both connector orientations as corroborating runtime evidence.
3. Use a USB power/protocol analyzer to identify the actual 120-W negotiation and pump sequence.
