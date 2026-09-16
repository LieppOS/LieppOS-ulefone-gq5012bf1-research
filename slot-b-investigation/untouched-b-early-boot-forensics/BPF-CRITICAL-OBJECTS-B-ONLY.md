# Current-B critical BPF objects absent from working A

The proposed A/B byte-comparison could not be performed because the working
Slot-A filesystem returned no files at:

- `/system/etc/bpf/bpfRingbufProg.o`
- `/vendor/etc/bpf/filterPowerSupplyEvents.o`

Current B does contain both objects.

## Current-B critical objects

### bpfRingbufProg.o

Path:

`/system/etc/bpf/bpfRingbufProg.o`

SHA256:

`b2088414e626beec57b20dfc5ec2436e9604f665f04a65d5d9fa2cb39249aa5c`

Critical label:

`BPF Ringbuf test`

### filterPowerSupplyEvents.o

Path:

`/vendor/etc/bpf/filterPowerSupplyEvents.o`

SHA256:

`27abd945bb43678877723b8ca5d181e1255b38a3618499b28a1bf69607e53cf2`

Critical label:

`healthd`

Exact Android 15 platform BPF loader semantics prove that failure of an object
with a `critical` section propagates from `loadAllElfObjects()`.

The resulting platform-loader path is:

critical object load failure
-> `legacyBpfLoader()`
-> 20-second sleep
-> exit 121
-> unsuccessful `bpfloader` service
-> `reboot_on_failure reboot,bpfloader-failed`

The successful Slot-A boot does not statically validate these two B objects
because no matching Slot-A objects were found at the checked paths.

This does NOT prove that either object fails on B.

The remaining BPF investigation is limited to these two critical objects:
their provenance, loader/kernel eligibility, exact BPF requirements, and any
preserved historical failure evidence.

All broader Tethering/cache/linker/dependency/version-selection BPF hypotheses
remain closed or strongly bounded.
