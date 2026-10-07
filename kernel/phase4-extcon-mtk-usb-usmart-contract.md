# GQ5012BF1 — extcon-mtk-usb uSmart state-machine contract

**Corrected 2026-10-07 from the exact reconstructed source.** Full integration closure:
[`usmart/README.md`](usmart/README.md). The underlying module remains byte-level closed;
no reconstruction was redone.

## uSmart GPIO28 path

| state | exact synchronous worker order | later asynchronous action |
|---|---|---|
| GPIO28 LOW (inserted) | GPIO152 HIGH → GPIO55 HIGH → `uvc_insert_status=true` | if `yft_usb_flag==0`, queue `USB_ROLE_HOST` |
| GPIO28 HIGH (removed) | GPIO152 LOW → GPIO55 LOW → `uvc_insert_status=false` | if `yft_usb_flag==0`, queue `USB_ROLE_NONE` |

The thermal flag check is **after** GPIO/status updates. Earlier documentation that placed
it at function entry and claimed no GPIO change was wrong.

GPIO28 is acquired `GPIOD_IN`; IRQ is threaded ONESHOT on both rising/falling edges; the
handler queues zero-delay work. There is no debounce, wait or retry. After successful IRQ
registration, probe samples GPIO28; LOW applies the inserted state immediately, while
HIGH relies on already-initialized LOW outputs/static-false status/NONE role.

## GPIO initialization and sysfs

`yft_parse_dts` gets/requests each raw output, calls `gpio_direction_output(...,0)`, then
sets LOW. GPIO55 is `uvc_switch_gpio`, GPIO152 is `uvc_vbus_gpio`.
`uvc_insert_status` is 0444, prints `0\n`/`1\n`, has no store and reports physical GPIO
state—not enumeration.

## Role

`mtk_usb_extcon_set_role` allocates zero-delay work on `extcon_wq`; the worker updates
extcon cables, calls `usb_role_switch_set_role` and caches the target without checking the
role-switch return. Allocation failure is returned but ignored by the uSmart worker.
Removal always requests NONE; no prior external role is restored.

## Separation from Type-C VBUS

SOURCE_VBUS handling calls `mtk_usb_extcon_set_vbus`: GPIO37 + MT6375 regulator at
5.25 V / 1.8 A, optionally limited to 0.5 A. It is a separate Type-C notifier branch and
is **not** gated by `yft_usb_flag`. The uSmart GPIO28 worker never calls this function;
its only power action is GPIO152.

## Thermal interaction

`yft_usb_flag` gates ordinary Type-C/psy role decisions and only the final role request of
the uSmart worker. Therefore uSmart can change power/route/status during thermal HOST.
`tiny2c_mode` itself is a pure HOST/NONE request and does not touch GPIO55/152.

## Other exact boundaries

- `usb_is_online` accepts power-supply TYPE USB or USB_CDP.
- `/proc/mtk_typec/smt_u2_cc_mode` is Type-C factory status, not uSmart.
- shutdown disables only Type-C VBUS; remove returns without uSmart cleanup.
- physical connector pinout, GPIO152 rail rating and switch/load-switch parts are
  board-only unknowns.
