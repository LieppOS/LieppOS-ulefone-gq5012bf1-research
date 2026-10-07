# Interaction with the internal thermal camera

Authoritative detail: `reverse-engineering/thermal-camera/internal-usb/` and workspace
`DONE/INTERNAL-THERMAL-USB`. This file records only the external consequence.

1. ThermoVue writes `tiny2c_usb_mode=1`: module rails GPIO149→191→192 go high, then
   `yft_usb_flag=1`.
2. It writes `tiny2c_mode=1`: extcon directly queues HOST (this sysfs path is not flag
   gated). If a PC gadget session is active, extcon changes DEVICE→HOST; MTU3 disconnects
   the UDC and populates xHCI. Wired ADB/MTP/etc disappears.
3. While the flag is 1, normal Type-C attach/detach and DR_SWAP role changes, charger psy
   DEVICE requests, and BC1.2 PHY switching are suppressed. SOURCE_VBUS on/off is not
   suppressed.
4. On stop, stock drops the thermal rails and clears the flag, then writes
   `tiny2c_mode=0`, forcing HOST→NONE.
5. Stock does **not** re-evaluate the still-attached external PC/charger state. No new
   TCPC or power-supply edge occurs, so the gadget remains detached until cable replug
   (or another relevant event). This is runtime-captured stock behavior.

Thus internal thermal and external Type-C data are not independent: they share one PHY,
one role switch and one MTU3 instance. The persistent configfs composition may still say
ADB/MTP/etc, but role NONE means no electrical gadget connection; replug causes charger
classification/DEVICE selection and the already requested gadget can enumerate again.
