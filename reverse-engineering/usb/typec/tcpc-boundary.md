# TCPC / Type-C boundary (USB-data view only)

The PD charging algorithms (PE5/PPS/UFCS, PDO selection, charger framework) are **out of scope** and closed elsewhere. This note records only what the USB data/role stack consumes.

## Modules

| module | status | USB-relevant role |
|---|---|---|
| `tcpc_mt6375.ko` | DONE/TCPC-MT6375 (66/66 exact) | MT6375 Type-C port controller: CC, VBUS detect, VCONN, water detection (SBU via ADC), cable-type detection |
| `tcpc_class.ko` | DONE/TCPC-CLASS (2.0.31_MTK, 707 functions ABI-exact) | Type-C state machine, PD protocol, `register_tcp_dev_notifier`, `tcpm_*` API |
| `tcpci_late_sync.ko` | **exact here** (2/2) | `late_initcall_sync` walking `tcpc_class` and calling `tcpc_device_irq_enable()` per TCPC, so CC events only start once all notifier consumers have registered (battery-absent notifier compiled out) |
| `rt_pd_manager.ko` | **exact here** (11/11 functions, data 19/20: only `srcversion`) | Linux `typec` class bridge (`/sys/class/typec/port0`) |
| `mux_switch.ko` | **exact here** (17/17) | `typec_switch`/`typec_mux` provider for `/soc/typec-mux-switch`, forwarding to registered mux ICs (none) |
| `pd_dbg_info.ko` | DONE/PD-DBG-INFO | PD debug log buffer |

## Notifier chain into USB

| consumer | registered for | events used for USB data |
|---|---|---|
| `extcon-mtk-usb` | `TCP_NOTIFY_TYPE_USB \| VBUS \| MISC` (0xe) | SOURCE_VBUS (8), TYPEC_STATE (13), DR_SWAP (17) |
| `rt_pd_manager` | all types | TYPEC_STATE, PR/DR/VCONN_SWAP, PD_STATE, partner ID, AMA_DP_*, WD0_STATE, VBUS_SHORT_CC, CC_HI, ALERT_RATELIMITED |
| charger side (`mtk_pd_adapter`, `mtk_chg_type_det`, `mt6375-charger`) | VBUS/USB/MISC | SINK_VBUS, PD contract, attach for BC1.2 (not covered here) |

## Separation: power negotiation vs data role

| concern | owner | USB data effect |
|---|---|---|
| PD contract, PDO/APDO, PPS/UFCS, input current | charger framework + `mtk_pd_adapter` (power-charging research) | none |
| sink detection / BC1.2 (SDP/CDP/DCP) | MT6375 charger through `usb2-phy` (`PHY_MODE_BC11_SW_SET/CLR`) | sets `POWER_SUPPLY_TYPE` → extcon `psy_detector` → DEVICE role on SDP/CDP |
| source VBUS (OTG) | TCPC `SOURCE_VBUS` → extcon → MT6375 `usb-otg-vbus` + GPIO 37 | VBUS present for host role |
| data role | TCPC TYPEC_STATE/DR_SWAP → extcon → MTU3 role switch | host/device |
| VCONN | TCPC (`tcpc,vconn-supply = 1` always) | none (no e-marker data use) |
| orientation | TCPC polarity → rt_pd_manager `typec_set_orientation` → `mux_switch` | **no effect on USB2**. D+/D− are flip-agnostic and no SS lanes need muxing |

## 2.0.31 / GQ5012BF1 deltas visible in `rt_pd_manager`

These are proven by the exact rebuild (patch 0001):

1. `tcp_notify.vsc_status` became an `int` bitmask (`BIT(TCPC_POLARITY_CC1/CC2)`). The log is now "enter short status, CC%s%s".
2. A new event, `TCP_NOTIFY_ALERT_RATELIMITED`, with a log line.
3. A new typec state, `TYPEC_PROTECTION`, is treated like UNATTACHED (partner removed, roles reset).
4. `WD0_STATE` (water) role postponement is skipped when `tcpc->bootmode` is 8 or 9 (KPOC / LP-offcharging). `tcpc->bootmode` sits at offset 0x3550 of `struct tcpc_device`, which requires `CONFIG_MTK_TYPEC_WATER_DETECT=1` in the header config. That is the same flag TCPC-CLASS needed.

Residual: `.modinfo srcversion` (an MD4 of the source text, with whitespace and `/* */` comments ignored) does not match. Code, data, relocations, imports and the other modinfo fields are exact. The stock source therefore differs from the reconstruction only in non-code tokens (for example `//` comments or brace style). 320 plausible token variants were tested without a match (`scripts/tools/rt_pd_manager_srcversion_variants.py`).

## Alternate modes

- The DT `tcpc/displayport` declares DFP_D pin assignments C/D/E, and `tcpc_class` has `pd_dpm_alt_mode_dp.c`. However:
  - the mux chain ends in `mux_switch` with no mux/redriver IC;
  - the MT6878 DT has no DP controller/PHY node;
  - USB is U2-only, so there are no SS lanes to repurpose.

  **DP Alt Mode is not functional on GQ5012BF1**: it is software-declared but not physically realisable. See `../binary-analysis/accessory-altmode.md`.
