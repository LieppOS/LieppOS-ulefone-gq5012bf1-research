# External USB relationship to uSmart

uSmart is a rear physical accessory path, **not** Android Open Accessory protocol and not
the internal Tiny2-C camera.

| signal | exact extcon behavior |
|---|---|
| GPIO28 `id-gpios` | both-edge IRQ; low = accessory present |
| GPIO152 `uvc_vbus_gpio` | low→1 powers/sources the accessory path; removal→0; does not use MT6375 OTG boost |
| GPIO55 `uvc_switch_gpio` | low→1 selects the uSmart D+/D− route; removal→0 returns the external Type-C route |
| `uvc_insert_status` | 1/0 tracks GPIO28 path |
| USB role | insertion queues HOST; removal queues NONE |

The actions are ordered GPIO152 → GPIO55 → status → role. They share the one U2 PHY,
MTU3 and xHCI with Type-C, so uSmart **steals external D+/D−** and external Type-C data
cannot coexist. The exact switch part/netlist is board-only; the route behavior is proven
by DT + exact source + successful external default and accessory/camera captures.

There is no uSmart-active gate on Type-C events. A later Type-C detach/DR/psy event can
therefore override the role while GPIO55 remains on the uSmart route; last queued role
wins until another GPIO28 edge or Type-C event. External Type-C SOURCE_VBUS can also be
controlled independently, although uSmart itself uses GPIO152 power rather than MT6375
boost.

`yft_usb_flag` is checked **after** GPIO152/55/status changes. During thermal operation a
uSmart edge can still power/switch the accessory route (and therefore disrupt thermal
D+/D−), but it skips the uSmart HOST/NONE role request, leaving the thermal HOST role.
Removal restores GPIO55=0 before returning. This ordering is a stock integration quirk.

Deep uSmart device/protocol behavior belongs to its own component; only the shared USB
contract is closed here.
