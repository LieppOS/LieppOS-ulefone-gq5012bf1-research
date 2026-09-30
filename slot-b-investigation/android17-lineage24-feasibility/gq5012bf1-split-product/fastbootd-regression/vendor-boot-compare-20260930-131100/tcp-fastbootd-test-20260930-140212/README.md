# TCP fastbootd after BootControl readiness

USB handoff testing proved that a late-started OrangeFox fastbootd obtains the
MediaTek AIDL IBootControl service, but manual USB gadget switching disconnects
ADB before providing a reliable host fastboot transport.

AOSP fastbootd natively supports TCP transport through:

    fastbootd.protocol=tcp

The TCP fastboot server listens on port 5554.

This experiment starts fastbootd only after the MTK AIDL BootControl service is
healthy, keeps USB ADB intact, forwards host TCP port 15554 to device TCP port
5554 through ADB, and performs read-only fastboot getvar operations.

No flash, resize, erase, partition creation/deletion, slot activation, userdata
operation, or metadata operation is performed.
