# Slot-B hwservicemanager VINTF deadlock candidate

The previous missing-property-context hypothesis is closed.

`hwservicemanager.` is present in:

- current platform sepolicy source;
- generated target plat_property_contexts;
- the mounted Slot-B system;
- factory/TIER3 system artifacts.

The mounted Slot-B and current generated property-context artifacts also have
the same SHA-256.

A stronger candidate is the hwservicemanager VINTF-disabled path.

Before publishing `hwservicemanager.ready=true`, hwservicemanager checks
whether its HIDL service transport is declared. If unsupported, it sets:

    hwservicemanager.disabled=true

and waits for init to stop it.

The corresponding init stop rule is property-triggered. Slot B currently
blocks inside the late-init / late-fs action chain before
queue_property_triggers is reached.

Meanwhile the MT6878 vendor late-fs action synchronously waits for:

    hwservicemanager.ready=true

If Slot-B VINTF causes the disabled path, this forms a circular early-boot
deadlock.

The remaining static question is whether Slot-B VINTF declares the required
android.hidl.manager service/transport.

PHONE_MODIFIED=0
