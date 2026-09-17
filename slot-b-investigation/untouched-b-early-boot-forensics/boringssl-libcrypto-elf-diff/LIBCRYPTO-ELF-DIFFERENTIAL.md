# Slot-B system vs Conscrypt libcrypto exact ELF differential

## Correction to previous run

Commit `1f5295b` was successful.

Its terminal footer was wrong because it attempted to re-hash files from a
Python temporary directory after that directory had already been deleted.

The footer's `SELFTEST_BINARY_IDENTICAL=0` is therefore invalid evidence.

Fresh extraction in this run establishes:

- B platform self-test:
  `1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`
- B Conscrypt self-test:
  `1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`
- byte-identical launcher:
  `True`

## libcrypto whole-file identity

Platform libcrypto:

- size: `1442904`
- SHA256: `660fa9a8e01922171c300d60aa862d3cea8b1752c4b73ae0c459d2b9d73f15f7`

Conscrypt libcrypto:

- size: `1442912`
- SHA256: `55cac6cb4581a9533ad56a66579804fb44a7fb7d1afb8f9ae63e36ff248679f3`

Size delta:

`8` bytes

Differing bytes within common file length:

`28592`

## Runtime/FIPS equivalence

`.text` byte-identical:

`True`

Critical functions byte-identical:

`True`

BoringSSL BCM text region byte-identical:

`True`

BoringSSL BCM rodata region byte-identical:

`True`

Sections with nonzero runtime addresses that differ:

`.bss, .note.gnu.build-id`

## Verdict

CONSCRYPT_LIBCRYPTO_FIPS_EXECUTION_PATH_BYTE_IDENTICAL: the launcher, .text, critical FIPS/self-test functions, and both BoringSSL BCM FIPS text/rodata regions are byte-identical between the B platform and Conscrypt copies. Whole-file differences remain, but the actual FIPS self-test execution regions are not different.

## Interpretation

The BoringSSL launcher calls `FIPS_mode()` and `BORINGSSL_self_test()` from
the linked libcrypto.

A whole-file libcrypto hash difference is therefore only meaningful if it
changes code/data used by that FIPS path.

This audit compares the actual FIPS functions and the BoringSSL BCM text and
rodata regions directly rather than treating Build-ID or ELF metadata changes
as functional differences.

## Safety

All Conscrypt extraction and comparison were host-side.

The phone remained booted on working Slot A.

Slot B was not booted.

No B executable was executed.

No partition, APEX state, slot metadata, `/data`, `/metadata`, or other
persistent phone state was modified.
