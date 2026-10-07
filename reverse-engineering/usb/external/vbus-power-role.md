# VBUS, power role and data role

These are separate state machines.

| concern | owner | operation | data-role effect |
|---|---|---|---|
| sink VBUS | MT6375 charger + charging framework | consumes external VBUS; BC1.2/PD/UFCS policy and input limits | charger power-supply type may cause extcon DEVICE |
| source VBUS | TCPC SOURCE_VBUS → exact `extcon-mtk-usb` → GPIO37 + MT6375 `usb-otg-vbus` regulator | fixed request 5.25 V / 1.8 A; off disables regulator and clears limit flag | none directly; normally paired with ATTACHED_SRC→HOST |
| limited source | AIDL IUsb `limitPowerTransfer` → `vbus_limit_cur` | write 1: 0.5 A; 0: 1.8 A, only applied when boost already on | none |
| data role | Type-C TYPEC_STATE/DR_SWAP or charger psy → extcon → MTU3 role switch | DEVICE/HOST/NONE | selects UDC or xHCI |
| Type-C power role | AIDL IUsb sysfs request → `rt_pd_manager` → TCPC PR swap | SINK/SOURCE class state | no direct extcon role change |
| VCONN | TCPC | e-marker/CC supply | none |
| gadget MaxPower | configfs `configs/b.1/MaxPower=500` mA | descriptor consumed by external host | not a source-boost limit |

## Ordering and quirks

- `set_vbus(on)` raises GPIO37 **before** regulator voltage/current/enable. It records
  `vbus_on=true` only after success. Callers ignore its return value.
- `set_vbus(off)` lowers GPIO37, calls regulator_disable without checking its return,
  clears `vbus_cur_inlimit`, then records off.
- Calling `vbus_limit_cur=1` while VBUS is off records the flag but changes no regulator
  current; the later on path still programs 1.8 A. The HAL should limit after source VBUS
  is active.
- A PR_SWAP only updates the power role. Data remains as-is unless a DR_SWAP/attach/psy
  event changes it; source VBUS follows TCPC's independent SOURCE_VBUS notification.
- On sink detach the charger owns power-path cleanup; on source detach extcon owns boost
  shutdown. PD/PPS voltage/current selection is deliberately outside this USB scope.
