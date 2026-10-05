# Type-C → USB data-role path (exact kernel modules)

```text
 CC1/CC2, VBUS, VCONN, SBU(ADC)
        │
 MT6375 TCPC  (tcpc_mt6375.ko, DONE/TCPC-MT6375)  role-def=5 Try.SNK DRP, Rp 1.5A, VCONN always,
        │                                          WD (water) + CTD (cable type) on, FOD/OTP off
 tcpc_class.ko (TCPC 2.0.31_MTK, DONE/TCPC-CLASS) ── typec state machine, PD policy engine, DPM
        │  srcu notifier chain "type_c_port0" (register_tcp_dev_notifier)
        ├──────────────────────────────┬──────────────────────────────────────┐
        ▼                              ▼                                      ▼
 rt_pd_manager.ko (exact)        extcon-mtk-usb.ko (exact)                charger side (not redone):
  /sys/class/typec/port0          USB data role + OTG VBUS                 mtk_pd_adapter, mtk_chg_type_det,
  typec_set_data_role/pwr_role/   (see ../extcon/README.md)                mt6375-charger, mtk_charger_framework
  vconn_role/orientation/opmode        │ usb_role_switch_set_role
  partner + PD identity (no altmode reg)▼
  fwnode_typec_mux_get(tcpc parent)  MTU3 role switch "11201000.usb0-role-switch"
        │ typec_mux_set (DP)           │ ssusb_mode_sw_work_v2
        ▼                              ▼
 mux_switch.ko (exact) /soc/typec-mux-switch  ─ no mux IC below (pass-through)
                                 host: populate xhci0 (USB2 root hub, 1 port)
                                 device: mtu3 UDC (configfs g1)
```

## Event matrix

| Type-C event (TCPC) | rt_pd_manager (typec class) | extcon-mtk-usb (USB) | MTU3 result |
|---|---|---|---|
| UNATTACHED → ATTACHED_SNK / NORP_SRC / CUSTOM_SRC / DBGACC_SNK (phone is sink) | data=DEVICE, pwr=SINK, opmode from Rp, vconn=SINK, orientation from polarity | **skipped** (`mediatek,bypss-typec-sink = 1`). The role then comes from the psy path: SDP/CDP → DEVICE | device (UDC) when the charger type is SDP/CDP. Stays NONE on a DCP |
| UNATTACHED → ATTACHED_SRC / ATTACHED_DEBUG (phone is source: OTG) | data=HOST, pwr=SOURCE, opmode from local Rp, vconn=SOURCE, orientation | SRC: role HOST. SOURCE_VBUS(mv>0) → GPIO 37=1 + MT6375 OTG 5.25 V/1.8 A | host: xHCI populated |
| UNATTACHED → ATTACHED_AUDIO | "Audio plug in". Partner accessory = AUDIO | no role change | none (see accessory doc) |
| any attached → UNATTACHED, or new state **TYPEC_PROTECTION** (2.0.31 delta) | partner unregistered, roles reset to the `prefer_role` default (SINK/DEVICE), orientation NONE | role NONE (for SRC/SNK/NORP/CUSTOM/DBGACC). SOURCE_VBUS(0) → GPIO 37=0, regulator off | off (`USB_ROLE_NONE` with clk-mgr v2) |
| DR_SWAP (PD) | `typec_set_data_role` | NONE then DEVICE/HOST, unless already there | swap |
| PR_SWAP / VCONN_SWAP (PD) | `typec_set_pwr_role` / `vconn_role` | none (VBUS follows SOURCE_VBUS) | — |
| WD0_STATE (water detect) | `tcpm_typec_change_role_postpone(role_def or SNK)`. **Skipped when bootmode is 8 or 9** (KPOC/low-power off-charging, a 2.0.31/GQ5012BF1 delta) | — | — |
| VBUS_SHORT_CC | log of CC1/CC2 bitmask (2.0.31 `int vsc_status`) | — | — |
| ALERT_RATELIMITED (2.0.31) | log only | — | — |
| `yft_usb_flag == 1` (MT6375 YFT mode) | unaffected | **all** role changes suppressed | holds the current role |

`rt_pd_manager` also handles the userspace requests from `/sys/class/typec/port0/{data_role,power_role,port_type}`. These are written by the USB AIDL HAL and go to `tcpm_dpm_pd_data_swap`/`power_swap`/`tcpm_typec_change_role_postpone`.

## DRP, suspend, accessories

- **DRP**: `tcpc,role-def = 5` (Try.SNK), so the port prefers sink. The live capture shows `preferred_role=sink` and `port_type=[dual]`.
- **Suspend**: the TCPC keeps CC detection running (`local-no-suspend` in dpm-caps). In device role MTU3 holds a wakeup source (`pm_stay_awake`). Host-role wake goes through `mediatek,syscon-wakeup`.
- **Accessory handling**: audio accessory (Ra/Ra) is reported to the typec class only. Debug accessory (DBGACC_SNK) counts as sink. The internal thermal "accessory" is **not** Type-C: it is GPIO 28 → `detect_cable`.
