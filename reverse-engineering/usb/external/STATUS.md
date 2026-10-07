# EXTERNAL-USB — STATUS

**DONE (static integration closure, 2026-10-07).** Runtime role-transition testing is not
required by this scope; all underlying kernel components are already exact and existing
stock captures prove the normal ADB gadget and thermal host transitions.

| DONE criterion | result |
|---|---|
| physical external path | USB-C D+/D− → GPIO55-default external route → only XS-PHY U2 port → MTU3; CC/VBUS/SBU → MT6375; no U3/DP/analog path or second controller — PROVEN |
| Type-C role path | TCPC state/DR swap + charger power-supply notifications → exact `extcon-mtk-usb` → MTU3 role switch — PROVEN |
| device/gadget mode | configfs g1, descriptors, UDC bind, all stock compositions/PIDs and FunctionFS ownership mapped — PROVEN (static); ADB-only composition runtime-proven |
| host/VBUS | ATTACHED_SRC + SOURCE_VBUS → HOST + GPIO37 + MT6375 5.25 V/1.8 A boost; xHCI/root port/class ownership mapped — PROVEN |
| BC1.2/data | PHY BC1.2 SET/CLR, SDP/CDP/DCP/unknown/PD mapping and extcon decision mapped — PROVEN |
| Android ownership | framework `usb` service; MediaTek AIDL IUsb v1 and IUsbGadget v1; init/property/configfs contract mapped — PROVEN |
| ADB/MTP/PTP/network/AOA | activation, FFS gating, RNDIS/NCM and unavailable-but-built ECM/EEM mapped — PROVEN |
| thermal interaction | host takeover, event suppression, gadget loss and no role restoration documented by reference to INTERNAL-THERMAL-USB — PROVEN |
| uSmart boundary | GPIO28 detect → GPIO152 power + GPIO55 route + HOST/NONE; shared-fabric races documented — PROVEN |
| unsupported modes | USB3, DP, passive analog audio, Thunderbolt, PCIe tunneling, SuperSpeed video explicitly closed — PROVEN negative |
| recovery/fastbootd | recovery controller + VID/PIDs recovered; same physical U2 limit; bootloader implementation bounded — PARTIAL boundary, non-blocking |
| failure behavior | role allocation/application, gadget bind, xHCI, VBUS, BC1.2, detach, thermal/uSmart takeover and replug mapped — PROVEN from exact source/static init |

No unresolved behavior remains in the normal Android external-USB integration. Non-blocking
residuals: board switch part/netlist; exact bootloader-fastboot descriptors; no runtime
capture for every statically configured gadget composition. These do not alter the closed
software contract.
