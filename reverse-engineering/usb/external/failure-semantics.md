# Failure semantics (static)

| failure / conflict | stock behavior | recovery / consequence |
|---|---|---|
| extcon role-record allocation fails | `mtk_usb_extcon_set_role` returns `-ENOMEM`; all notifier/sysfs callers ignore it | old role remains; next attach/property/sysfs edge may retry |
| underlying `usb_role_switch_set_role` fails | `update_role` ignores return and still assigns `c_role=new_role` after changing extcon state | software can report target role while MTU3 did not switch; detach/replug is the normal new edge |
| xHCI population/enable fails | role/extcon can remain HOST but no root hub/device appears | detach/role NONE tears host path down; reattach retries |
| FunctionFS producer absent | ADB/MTP/PTP readiness trigger never fires, so composition is not UDC-bound | starting producer or selecting another composition recovers |
| configfs UDC bind/write fails | init has no conditional error branch and still executes `setprop sys.usb.state` | requested/applied properties may claim success while host sees no gadget; `none`→new config or replug/restart retries |
| gadget cable detach during transfer | TCPC/charger → role NONE; MTU3 gadget disconnect/stops; host sees removal | gadget composition persists in configfs and re-enumerates after a fresh valid DEVICE attach |
| VBUS voltage/current/enable fails | GPIO37 was already raised; `set_vbus` returns error, but notifier ignores it and `vbus_on` stays false | HOST may exist without powered external device; later SOURCE_VBUS/off or detach lowers GPIO37; next attach retries |
| VBUS disable fails | return ignored; driver records off and clears current-limit state | potential regulator/hardware inconsistency; no software retry until next event |
| BC1.2 PHY acquisition/mode fails | error logged; classification path cannot cleanly hand D+/D− between charger detector and USB | gadget role may be absent/misclassified; detach/replug reruns detection |
| CDP-block never clears | waits up to 250 × 100 ms, logs timeout, then continues BC1.2 enable | delayed device-mode discovery |
| DCP | no DEVICE role by design | charge-only; no gadget enumeration |
| unknown TA | reported TYPE=USB, so DEVICE is attempted even though USB_TYPE=DCP | harmless gadget attempt if no data host exists |
| thermal takeover during gadget | DEVICE→HOST disconnects ADB/MTP/etc; flag suppresses external role/BC1.2 events | thermal stop forces NONE and does not restore DEVICE; external cable replug required |
| Type-C cable changes during thermal | role changes suppressed; SOURCE_VBUS is not | after thermal stop state may be stale; replug/re-event required |
| uSmart insertion | GPIO152 power + GPIO55 route happen before HOST request; external Type-C pair is removed from fabric | removal returns route but forces NONE; external cable replug may be required |
| Type-C event while uSmart active | no uSmart gate; later TCPC/psy event can override HOST/NONE while GPIO55 remains uSmart | last role event wins; toggle/replug appropriate connector to re-evaluate |
| uSmart edge during thermal | GPIOs/status still change, role request suppressed after changes | can disrupt thermal route while keeping HOST; remove accessory to return GPIO55 |
| external OTG detach | SOURCE_VBUS off and role NONE are independent events | boost off + xHCI depopulation; a new attach rebuilds host |
| PR_SWAP without DR_SWAP | power role/VBUS changes but data role stays unchanged | valid independent roles; subsequent DR_SWAP changes data |
| TCPC TYPEC_PROTECTION state | Type-C class drops partner/resets roles, but extcon has no explicit protection-state role branch | electrical protection remains TCPC-owned; data cleanup relies on a separate UNATTACHED/role event |

No watchdog in extcon reconciles physical Type-C, uSmart and thermal state. Recovery is
edge-driven; cable replug, GPIO28 edge or an explicit thermal sysfs transition supplies a
new decision.
