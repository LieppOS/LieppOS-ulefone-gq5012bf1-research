# Slot-B BoringSSL self-test A/B identity audit

## Shared APEX state

Shared active/staged APEX update state is classified:

`CLOSED`

Observed counts:

- active `/data/apex/active` APEX/CAPEX packages:
  `0`
- `/data/apex/sessions` child entries:
  `0`
- `/metadata/apex/sessions` child entries:
  `0`
- `/metadata/apex/images/active` child entries:
  `0`

## BoringSSL reboot-critical service boundary

Reboot-critical BoringSSL service blocks found in current B:

`6`

A/B byte-identical executable controls:

`0`

A/B differing executable controls:

`2`

B self-test executables absent on working A:

`1`

Missing direct shared-library dependencies:

`0`

Preserved Tier3 direct BoringSSL failure evidence:

`NO`

## Verdict

BORINGSSL_A_B_BINARY_DIFFERENCE_PRESENT: at least one reboot-critical self-test executable differs between working A and current B. Static source/build comparison is required before closing this branch.

## Safety

The phone remained booted on working Slot A.

No self-test executable was run manually.

No B binary was copied to or executed from `/data/local/tmp`.

No partition, APEX, slot state, boot-control metadata, `/data`, `/metadata`,
or persistent Android state was modified.

Working-A executable bytes were streamed read-only over adb only for host-side
hash/ELF identity inspection.
