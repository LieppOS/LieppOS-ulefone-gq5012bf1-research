# Interaction with the external Type-C port

There is one USB2 PHY port, one MTU3/xHCI and one role switch. Arbitration is purely
software, by **last writer wins** on the role plus the `yft_usb_flag` gate; there is no
lock, priority or refusal path.

| situation | static behaviour | evidence |
|---|---|---|
| PC/charger (phone = device) attached, then thermal start | `tiny2c_usb_mode`=1 sets flag; `tiny2c_mode`=1 → role DEVICE→HOST (`EXTCON_USB`=0, `EXTCON_USB_HOST`=1). Gadget/ADB drops (UDC `not attached`), camera enumerates on `1-1` | exact extcon source; capture pre→active |
| thermal stop with the PC still attached | rails off, flag 0, role HOST→NONE. **Nothing re-asserts DEVICE**: TCPC state did not change and the psy detector only reacts to power-supply events → gadget stays `not attached` until the cable is re-plugged (or another TCPC/psy event) | capture home/restored (`not attached`); source |
| cable attach/detach/DR_SWAP while thermal runs | TCPC role changes ignored ("yft_drv ignore usb func for yft_usb_flag"); psy detector ignored; charger BC1.2 PHY switching skipped (`mt6375_chg_set_usbsw` returns 0) → no D+/D− disturbance of the camera session; charging power path itself is not gated | exact sources |
| OTG device on Type-C (phone = source) + thermal start | role already HOST; `SOURCE_VBUS` is **not** gated, so VBUS stays on; `tiny2c_mode`=1 re-queues HOST (no-op transition). Which D+/D− consumer the host sees is decided by board routing (not software-visible); stock offers no simultaneous use | source; board routing BOARD-ONLY |
| thermal stop with OTG device still attached | role HOST→NONE although Type-C is still `ATTACHED_SRC` and VBUS on → external device unusable until re-plug | source |
| simultaneous internal + external data | not supported (single port, single role); USB2-only fabric (USB stack DONE) | PROVEN |
| Type-C power role | unaffected by thermal (capture: `power_role=source [sink]`, no partner) | capture |

The thermal session therefore **steals the controller** whenever an app writes the two
nodes; protection of the camera session against external events is the flag gate;
restoration of the external role after the session is not implemented in stock.
