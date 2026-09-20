# Slot-B service-state V3 diagnostic plan

V2 proved that event-triggered checkpoint actions execute on Slot B, while
property-triggered lifecycle checkpoints remained untouched.

The vndservicemanager control is invalid for this B system: its rc definition
is empty and its executable is absent.

Android init Service::Start() also has several error returns before
NotifyStateChange("running"), including executable lookup, SELinux context
calculation, fork and process-group setup.

V3 therefore avoids property-trigger instrumentation entirely.

At fs, post-fs and late-fs it directly expands and persists the current values
of init.svc.logd, init.svc.lmkd, init.svc.servicemanager,
init.svc.hwservicemanager and hwservicemanager.ready.

These actions use event triggers already proven operational by the previous
Slot-B checkpoint boots.

PHONE_MODIFIED=0
