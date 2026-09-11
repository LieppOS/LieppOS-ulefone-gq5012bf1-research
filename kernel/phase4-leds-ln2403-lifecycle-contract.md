# LN2403 lifecycle / PM contract

Module init registers one platform driver named `yft_camplight`; module exit
unregisters it. The sole OF compatible is `mediatek,yft_camplight`.

The remove callback only logs and returns 0. It deliberately does not:

- remove the three device attributes itself;
- cancel either hrtimer;
- disable PWM3;
- force GPIO22 or five output GPIO values off;
- relax or unregister either wakeup source;
- free GPIO requests or the 280-byte heap object;
- clear global pointers.

The device core eventually destroys attributes with the device kobject, but the
callback performs no ordered hardware/resource teardown. These are stock
defects/retained-resource semantics, not reconstruction oversights. Module
unload while active is unsafe for that reason.

The driver has no `.shutdown`, `.suspend`, `.resume`, or `dev_pm_ops`. It does
not auto-quiesce at reboot/suspend and does not restore state. Its only power
integration is wakeup-source holds controlled by sysfs mode stores. This is a
loadable normal-boot vendor_dlkm module and is absent from recovery.
