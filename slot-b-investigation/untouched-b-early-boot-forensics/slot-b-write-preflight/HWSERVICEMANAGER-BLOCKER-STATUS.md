# hwservicemanager Slot-B blocker audit

MT6878 vendor init has a hard late-fs dependency:

`wait_for_prop hwservicemanager.ready "true"`

The B system_ext init definition declares:

`service hwservicemanager /system/system_ext/bin/hwservicemanager`

The first audit did not find a regular hwservicemanager binary beneath the
mounted B system/system_ext trees.

This follow-up resolves exact paths and symlinks before deciding whether this
is a proven missing-executable boot blocker.
