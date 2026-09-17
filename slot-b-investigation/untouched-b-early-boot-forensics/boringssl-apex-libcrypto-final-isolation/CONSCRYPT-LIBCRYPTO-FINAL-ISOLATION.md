# Slot-B Conscrypt libcrypto final isolation

## Major narrowing

The active Slot-B architecture is 64-bit only for this investigation.

The current-B Conscrypt self-test executable:

`/apex/com.android.conscrypt/bin/boringssl_self_test64`

is byte-identical to current B's earlier platform/system self-test executable.

Self-test executable SHA256:

`1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`

The remaining difference is therefore the linked 64-bit BoringSSL library.

Conscrypt APEX libcrypto:

`55cac6cb4581a9533ad56a66579804fb44a7fb7d1afb8f9ae63e36ff248679f3`

Platform/system libcrypto:

`660fa9a8e01922171c300d60aa862d3cea8b1752c4b73ae0c459d2b9d73f15f7`

The Conscrypt APEX direct dependency audit previously found no definite
architecture/bitness failure.

Thus the remaining BoringSSL hypothesis is no longer a generic self-test,
init, binary, APEX-state, or dependency hypothesis. It is specifically:

**whether the current-B Conscrypt 64-bit libcrypto implementation fails its
BoringSSL self-test on this device.**

## Historical control

The preserved Tier3 fallback log is Slot A.

Its Conscrypt APEX self-test started synchronously and exited with status 0,
so it is a valid behavior/timing control only, not Slot-B runtime evidence.

No preserved direct `boringssl-self-check-failed` token from B has been found.

## Host differential

QEMU result:

`QEMU_TEST_NOT_AVAILABLE`

System-pair return code:

`None`

Conscrypt-pair return code:

`None`

A host QEMU pass is supporting evidence but does not replace a real MT6878
runtime result because CPU HWCAP dispatch and Android runtime details can
differ.

A differential result where the system pair passes and the Conscrypt pair
fails under the same harness would materially strengthen the Conscrypt
libcrypto branch.

## Safety

All APEX extraction and differential execution are host-side.

The phone remained on working Slot A.

No Slot-B binary or library was copied to or executed on the phone.

No partition, slot metadata, `/data`, `/metadata`, APEX state, or persistent
phone state was modified.
