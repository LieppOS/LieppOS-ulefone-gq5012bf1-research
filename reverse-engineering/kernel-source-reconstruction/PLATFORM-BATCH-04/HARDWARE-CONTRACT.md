# Batch04 charging / Type-C / USB hardware contract

Detailed per-target source units/hashes/APIs: evidence/SOURCE-TO-HARDWARE-CONTRACTS.json.
Saved DT/DTBO/load/runtime evidence: evidence/hardware/*.tsv and runtime-boundary JSON.
Import/export/load contracts: DEPENDENCIES.tsv and evidence/PROVIDER-GRAPH.tsv.
Authoritative established owners remain reverse-engineering/power-charging,
mt6375-pmic,usb-charger-integration,usb,thermal-camera and kernel/usmart.
No new phone capture or physical command was performed.

## Evidence grades

PROVEN_RUNTIME = explicitly cited historical read-only observation, not new measurements.
ENABLED_IN_STOCK_DT = effective enabled compatible/resources, not successful probe.
STOCK_BINARY_IMPLEMENTATION = actual matched implementation (whole25 A; per-axis-only
for unaccepted C explicitly scoped in their ledgers). PUBLIC_REFERENCE_ONLY = actual
candidate source whose relevant behavior is not fully stock-matched. UNKNOWN = no
supported observation of wiring/current/throughput/voltage/profile/runtime behavior.

## Power topology

```text
External connector/VBUS
  -> MT6375 parent I2C@11280000, address0x34 (existing Batch03 parent A)
  -> MT6375 charger child / primary_chg / OTG regulator (selected)
  -> charger_class -> mtk_chg_type_det and mtk_charger_framework (selected)
  -> adapter/PD/PE algorithm classes and policy (selected)
  -> battery power_supply and MT6375 gauge algorithms (selected)
       -> named 3rd-gauge provider (SH366003 module, outside selected30)
```

Configured MT6375 MFD/child IRQs and IIO channels are not separate independent I2C chips.
SPMI/I2C/platform bus addresses and interrupt-provider references are recorded separately;
SPMI child slave addresses must not be reinterpreted as CPU MMIO.

Recovered stock-equivalent YFT source uses `3rd-gauge` for battery/daemon SOC and battery
properties. `yft_cam_open_flag`/`yft_long_charger_flag` are true source exports in
mtk_charger_framework, shared with already certified camera/charger-cooling consumers.
Their natural CRC/license/namespace and producer types are cross-checked, not copied.
Source source-limited camera/thermal policy, PE/PD current-selection/calibration constants,
charger fault/OTG/suspend/watchdog logic and warning-location metadata are preserved in
complete patches. Configured values/code constants are not measured limits or proof of
PD/PPS delivery. No current, voltage, charger watchdog or power supply setting was changed.

Charging detection/class srcversion gaps remain C even though bodies and ABI match.
Kernel PD algorithms, TCPC controller operations and userspace power decisions are distinct;
selected presence does not prove a negotiated profile or fitted charge-pump capability.

## Shared USB topology

```text
Type-C USB2/default pair ----+
                            +-- GPIO55 board route -- USB2 XS-PHY -- MTU3 USB0
uSmart USB2 pair ------------+                            |             |
                                                     common PHY     xHCI host
Internal thermal USB2 3474:4321 ----- shared USB0 path (physical default-route wiring UNKNOWN)

Type-C CC/PD -> MT6375 TCPC -> tcpc_class / rt_pd_manager
                                  -> extcon -> common USB0 role switch
uSmart GPIO28 detect -> extcon GPIO152 power / GPIO55 route -> same role switch
Thermal yft_tiny2c_usb GPIO149/191/192 rails -> tiny2c_mode -> same role switch
```

This is a software/configuration topology, not a schematic. There is one configured USB2
PHY/controller/host fabric. Separate detect/rail controls do not establish independent
controllers or simultaneous Type-C/uSmart/thermal data paths.

## Actual board GPIO ownership (important correction)

- GPIO28 `id-gpios`: active-low **uSmart accessory** detect, extcon exact source.
- GPIO55 `uvc_switch_gpio`: HIGH selects uSmart, LOW external/default route.
- GPIO152 `uvc_vbus_gpio`: active-high **uSmart accessory power**, not thermal rails.
- GPIO37 `otg_gpio_select`: external OTG VBUS selection around MT6375 regulator.
- GPIO149/191/192: thermal module rails, implemented by separately owned/certified
  `yft_tiny2c_usb`, not one of these30.
- `/sys/class/yft_extcon/tiny2c_mode`: selected extcon store queues HOST/NONE, no
  GPIO55/152 writes. Legacy read returns0; do not infer current role from that value.

Earlier usb/hardware/topology.md mislabeled GPIO55/152 as thermal controls. It is corrected
with existing kernel/usmart/usb-routing.md and thermal-camera/hardware/topology.md evidence.
Saved thermal capture enumerates3474:4321 on1-1 at480M with `uvc_insert_status=0`.
Physical default-route thermal/Type-C sharing or another idle board mux remains UNKNOWN.
Route-element silicon/contact numbering and simultaneous electrical operation remain UNKNOWN.

## Role arbitration and concurrency

`yft_usb_flag` is a genuine selected mt6375-charger GPL export; thermal ownership suppresses
stock extcon Type-C/power-supply/ID role work and BC1.2/PHY switching. This is host source
behavior, not an external controller firmware reconstruction.

uSmart does not have a separate arbitration lock. Source allows Type-C events to change
common role while GPIO55/152 remain selected/on. Removing uSmart restores route/power and
queues NONE without replaying an already-attached Type-C state. Last queued role work wins;
routing GPIOs and role changes are not atomically serialized. These are stock software
limitations, not newly tested physical states. See kernel/usmart/typec-interaction.md.
Do not claim concurrent independent ports or additional modes.

## Configured controller, PHY and power resources

From existing saved DT/source/runtime research:

- `/soc/usb0@11201000`, `mediatek,mtu3`: MAC0x11201000/0x2e00,
  IPPC0x11203e00/0x100, GIC SPI384; OTG, role switch, maximum-speed high-speed.
- xHCI child0x11200000/0x1000, SPI385; populated by MTU3 host role, not an independent
  second connector controller. Recorded host root hub is usb1, one USB2 port.
- XS-PHY0x11f40000/0x400: USB2 child only, clk26m reference, saved efuse/calibration
  references/tuning. No linked U3 PHY; disabled FPGA U3 test node is not fitted proof.
- MTU3 clocks sys_ck/host_ck/frmcnt_ck; SSUSB power-domain5; MT6369 VUSB vusb33 supply;
  wakeup/syscon resources and PHY/role graph are retained in the detailed DT ledgers.
- USB audio offload references ADSP/SCP/audio APIs and audio-xhci SRAM; DMA/IOMMU and
  shared-memory configuration must not be interpreted as successful firmware operation.
- Type-C mux node registers orientation/mode/accessory interfaces; no downstream mux/
  redriver IC caller is established. Presence of the mux class or Type-C does not prove USB3.

PROVEN_RUNTIME historical logs report U2 IP0x1008 and zero USB3 protocol ports; saved DT
also selects only USB2. This supports the existing USB2-only verdict for this instance,
not an assertion about all MT6878 driver-family capabilities. No throughput was measured.

## Loading, external ABI, firmware and boundaries

Every selected canonical identity/partition occurrence/load-list position and provider
relation is retained. Graph covers1912 imports and every selected export.195 noncore source
boundaries are checked;18 external slots are freshly source-derived, including common IIO,
AEE/lbat,clock/display/QoS,RPS,ADSP/SCP/audio. Existing regulator/PINCTRL/clock/PMIC/MFD,
thermal/power/IOMMU/GKI contracts remain unchanged; a matching API never certifies the
whole external producer or runtime provider selection.

Unaccepted TCPC core has eight real function-source differences plus timer/source token/
layout consequences; do not present those candidate branches as fully proven stock behavior.
TCPC-MT6375 bodies match but token/counter metadata remains C. Their driver source does not
prove CC/PD negotiation, VCONN delivery, alternate-mode hardware or fault handling under load.

External SH366003/charge-pump controllers, TCPC silicon, connected accessories/thermal UVC
firmware/calibration and ADSP/SCP audio offload firmware are outside this normal-world
source batch. No ADB/phone/PD/USB role/charging control/register/GPIO/DMA/mailbox/firmware
transaction, stress test, firmware/calibration edit, flash or push occurred.
