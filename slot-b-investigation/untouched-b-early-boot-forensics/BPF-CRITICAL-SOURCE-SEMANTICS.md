# Current-B critical BPF source semantics

Two remaining current-B critical platform BPF objects now have exact source
and build-definition provenance.

## bpfRingbufProg.o

Source:

`system/bpf/progs/bpfRingbufProg.c`

The program is explicitly documented as a test-only program.

It defines:

- a BPF ring-buffer map;
- one socket-filter BPF program;
- minimum program kernel version 5.8.0;
- use of ringbuf reserve/submit helpers;
- critical label `BPF Ringbuf test`.

Its Soong module is:

`bpfRingbufProg.o`

and `system/bpf/loader/Android.bp` requires this object only through the
`product_variables.debuggable` dependency.

This provides a concrete explanation for why stock Slot A, which identifies as
a user/release-keys build, does not contain this object while a debuggable
custom Slot-B build can contain it.

If the exact stock GKI cannot create the ringbuf map or verify/load this
socket-filter program, the critical-object semantics can propagate to the
legacy BPF loader fatal path.

No such failure has been observed.

## filterPowerSupplyEvents.o

Source:

`hardware/interfaces/health/utils/libhealthloop/filterPowerSupplyEvents.c`

The program:

- is an AOSP health component, not Ulefone-specific;
- is built as a vendor BPF object;
- is installed into vendor through the base vendor product configuration;
- is a socket-filter program used to filter power-supply netlink uevents;
- explicitly requires kernel >= 5.10.0 because the source documents verifier
  rejection on Linux 5.4;
- carries critical label `healthd`.

The Ulefone stock kernel is Linux 6.1.115, so the source-declared minimum
kernel version is satisfied. Exact helper/verifier compatibility still needs
to be checked against the exact GKI source before completely closing the
branch.

## Important loader-version caveat

The legacy platform `Loader.cpp` search has not yet proven that it consumes
the ELF `bpfloader_min_ver` and `bpfloader_max_ver` sections.

Therefore the previously observed object metadata range [41,65536) must not
yet be treated as a proven legacy-loader eligibility gate.

The exact `loadProg()` implementation must be inspected first.

## Current priority

The highest-value BPF discriminator is now the debug-only
`bpfRingbufProg.o`.

If the exact 6.1.115 Google GKI source proves:

- BPF ring-buffer map support;
- ringbuf reserve/submit helper implementations;
- availability of those helpers to socket-filter programs;

then no concrete static incompatibility remains for this object.

Absent direct runtime failure evidence, BPF should then be demoted in favor of
other second-stage reboot authorities.
