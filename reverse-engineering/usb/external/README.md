# EXTERNAL-USB — external USB-C integration (GQ5012BF1)

**DONE (offline static integration closure, 2026-10-07).** The external receptacle shares
the single USB2-only MTU3/`usb2-phy0` fabric. MT6375 TCPC events and MT6375 charger
classification feed `extcon-mtk-usb`, which selects DEVICE/HOST/NONE; Android configfs
owns gadget compositions, while dynamic xHCI + usbcore own external host enumeration.
The internal thermal camera and uSmart accessory can take over the same fabric.

Normal external path:

```text
USB-C CC/VBUS/SBU → MT6375 TCPC/charger
USB-C D+/D− → board route (GPIO55=0) → usb2-phy0@11f40000
            → MTU3 11201000.usb0
              ├─ DEVICE: configfs g1 → UDC → ADB/MTP/PTP/RNDIS/NCM/…
              └─ HOST: xHCI child 11200000.xhci0 → usb1 root port 1
```

There is no USB3 port, U3 PHY, SuperSpeed/DP mux, DP transmitter, analog-audio switch,
Thunderbolt/PCIe path, or second external controller. Stock OTG VBUS is fixed 5-V-class
(5.25 V requested) from the MT6375 boost at 1.8 A, optionally limited to 0.5 A.

| file | scope |
|---|---|
| `claim-audit.md` | Phase-1 classification of every old pack claim |
| `hardware-path.md` | receptacle/CC/VBUS/D+/D− → PHY → MTU3 |
| `typec-state-machine.md` | attach, detach, DR/PR swap and charger/data consequences |
| `device-mode.md` | configfs device sequence, descriptors, ADB/MTP/PTP/network/AOA |
| `gadget-functions.tsv` | every stock-created/configured function and PID |
| `host-mode.md` | Type-C source → boost + xHCI; external classes/policy |
| `vbus-power-role.md` | sink/source/data-role ownership and current limit |
| `bc12-boundary.md` | SDP/CDP/DCP/unknown/PD USB-side behavior |
| `usb-hal.md` | framework → AIDL v1 HALs → sysfs/configfs |
| `init-property-contract.tsv` | stock USB properties and triggers |
| `thermal-interaction.md` | authoritative INTERNAL-THERMAL-USB consequences |
| `usmart-boundary.md` | GPIO28/55/152 takeover and coexistence |
| `recovery-fastboot.md` | supported static recovery/fastbootd boundary |
| `failure-semantics.md` | failures and stock recovery behavior |
| `source-boundary.md` | owning closed component at each layer |
| `stale-claims.md` | corrected legacy statements |

Low-level proofs remain in the parent USB tree and are referenced rather than copied.
Runtime captures remain in `usb-research/evidence/`.
