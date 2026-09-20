# Default-backed hwservicemanager V4 runtime result

Slot B was booted with the V4 diagnostic vendor pair.

The V4 instrumentation uses `${property:-ABSENT}`, so every late-fs
snapshot should produce an explicit value even when the property does
not exist.

The relevant snapshots are:

- servicemanager.ready
- hwservicemanager.ready
- hwservicemanager.disabled
- init.svc.servicemanager
- init.svc.hwservicemanager
- completion of the V4 late-fs diagnostic action

No marker interpretation is recorded here until the captured values are
reviewed.

