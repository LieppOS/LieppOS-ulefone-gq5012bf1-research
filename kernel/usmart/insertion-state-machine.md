# Insertion, removal and boot state machine

Owner: exact `extcon-mtk-usb.ko` (`mtk_usb_extcon_id_pin_init`,
`mtk_usb_idpin_handle`, `mtk_usb_extcon_detect_cable`).

## Probe

1. Parse/request GPIO152 and GPIO55 as outputs; each is initialized LOW.
2. Create `uvc_insert_status` (kernel mode 0444).
3. Acquire GPIO28 as `GPIOD_IN`; map it to an IRQ.
4. Register a threaded ONESHOT IRQ on **both rising and falling edges**.
5. Sample GPIO28 synchronously.
6. If LOW: GPIO152=1 → GPIO55=1 → status=true → queue HOST.
7. If HIGH: do nothing; defaults remain power=0, route=external, status=false,
   cached role=NONE.

The probe-time LOW path does not consult `yft_usb_flag`. Userspace is not required for
boot-with-accessory enumeration.

## Runtime edge

The threaded IRQ queues the same delayed-work object on
`system_power_efficient_wq` with delay **0**. There is no hardware/software debounce,
sleep, settle delay, retry, accessory-type check or GPIO readback. Repeated edges while
the work is pending may coalesce; the worker reads the final GPIO28 level.

| order | inserted: GPIO28 LOW | removed: GPIO28 HIGH |
|---:|---|---|
| 1 | GPIO152 = HIGH (power) | GPIO152 = LOW (power cut) |
| 2 | GPIO55 = HIGH (uSmart route) | GPIO55 = LOW (external route) |
| 3 | `uvc_insert_status = 1` | `uvc_insert_status = 0` |
| 4 | if `yft_usb_flag==1`, return; else queue HOST | if `yft_usb_flag==1`, return; else queue NONE |

The thermal flag therefore suppresses only step 4, **not** power, routing or status.
This ordering supersedes older reports that placed the gate at function entry.

Role work runs asynchronously on the single-thread `extcon_usb` workqueue. It changes
EXTCON state, invokes `usb_role_switch_set_role`, updates the cached role, and has no
completion handshake with enumeration.
