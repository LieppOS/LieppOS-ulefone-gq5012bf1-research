# USB charging and reverse-power integration

## Separation of planes

The phone has two related but distinct planes:

```text
CC / PD / PPS / role policy                power conversion
MT6375 TCPC -> tcpc_class/PD manager  ---> MT6375 charger -> charger framework
                                                  |
                                                  +-> SC8571 master/slave pumps
                                                  +-> SC8510/SC851x path
                                                  +-> fuel gauges / RT6160 supplies
```

This high-power charging architecture does not imply SuperSpeed data capability. CC/PD use dedicated Type-C conductors and USB2 BC1.2 uses D+/D−.

## Identified hardware

| Component | Stock role | USB relationship | Confidence |
|---|---|---|---|
| MT6375 | primary charger + TCPC + OTG VBUS provider + BC1.2 | owns CC/PD, references MTU3 and USB2 PHY, provides `usb-otg-vbus` | PROVEN |
| SC8571 at `11-0066` | `primary_dvchg`, alias `sc-cp-master` | charger-class charge-pump actuator/ADC leaf | PROVEN |
| SC8571 at `6-0067` | `secondary_dvchg`, alias `sc-cp-slave` | parallel charger-class charge-pump actuator/ADC leaf | PROVEN |
| SC8510/SC851x at `6-0069` | 2S switched-capacitor configuration/debug/IRQ shim | registers no charger, power supply, regulator, extcon or USB role and exports no enable/direction API | PROVEN role boundary; board rail use UNKNOWN |
| SH366003 at `9-0055` | secondary fuel gauge | battery telemetry, not USB data | PROVEN |
| RT6160 devices | power-management rails | no USB data ownership shown | PROVEN identity; exact rail consumers outside this report |

The MediaTek charger framework and charging algorithms select among ordinary USB, PD, PPS and pump-assisted paths and contain a generic UFCS-adapter search path.

## Control ownership

| Function | Owning component/path | Evidence boundary |
|---|---|---|
| CC attach and polarity | MT6375 TCPC + `tcpc_mt6375.ko` | exact driver control flow |
| PD message transport | MT6375 TCPC + `tcpc_class.ko` | exact imports/exports and reconstructed driver |
| PPS PDO/APDO request policy | `mtk_pd_adapter.ko`, `mtk_pd_charging.ko`, charger framework | `tcpm_dpm_pd_get_pps_status` and adapter-class edges |
| UFCS policy | `mtk_charger_framework.ko` / `mtk_pep40.ko` consumer path | policy proven; provider not found |
| sink charging policy | MediaTek charger framework + selected algorithm | exact 120-W live selection unmeasured |
| charge-pump actuation/telemetry | `primary_dvchg` and `secondary_dvchg` SC8571 charger devices | SC8571 itself imports no PD/PPS/adapter policy API |
| BC1.2 detection | MT6375 charger coordinated with USB2 PHY | Ulefone `yft_usb_flag` gates conflicts |
| external source VBUS / OTG boost | MT6375 `usb-otg-vbus`, commanded by `extcon-mtk-usb` | exact 5.25-V/1.8-A stock request |
| USB data role | `extcon-mtk-usb` → MTU3 role switch | independent of sink/source charging algorithm |
| SC8510 direction/enable | not exposed by the stock SC851x module | external pin/default or other control remains UNKNOWN |
| battery telemetry | primary MediaTek path plus SH366003 secondary gauge | not a USB data controller |

The exact SC8571 contract is preserved in `kernel/phase4-sc8571-hardware-contract.md`; the SC8510 role boundary is preserved in `kernel/phase4-sc851x-hardware-contract.md`.

## MT6375 USB2/BC1.2 integration

The MT6375 charger DT node references:

```text
phys = <USB2-PHY 3>
phy-names = "usb2-phy"
usb = <11201000.usb0>
```

This lets the charger coordinate BC1.2 detection and USB data-role transitions with the same USB2 PHY. The Ulefone export `yft_usb_flag` prevents ordinary charger/BC1.2 transitions from conflicting with the internal thermal-camera route.

## 120-W sink charging

Ulefone officially states 120-W wired charging. Stock software exposes PD, PD_PPS and UFCS-aware policy paths, while SC8571 master/slave pumps provide the high-current conversion architecture.

Classification:

- advertised 120-W capability: **PROVEN official product specification**;
- PD/PPS integration: **PROVEN**;
- UFCS-aware policy code: **PROVEN**;
- operational UFCS provider/negotiation: **NOT PROVEN and strongly disfavored by the extracted registration audit**;
- exact protocol/pump combination used at the 120-W operating point: **UNKNOWN without charger-analyzer and live register trace**.

`evidence/stock-charger-ufcs-analysis.txt` scans all 471 extracted modules. Only `mtk_pd_adapter.ko` imports `adapter_device_register`; the DT names only `pd_adapter`. The framework initializes both protocol state fields to `1`, so the old `ufcs_type:1` log is not affirmative capability evidence.

No 120-W claim should be assigned solely to MT6375's OTG regulator; sink charging uses the wider charger/pump system.

## External OTG and 10-W wired reverse charging

The ordinary Type-C source-VBUS path is exact:

1. MT6375 TCPC reports source-role/VBUS state;
2. `extcon-mtk-usb.ko` selects host role through the MTU3 role switch;
3. GPIO 37 (`otg_gpio_select`) is asserted with source VBUS;
4. the `usb-otg-vbus` regulator is set to 5.25 V and 1.8 A and enabled;
5. xHCI binds at `11200000.xhci0` for external peripherals;
6. disable/shutdown reverses GPIO/regulator state.

5.25 V × 1.8 A is approximately 9.45 W, consistent with the official “10 W wired reverse charging” rating. Classification: **STRONGLY_SUPPORTED exact external reverse-power path**.

The underlying MT6375 regulator DT allows 4.85–5.50 V and 0.5–2.4 A, but stock extcon policy requests the narrower values above. Do not increase them without electrical/thermal validation.

## Internal thermal/accessory power

GPIO 152 (`uvc_vbus_gpio`) powers the internal/accessory-facing UVC route, while GPIO 55 selects the UVC USB route. `yft_tiny2c_usb.ko` separately sequences 1.8-V, 3.3-V and I/O 3.3-V rails.

This path is not the official external 10-W reverse-charging interface. Existing stale `reverse_charging_level` labels do not have a live stock implementation and must not be exposed as a LieppOS control.

## VBUS limiting and safety

`extcon-usb/vbus_limit_cur` selects the stock current-limit policy while Type-C VBUS is active. MT6375 source enable includes boost programming and USB-killer/fault protection. A custom kernel must preserve:

- safe-0-V and VBUS-present checks;
- OVP/OCP and USB-killer behavior;
- source/sink mutual exclusion;
- GPIO 37/regulator ordering;
- `yft_usb_flag` gating;
- shutdown cleanup.

## USB3 relevance

PD, PPS, UFCS, 120-W charging and 10-W reverse power can all coexist with USB2-only data. The observed charging architecture supplies no positive evidence for USB3 PHYs or PCB lane routing.
