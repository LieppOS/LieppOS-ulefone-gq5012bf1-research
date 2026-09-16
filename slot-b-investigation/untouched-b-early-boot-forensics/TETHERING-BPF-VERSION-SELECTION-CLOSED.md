# Tethering BPF object-version selection closed

Exact Android 15 `NetBpfLoad.cpp` source proves that whole ELF objects are
filtered before maps/programs are loaded.

For each object:

- if `bpfloader_ver < bpfloader_min_ver`, the object is ignored and loadProg
  returns success;
- if `bpfloader_ver >= bpfloader_max_ver`, the object is ignored and loadProg
  returns success;
- otherwise the object is processed.

Android-V root netbpfload computes bpfloader version 46.

Current-B objects therefore resolve as follows:

- `offload.o`: [2,19) -> intentionally skipped
- `test.o`: [2,19) -> intentionally skipped
- `offload@mainline.o`: [43,65536) -> processed
- `test@mainline.o`: [43,65536) -> processed
- `netd_shared/netd.o`: [43,65536) -> processed
- `net_shared/clatd.o`: [43,65536) -> processed
- `net_shared/dscpPolicy.o`: [43,65536) -> processed

`loadAllElfObjects()` treats version-filtered objects as successful loads.

Therefore coexistence of legacy and `@mainline` BPF objects is intentional and
BPF loader-version selection is CLOSED as an explanation for the Slot-B boot
failure.

The remaining BPF boundary is limited to actual runtime loading/verifier
failure of a selected object or failure in the subsequent platform-bpfloader
handoff.
