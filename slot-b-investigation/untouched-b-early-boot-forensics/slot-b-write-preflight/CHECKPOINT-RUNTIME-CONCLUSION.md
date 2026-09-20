# Instrumented Slot-B runtime conclusion

The persistent checkpoint experiment establishes a runtime boot boundary.

Markers overwritten by Slot B:

- `00-early-init=1`
- `10-fs=1`
- `30-post-fs=1`
- `25-late-fs-trigger=1`

Markers not overwritten:

- `20-hwservicemanager-running=0`
- `21-hwservicemanager-ready=0`
- `40-vendor-modules-ready=0`
- every `post-fs-data` and later milestone remained zero.

The zero-valued files retained their pre-seed timestamps while the reached
markers received timestamps from the actual B boot. Therefore the result is
not an instrumentation-load failure.

`post-fs` precedes `late-fs`; consequently `30-post-fs=1` does not establish
completion of the MT6878 late-fs action.

The MT6878 late-fs action contains:

`wait_for_prop hwservicemanager.ready "true"`

No hwservicemanager running or ready transition was observed.

Runtime failure class:

`SLOT_B_LATE_FS_HWSERVICEMANAGER_READY_STALL_PROVEN_RUNTIME`

This proves the immediate init stall boundary. It does not yet prove the
underlying reason hwservicemanager fails to reach running/ready.

`vendor.all.modules.ready=1` was also not observed and remains a possible
secondary blocker after the late-fs issue is resolved.

pstore remained empty.
