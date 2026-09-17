# Slot-B BoringSSL final chronology boundary

## Confirmed corrections

The preserved Tier3 fallback `getprop` snapshot is Slot A, not Slot B.

It reports:

- `ro.boot.slot_suffix=_a`
- stock Ulefone fingerprint
- `ro.zygote=zygote64`
- `sys.boot_completed=1`

It therefore cannot be used as runtime evidence that B completed a BoringSSL
test.

Current B does contain both vendor BoringSSL executables:

- `/vendor/bin/boringssl_self_test32`
- `/vendor/bin/boringssl_self_test64`

The earlier missing-executable hypothesis is closed.

The preceding dependency report also contained an analysis error: the 32-bit
self-test was allowed to match libraries under `vendor/lib64`. That result is
invalid. The corrected audit resolves 32-bit and 64-bit dependencies only
against matching-bitness directories and treats libc/libm/libdl as Android
runtime/Bionic dependencies rather than ordinary vendor-private libraries.

## Vendor BoringSSL chronology

Current B's vendor zygote-specific rc executes the applicable vendor
BoringSSL self-test from `early-init` using `exec_start`.

Android init's `exec_start` uses the SVC_EXEC wait-style execution path.

The historical controlled Slot-B run subsequently reached MediaTek USB
VID:PID `0e8d:201c`, already established as the ordinary ADB/FunctionFS
gadget path rather than KPOC.

Therefore the vendor BoringSSL self-test path is strongly excluded as the
reset source: boot progressed beyond its synchronous early-init execution.

## Remaining question

The remaining BoringSSL question is limited to chronology of:

1. system BoringSSL self-test;
2. Conscrypt/APEX BoringSSL self-test triggered by `apexd.status=ready`;
3. initialization of `sys.usb.config`;
4. adbd setting `sys.usb.ffs.ready=1`;
5. MTK USB gadget binding with product ID 0x201c.

If exact init ordering places every applicable BoringSSL self-test before the
0x201c gadget can bind, the entire BoringSSL branch can be closed.

## Historical failure evidence

No preserved direct `boringssl-self-check-failed` token has been identified.

## Safety

This investigation is read-only on the phone.

No B executable is run.
No partition is written.
No slot metadata is changed.
No persistent Android state is modified.
