# Slot-B debug ringbuf BPF static compatibility closed

## Legacy loader object selection

Exact Android 15 platform `Loader.cpp` proves that legacy `loadProg()` does
not consume the ELF sections:

- `bpfloader_min_ver`
- `bpfloader_max_ver`

`loadAllElfObjects()` enumerates every `.o` file in its configured
directories and invokes `loadProg()`.

`loadProg()` reads the critical/license/program/map data and attempts map and
program creation.

Therefore the previously observed object metadata range `[41,65536)` is not a
legacy platform-loader eligibility gate and must not be used to reason about
whether the two critical platform objects are selected.

## bpfRingbufProg.o

Current B contains:

`/system/etc/bpf/bpfRingbufProg.o`

Source:

`system/bpf/progs/bpfRingbufProg.c`

The source defines a test-only socket-filter program with:

- one BPF ring-buffer map;
- minimum program kernel version 5.8.0;
- `bpf_ringbuf_reserve`;
- `bpf_ringbuf_submit`;
- critical label `BPF Ringbuf test`.

The module is included through the `product_variables.debuggable` dependency
of the platform bpfloader.

## Exact stock GKI compatibility

The exact Ulefone Google GKI source contains:

- `BPF_MAP_TYPE_RINGBUF`;
- ring-buffer map verifier support;
- `bpf_ringbuf_reserve` implementation and function prototype;
- `bpf_ringbuf_submit` implementation and function prototype;
- both helpers in `bpf_base_func_proto()`.

The socket-filter verifier helper dispatcher falls back to
`bpf_base_func_proto()`, making those ringbuf helpers available to socket
filter BPF programs.

The exact verifier also explicitly validates ringbuf map/helper compatibility.

The Ulefone kernel is Linux 6.1.115, above the program's declared 5.8 minimum.

Conclusion:

No concrete static kernel incompatibility has been found for
`bpfRingbufProg.o`.

A runtime-specific allocation/verifier/state failure remains theoretically
possible, but there is no direct evidence that one occurred during the B boot.

The debug-ringbuf branch is therefore closed as a static explanation for the
Slot-B failure.

## Remaining BPF boundary

The only remaining critical platform object requiring a final static check is:

`/vendor/etc/bpf/filterPowerSupplyEvents.o`

Its AOSP source:

- uses socket-filter BPF;
- explicitly requires kernel >= 5.10;
- carries critical label `healthd`.

The exact Ulefone kernel is 6.1.115.

If its compiled instruction/helper requirements are supported by the exact
GKI source, BPF should be demoted absent direct runtime evidence of
`bpfloader-failed`.
