# Type-C attach/data-role state machine

Owners: MT6375 TCPC hardware → `tcpc_class` policy → notifier chain. `rt_pd_manager`
updates `/sys/class/typec/port0`; exact `extcon-mtk-usb` selects the MTU3 data role;
MT6375 charger classifies sink attachments. The port is Try.SNK DRP, Rp 1.5 A,
preferred sink.

| event/state | Type-C class | extcon/data consequence | power consequence |
|---|---|---|---|
| UNATTACHED → ATTACHED_SNK / NORP_SRC / CUSTOM_SRC / DBGACC_SNK | DEVICE, SINK, polarity/opmode | direct sink handler is intentionally bypassed (`mediatek,bypss-typec-sink=1`); charger classification later requests DEVICE for power-supply type USB/USB_CDP | MT6375 is sink; BC1.2/PD decides charging |
| classified SDP | unchanged | psy notifier: NONE→DEVICE | sink; SDP current policy outside scope |
| classified CDP | unchanged | psy notifier: NONE→DEVICE | sink; CDP |
| classified DCP/Apple/Samsung | unchanged | no DEVICE role; remains NONE | charge-only |
| classified unknown TA | unchanged | stock reports power-supply **TYPE=USB** (USB_TYPE=DCP), so psy notifier attempts NONE→DEVICE; enumeration depends on partner | sink; stock quirk |
| PD/PPS sink ready | power role SINK; PD contract owned by charger | MT6375 forces reported type USB_CDP, so NONE→DEVICE; PD voltage/current algorithm is out of scope | sink under PD/PPS |
| UNATTACHED → ATTACHED_SRC | HOST, SOURCE | queue HOST → xHCI | separate SOURCE_VBUS event turns boost on |
| ATTACHED_DEBUG | HOST/SOURCE path | host | source VBUS as notified |
| ATTACHED_AUDIO | AUDIO partner | no USB role | no analog-audio route exists |
| attached supported state → UNATTACHED | partner removed; reset to preferred SINK/DEVICE, orientation NONE | queue NONE; gadget stops or xHCI depopulates | SOURCE_VBUS(0) turns boost off; charger attach NONE clears BC1.2 state |
| TYPEC_PROTECTION (water/protection state) | `rt_pd_manager` treats it like unattached for Type-C class | extcon has **no explicit TYPEC_PROTECTION branch**; data-role cleanup depends on a separate UNATTACHED/other event | TCPC protection policy owns electrical safety |
| DR_SWAP → UFP | data role DEVICE | if not DEVICE: queue NONE then DEVICE | power role unchanged |
| DR_SWAP → DFP | data role HOST | if not HOST: queue NONE then HOST | power role unchanged |
| PR_SWAP | power role updated by `rt_pd_manager` | **no direct data-role change**; extcon psy path only adds DEVICE when current role is NONE | VBUS follows later SOURCE_VBUS notification |
| VCONN_SWAP | VCONN class state only | none | TCPC owns VCONN |

`extcon_wq` serializes queued role records and updates EXTCON_USB/EXTCON_USB_HOST before
calling `usb_role_switch_set_role`. Role and VBUS are separate TCPC events, so transient
source/host or sink/device ordering is allowed; they are not one atomic transaction.

While `yft_usb_flag=1`, Type-C attach/detach and DR_SWAP role changes and charger psy role
requests are suppressed, but SOURCE_VBUS is **not** suppressed. See
`thermal-interaction.md`.
