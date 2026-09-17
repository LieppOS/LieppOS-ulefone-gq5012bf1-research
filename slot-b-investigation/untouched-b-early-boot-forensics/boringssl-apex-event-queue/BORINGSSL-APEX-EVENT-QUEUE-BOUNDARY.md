# Slot-B BoringSSL APEX event-queue boundary

## Already closed

The vendor BoringSSL tests run via synchronous `exec_start` during
`early-init`.

The platform/system BoringSSL tests run via synchronous `exec_start` during
`init`.

Second-stage init queues `early-init` before `init` before `late-init`.

Given the separately established non-KPOC interpretation of the historical
Slot-B ordinary ADB observations, those two BoringSSL stages are excluded as
the later reset source.

Both vendor self-test architectures also have matching-bitness direct library
closure.

No direct historical `boringssl-self-check-failed` token has been recovered.

## Important PID correction

MediaTek PID `0x201C` is not unique to one USB state.

The current vendor rc assigns it to both:

- KPOC ADB; and
- ordinary ADB with zero ACM ports.

Therefore PID 201C alone cannot distinguish KPOC from ordinary Android ADB.
The ordinary-ADB interpretation relies on the separate KPOC investigation and
its boot-mode/property evidence.

## Remaining BoringSSL window

The Conscrypt/APEX BoringSSL self-test is different.

It is triggered by:

`apexd.status=ready`

and runs through synchronous `exec_start`.

The remaining question is the Android init event queue ordering between:

1. `post-fs-data`;
2. the property change to `apexd.status=ready`;
3. the resulting property-trigger action;
4. `zygote-start`;
5. `early-boot`;
6. `boot`;
7. USB ADB configuration and FunctionFS readiness.

If the property-trigger action is necessarily processed before the `boot`
event, historical ordinary ADB progress excludes the APEX self-test as well.

If the property-trigger event is appended behind an already queued `boot`
event, USB progress does not by itself exclude a later APEX BoringSSL failure.

## Safety

This investigation is read-only.

The phone remains on working Slot A.

No B executable is run.
No partition is modified.
No slot metadata is modified.
No persistent Android state is modified.
