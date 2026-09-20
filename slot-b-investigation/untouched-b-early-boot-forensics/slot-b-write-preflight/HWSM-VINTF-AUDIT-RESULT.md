# hwservicemanager VINTF audit result

The missing-VINTF-declaration hypothesis is closed.

Slot B contains:

    android.hidl.manager
    @1.2::IServiceManager/default
    transport=hwbinder

The current Lineage output contains the same declaration, and factory Android
contains the equivalent declaration.

The vendor compatibility matrix also references android.hidl.manager.

Therefore there is no static evidence that hwservicemanager should enter its
"HIDL unsupported" / `hwservicemanager.disabled=true` branch.

A runtime getTransport() failure remains possible if VINTF loading or parsing
fails at runtime, but this is no longer the leading static explanation.

V4 will directly snapshot, with default values:

- servicemanager.ready
- hwservicemanager.ready
- hwservicemanager.disabled
- init.svc.servicemanager
- init.svc.hwservicemanager

The `:-ABSENT` syntax prevents a missing property from aborting the diagnostic
write, correcting the main weakness of V3.

PHONE_MODIFIED=0
