# Current-B critical BPF source provenance

Source-tree provenance for both remaining current-B critical platform BPF
objects is now identified.

## bpfRingbufProg.o

Current-B path:

`/system/etc/bpf/bpfRingbufProg.o`

Source-tree file:

`system/bpf/progs/bpfRingbufProg.c`

SHA256 of current-B object:

`b2088414e626beec57b20dfc5ec2436e9604f665f04a65d5d9fa2cb39249aa5c`

Critical label:

`BPF Ringbuf test`

## filterPowerSupplyEvents.o

Current-B path:

`/vendor/etc/bpf/filterPowerSupplyEvents.o`

Source-tree file:

`hardware/interfaces/health/utils/libhealthloop/filterPowerSupplyEvents.c`

SHA256 of current-B object:

`27abd945bb43678877723b8ca5d181e1255b38a3618499b28a1bf69607e53cf2`

Critical label:

`healthd`

No exact compiled copy of either object was retained in the current Lineage
`out/` tree, so source-tree provenance does not by itself prove byte-identical
binary provenance.

## A/B platform BPF generation difference

Working Slot A currently contains platform BPF files with `.bpf` suffixes:

- `cputimeinstate/timeInState.bpf`
- `fuseMedia.bpf`
- `gpuMem.bpf`
- `gpuWork.bpf`
- `memevents/bpfMemEvents.bpf`

No normal `/vendor/etc/bpf` object was observed on working A.

Current B instead contains `.o` platform objects, including:

- `bpfRingbufProg.o`
- `fuseMedia.o`
- `gpuMem.o`
- `gpuWork.o`
- `memevents/bpfMemEvents.o`
- `memevents/bpfMemEventsTest.o`
- `timeInState.o`
- three uprobestats objects
- vendor `filterPowerSupplyEvents.o`

Therefore working A and current B use materially different platform-BPF
layouts/generations.

A's successful boot proves generic BPF capability of the stock Ulefone kernel,
but it does not directly validate B's two B-only critical objects.

The exact numeric legacy platform-bpfloader version remains unresolved and
must not yet be assumed from the Tethering netbpfload version.
