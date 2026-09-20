# hwservicemanager path hypothesis conclusion

The Slot-B system image contains:

`/system/system_ext -> /system_ext`

The stock Ulefone system image contains the same compatibility symlink.

The host-side failure to access:

`b-mounts/system/system/system_ext/bin/hwservicemanager`

does not indicate an Android runtime failure. The symlink target is absolute,
so ordinary host pathname resolution attempts to use the host `/system_ext`
instead of the separately extracted Android `system_ext` partition.

Therefore the missing-runtime-path hypothesis is closed.

The next diagnostic distinguishes:

- hwservicemanager never starting;
- hwservicemanager entering running and immediately exiting;
- hwservicemanager restarting;
- hwservicemanager being explicitly disabled;
- a broader essential-service/property-trigger problem.

`servicemanager` and `vndservicemanager` running transitions are included as
controls.

No phone modification was performed.
