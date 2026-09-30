# Same-boot fastbootd BootControl race test

Live OrangeFox evidence established that the MTK AIDL BootControl service
initially failed registration because its VINTF declaration was not yet
available, then restarted approximately five seconds later and registered
successfully.

AOSP FastbootDevice acquires BootControl during construction and retains that
client for the lifetime of the fastbootd process.

This test therefore starts fastbootd only after OrangeFox already has a
working MTK IBootControl service, without rebooting recovery.

No partition flash, erase, resize, create or delete operation is performed.
