# Failure and shutdown semantics

| failure/event | stock behavior | consequence/recovery |
|---|---|---|
| GPIO28 acquisition, IRQ mapping or IRQ request fails | `id_pin_init` returns error; probe logs it and continues | no boot sample and no insertion/removal handling; Type-C portions still operate |
| GPIO152 parse/request/direction fails | parser returns -1; probe logs and continues | later ID work still calls GPIO152 set with no readback/error path; accessory likely unpowered |
| GPIO55 parse/request/direction fails | parser returns -1; probe logs; status sysfs still attempted | worker skips route write (`>0` guard) but still changes power/status/role; host can be selected on wrong route |
| `uvc_insert_status` creation fails | logged only | hardware works; SystemUI/factory readers fail |
| IRQ bounce | both edges queue same zero-delay work; no debounce | edges can coalesce; worker applies final sampled level, possibly rapid power/route changes |
| role-record allocation fails | return ignored after GPIO/status update | routed/powered uSmart with old data role |
| `usb_role_switch_set_role`/xHCI fails | return ignored and cached role updated | status says inserted but no root hub/enumeration; no rollback/retry |
| USB enumeration fails | no kernel timeout/rollback | GPIO152/55/status/HOST persist until removal/other event |
| unsupported device | usbcore may enumerate; camera app may ignore/fail to open | remains powered/routed/HOST; status remains 1 |
| camera app/process crash | usbfs fds/claims close, but app never owned GPIOs/role | accessory remains powered, routed and HOST until physical/event change |
| removal during stream | power is cut first, route changes second, role NONE queued last | abrupt USB disconnect/transfer errors; app receives detach if alive |
| removal with Type-C still attached | route returns external, role forced NONE | previous external role not restored; replug/new event needed |
| Type-C event during uSmart | no uSmart gate | role can become DEVICE/NONE/HOST while GPIO55/152 remain uSmart |
| thermal start while uSmart attached | thermal HOST request cannot change GPIO55 | uSmart route wins; Tiny2-C may not enumerate |
| uSmart edge during thermal | GPIO/status change before thermal gate; role stays thermal HOST | uSmart can steal route; removal returns route without clearing HOST |
| boot with accessory attached | after successful IRQ registration, synchronous LOW sample powers/routes and queues HOST before userspace | autonomous enumeration; SystemUI prompt may miss an already-completed attach broadcast |
| orderly kernel shutdown | extcon shutdown disables only Type-C MT6375/GPIO37 source VBUS | no explicit GPIO152/55/status/NONE cleanup; reset/power loss is relied upon |
| driver remove | returns 0, no cleanup | no hot-unbind-safe teardown |

Stock has no reconciler that compares GPIO28, GPIO55, cached role, Type-C state and thermal
ownership. Recovery is event-driven: remove/reinsert, Type-C replug, or thermal transition.
