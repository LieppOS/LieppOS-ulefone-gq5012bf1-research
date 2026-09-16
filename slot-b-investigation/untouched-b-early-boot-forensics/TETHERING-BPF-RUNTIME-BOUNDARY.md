# Current-B Tethering BPF runtime boundary

## Source provenance

The exact current-B Tethering init scripts are byte-identical to the current
Lineage 22.2 Connectivity source tree.

`netbpfload.35rc`:

`b6eb65420c99148ad0c9ebc611d9733768d1d07085e52b8028502111ebbe58a3`

`netbpfload.33rc`:

`39d672ed2881de6ecd27340cbe008b700894084f00fb80041ee3212b55612f57`

Therefore B's bpfloader init/reboot policy is not explained by a stale or
foreign RC artifact.

The exact old B APEX artifact was not found in the present Lineage `out/`
tree. This is only negative artifact-retention evidence and does not establish
different source provenance.

## Concrete fatal mechanism

Exact `NetBpfLoad.cpp` source shows that if:

`loadAllElfObjects(...)`

fails for any required location, netbpfload logs a critical BPF-loading
failure, sleeps for 20 seconds, and exits with status 2.

B's exact Android-V init definition has:

`reboot_on_failure reboot,bpfloader-failed`

Therefore a required BPF object verifier/load failure provides a concrete
Android-controlled Slot-B reboot mechanism.

This mechanism is temporally compatible with a delayed second-stage reboot,
but it has not been observed directly on B.

## Generic kernel checks

Android V requires Linux 6.1 to be at least 6.1.57.

The Ulefone kernel is 6.1.115 and has the core required BPF configuration
enabled. Working Slot A also successfully boots a newer Android-15 Tethering
BPF stack on this exact kernel.

Therefore generic lack of BPF support is strongly disfavored.

The remaining BPF hypothesis is specific to B's own v352 netbpfload/BPF
objects or to its post-mainline handoff.

## Post-mainline handoff

When running as root, netbpfload attempts to exec:

`/apex/com.android.uprobestats/bin/uprobestatsbpfload`

and if that fails falls back to:

`/system/bin/bpfloader`

If the platform loader exec also fails, netbpfload returns nonzero and the
init reboot-on-failure policy applies.

B does not package the same uprobestats APEX observed on working A, so the
existence and usability of B's `/system/bin/bpfloader` is the next static
check.

No claim is made yet that B actually failed in the BPF path.
