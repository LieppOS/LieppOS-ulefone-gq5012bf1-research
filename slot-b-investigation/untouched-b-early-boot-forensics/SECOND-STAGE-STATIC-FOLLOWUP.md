# Slot-B second-stage static follow-up

## Fatal service binaries

Exact current Slot-B filesystems contain valid executables for:

- `/system/bin/apexd`
- `/system/bin/vold`
- `/vendor/bin/boringssl_self_test32`
- `/vendor/bin/boringssl_self_test64`

`/system/bin/netbpfload` is absent, but this is expected by the shipped
`netbpfload.rc`: the service is updatable and is intended to be overridden by
the `com.android.tethering` APEX. The fallback service executes
`/system/bin/false` and has:

`reboot_on_failure reboot,netbpfload-missing`

Therefore a failure to activate/load the Tethering APEX can manifest as
`netbpfload-missing`; the absent `/system/bin/netbpfload` is not itself the
defect.

## Exact Android 15 init semantics

`reboot_on_failure` triggers shutdown/reboot whenever the service cannot start
or terminates unsuccessfully.

For a `critical` service, Android init counts unsuccessful exits. Before
`sys.boot_completed=1`, the fifth failure triggers a fatal reboot.

Immediately before that fatal reboot init writes:

`persist.init.svc.last_fatal_reboot_epoch`

The marker is throttled so another native critical-service fatal reboot is not
performed within 24 hours.

This property is therefore a potentially persistent forensic marker for the
September untouched-B failure.

## Packaged APEX divergence

Current B and stock A have different packaged APEX module sets.

Both contain common core modules including ART, runtime, conscrypt, tethering,
Wi-Fi, permission and media.

Notable stock-A-only modules include:

- `com.android.bt`
- `com.android.compos`
- `com.android.crashrecovery`
- `com.android.telephonycore`
- `com.android.uprobestats`
- `com.google.android.widevine.nonupdatable`
- `com.android.vndk.v32`

Current B instead contains `com.android.btservices` and additional virtual
biometrics/CAS APEXes.

This difference is not inherently invalid, but because `/data/apex` is shared
between A and B, persistent APEX state is now a concrete compatibility branch.

Next checks:

1. read `persist.init.svc.last_fatal_reboot_epoch`;
2. inventory shared `/data/apex` state read-only;
3. establish whether A-only persistent APEX state exists;
4. prove the B Tethering APEX contains the expected bpfloader override.
