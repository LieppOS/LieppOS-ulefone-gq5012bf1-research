# Slot-B split-permission crash provenance

The authorized Slot-B diagnostic boot isolated the current boot blocker to a
framework PermissionManager failure rather than an early boot, AVB, KeyMint,
or basic userdata-mount failure.

Observed fatal exception:

`java.lang.IllegalStateException: Unknown source permission
com.google.android.gms.permission.ACTIVITY_RECOGNITION in split permissions`

The crash occurs during PackageManager startup through
`AppIdPermissionPolicy.evaluatePermissionState()` and
`onStorageVolumeMounted()`. `system_server` dies and zygote restarts.

The preceding Slot-B capture also demonstrated mounted `/data` and user-0
storage, with vold and keystore2 still running.

`split-permission-provenance.txt` records a read-only search for the exact
declaration/state causing this mismatch.

No partitions were written by this provenance investigation.
