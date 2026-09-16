# Slot-B critical BPF object eligibility boundary

Two current-B platform BPF objects remain capable of making the legacy
platform BPF load fatal because they contain `critical` sections:

- `/system/etc/bpf/bpfRingbufProg.o`
  - critical label: `BPF Ringbuf test`
  - SHA256:
    `b2088414e626beec57b20dfc5ec2436e9604f665f04a65d5d9fa2cb39249aa5c`

- `/vendor/etc/bpf/filterPowerSupplyEvents.o`
  - critical label: `healthd`
  - SHA256:
    `27abd945bb43678877723b8ca5d181e1255b38a3618499b28a1bf69607e53cf2`

Both objects advertise identical object-level loader metadata:

- `bpfloader_min_ver = 41`
- `bpfloader_max_ver = 65536`
- `btf_min_bpfloader_ver = 42`
- `btf_user_min_bpfloader_ver = UINT32_MAX`

The exact current platform-loader version has not yet been established, so
object eligibility is not yet classified PASS/FAIL.

Exact Android platform-loader source also shows additional per-map and
per-program kernel-version checks before `BPF_PROG_LOAD`.

The preserved TIER3 Phase5 search found no literal evidence for:

- `bpfRingbufProg`
- `filterPowerSupplyEvents`
- `BPF Ringbuf test`
- `CRITICAL FAILURE LOADING BPF PROGRAMS`
- `Platform BpfLoader loading`
- exit 121
- `bpfloader-failed`

Therefore there remains no preserved historical evidence that either critical
object actually failed during the Slot-B boot attempt.

The previous broad source search produced generic healthd/init references but
no established exact source provenance for these two object files.

Next discriminators:

1. establish the exact platform bpfloader version;
2. determine whether both objects are selected by the [41,65536) gate;
3. identify their exact source/build provenance;
4. compare A/B system and vendor generations before using Slot A as an oracle.
