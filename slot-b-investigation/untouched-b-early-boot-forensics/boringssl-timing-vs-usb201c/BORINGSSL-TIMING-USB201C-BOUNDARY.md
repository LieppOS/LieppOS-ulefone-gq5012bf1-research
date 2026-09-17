# Slot-B BoringSSL timing vs USB-201c boundary

## Correction

The previously suspected missing vendor BoringSSL executable condition is
false.

Current B contains both:

- `/vendor/bin/boringssl_self_test32`
- `/vendor/bin/boringssl_self_test64`

and contains vendor zygote trigger files for both:

- `zygote64`
- `zygote64_32`

Therefore the proposed deterministic chain:

missing `/vendor/bin/boringssl_self_test*`
-> exec_start failure
-> `reboot_on_failure reboot,boringssl-self-check-failed`

is closed.

## Remaining BoringSSL question

The system and vendor BoringSSL self-test binaries still differ from working A,
which is expected to be possible across different Android builds and is not
itself proof of failure.

The stronger discriminator is boot ordering.

The vendor self-tests are started through `exec_start` during early-init.
The system self-tests are started during the init phase.
Conscrypt/APEX self-tests are started when `apexd.status=ready`.

All carry:

`reboot_on_failure reboot,boringssl-self-check-failed`

The historical B investigation separately reached MediaTek USB VID:PID
`0e8d:201c`, previously identified as the ordinary ADB/FunctionFS gadget path.

If exact init semantics and current-B rc ordering prove that all applicable
BoringSSL tests complete synchronously before that USB/ADB state can be
reached, then the historical 201c observation strongly disfavors BoringSSL
self-test failure as the Slot-B reset cause.

## Historical fallback caveat

A preserved Tier3 fallback getprop snapshot contains a stopped
`boringssl_self_test64_vendor` service and a corresponding boot-time property.

That snapshot must not be attributed to B until its slot suffix/fingerprint is
checked, because its path is under `fallback/` and may represent working A
after recovery.

## Safety

This investigation is read-only on the phone.

No self-test binary is manually executed.
No slot is changed.
No partition or persistent Android state is modified.
