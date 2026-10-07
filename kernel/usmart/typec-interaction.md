# Interaction with external Type-C

Authoritative USB details: `reverse-engineering/usb/external/`.

uSmart and Type-C have different detect/power controls but one D+/D− route and one role.
There is no uSmart-active flag or lock.

| starting state / event | exact result |
|---|---|
| PC/device session, then uSmart insert | GPIO152=1, GPIO55=1 removes Type-C D+/D−, status=1, role DEVICE→HOST; gadget/ADB disconnects |
| Type-C OTG HOST, then uSmart insert | route changes to uSmart; HOST request is effectively no-op; Type-C GPIO37/MT6375 source VBUS can remain independently active |
| uSmart active, then Type-C attach/DR_SWAP/detach/psy event | Type-C notifier is not gated by uSmart; it can queue DEVICE/HOST/NONE while GPIO55 stays HIGH and GPIO152 stays HIGH |
| uSmart remove | GPIO152=0, GPIO55=0 returns external route, status=0, role→NONE |
| external cable still attached after removal | no replay/re-evaluation of prior Type-C state; external gadget/host may remain NONE until replug or another event |

Broken-but-stock states are therefore possible: powered uSmart routed with DEVICE/NONE,
external source boost active while the uSmart route is selected, or external route
restored while role remains stale until queued NONE completes. Last queued role work wins;
GPIO state is not part of that serialization.

uSmart's GPIO152 path is not the MT6375/GPIO37 external VBUS path. Type-C SOURCE_VBUS
remains independently controlled even when uSmart is selected.
