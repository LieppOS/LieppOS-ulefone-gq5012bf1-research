# Slot-B BPF static investigation boundary

## Runtime linker resolution

`/system/bin/linker64` in current B is an absolute symlink:

`/apex/com.android.runtime/bin/linker64`

The earlier host-side `test -e` result reported it as missing because the host
does not provide Android's runtime `/apex` namespace.

The exact current-B `com.android.runtime.apex` payload contains:

`/bin/linker64`

with:

- size: 2201792 bytes
- SHA256:
  `34f6226623cef8717ba8def604bc7bd75ebb7fa9305a9faa345a877cc3170417`
- Build ID:
  `c1af9809aff4f64a8a094e823115dd2a`

Therefore the B platform bpfloader interpreter path is structurally valid.

## Platform-loader fatal semantics

Exact Android 15 `system/bpf/loader/Loader.cpp` shows that failed ELF objects
only propagate failure from `loadAllElfObjects()` when the object contains a
`critical` section.

For an object without `critical`, a load failure is logged but does not make
the location fatal.

Among the current-B platform BPF objects inspected, the objects with an
explicit `critical` section are:

- `/system/etc/bpf/bpfRingbufProg.o`
- `/vendor/etc/bpf/filterPowerSupplyEvents.o`

The other inspected system/memevents/uprobestats/GPU/time/fuse objects do not
carry an observed `critical` section and therefore are optional under this
loader path.

A critical-object failure would cause:

`legacyBpfLoader()`
-> 20 second sleep
-> `exit(121)`
-> unsuccessful `bpfloader` service
-> `reboot_on_failure reboot,bpfloader-failed`

No such failure has been observed on B.

Final static discriminator: compare these two critical objects against the
known-working Slot-A copies on the exact same kernel.

If both are byte-identical, no static BPF incompatibility has been found and
the BPF branch should be demoted absent direct runtime evidence.
