# USB status (2026-10-05)

| scope | state | basis |
|---|---|---|
| MTU3 controller + xHCI + boost/logger/offload kernel | **CLOSED (exact)** | 5 modules byte-identical except build-id; DT contract, PM and role state machine mapped |
| XS-PHY (USB2) | **CLOSED (exact)** | byte-identical; tuning/calibration map; the USB3 PHY is absent; misfiled D-PHY/provisioning files identified |
| extcon-mtk-usb | **CLOSED (exact)** | 22/22, all sections; the YFT patch is reconstructed |
| Type-C role kernel (rt_pd_manager, tcpci_late_sync, mux_switch) | **CLOSED** | code/data/ABI exact; `rt_pd_manager` keeps a srcversion-only residual (source comments/formatting) |
| gadget kernel (usb_meta, RNDIS) | **CLOSED (exact)** | byte-identical; the configfs flow is mapped |
| USB2 vs USB3 | **RESOLVED: D (not present)** | hardware capability registers in stock kmsg plus the exact driver source |
| USB HAL (AIDL IUsb/IUsbGadget v1) | boundary **MAPPED** | proprietary binaries, sysfs interface documented |
| External USB-C integration | **CLOSED (static)** | physical path, Type-C state machine, device/gadget, host/VBUS, BC1.2, HAL/init, thermal/uSmart boundaries and failures in [`external/`](external/) |

Not performed, by offline rule (not closure blockers):

- new cable/OTG/DR-swap runtime tests beyond existing captures
- live validation of every statically configured gadget composition
- physical identification of the GPIO55 board switch

## Open (not claimed)

- `rt_pd_manager` `srcversion`: the exact stock source text (comments/whitespace) is unknown.
- The part number/netlist of the board D+/D− switch on GPIO 55 (software behavior is closed).
- Exact pre-Android bootloader-fastboot descriptors (recovery/fastbootd properties are mapped).

## Workspace classification (2026-10-05)

Recorded in `REVERSE-ENGINEERING-STATUS.md` and `COPY-MANIFEST.tsv` of the organized workspace:

- PARTIAL → DONE: `MTU3-SSUSB` (controller + xHCI + boost/logger/offload + gadget vendor modules), `USB-PHY`, `EXTCON-MTK-USB`, `USB-TYPEC` (role kernel; the TCPC core was already in `DONE/TCPC-CLASS` and `DONE/TCPC-MT6375`).
- BLOCKED → DONE: `USB3-FEASIBILITY`, a resolved negative (verdict D).
- Staying PARTIAL, with notes added: `EXTERNAL-USB` (runtime/replacement validation) and `INTERNAL-THERMAL-USB` (thermal app/libusb protocol). `USB-CHARGER-INTEGRATION` is unchanged (charging scope).
- USB-PHY audit:
  - `panel-ky-vtdr6115-dphy-cmd.c` (a DSI D-PHY panel driver) was dropped; the canonical copy is in `DONE/VTDR6115-DISPLAY`.
  - `47-resume-approved-b-physical-provisioning.sh` was moved to `PARTIAL/PARTITION-OWNERSHIP`.

Totals: DONE 57 → 62, PARTIAL 72 → 68, BLOCKED 4 → 3, total 133.
