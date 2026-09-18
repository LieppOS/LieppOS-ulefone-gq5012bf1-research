# Slot-B reset investigation boundary before watchdog audit

## hwservicemanager correction

The previous missing-hwservicemanager hypothesis is closed.

Current B contains:

`/system_ext/bin/hwservicemanager`

The separate host mount layout caused an incorrect earlier path inference.

Additionally, Android init checks a service executable using `stat()` before
fork. A genuinely missing executable therefore fails `Service::Start()` before
a child exists and cannot directly increment the critical-process crash
counter.

## Zygote

No actual assignment to:

`zygote.critical_window.minute`

was found in the inspected current-B property/init material.

The zygote declaration defaults this to `off`.

Exact Android init parser semantics return from `ParseCritical()` for
`window=off` before setting `SVC_CRITICAL`.

Therefore zygote's critical fatal path is strongly demoted by current static
evidence.

## Bare-critical service timing

Android init:

- clamps abnormal service restart periods to at least 5 seconds;
- enters fatal handling only after `crash_count_ > 4`.

The earliest fifth-crash fatal event is therefore approximately 20 seconds
after the first abnormal exit.

Preserved B USB/reset timing includes:

- 201C at +10.240 -> preloader at +15.863 = 5.623 s
- 201C at +142.198 -> preloader at +146.454 = 4.256 s

Thus ordinary five-crash fatal handling cannot directly explain the shortest
observed B reset cycles.

It may still be relevant to longer attempts, but it cannot be the sole reset
mechanism for all observed cycles.

## Android init immediate-reset inventory

The current-B `reboot_on_failure` inventory contains only branches already
closed or substantially demoted by prior work:

- BoringSSL
- BPF
- apexd / apexd-bootstrap
- vold

The `on property:sys.powerctl=*` action in the vendor rc is a consumer of an
existing power-control request, not evidence identifying the producer.

## Next boundary

The investigation now prioritizes:

- kernel panic and panic timeout;
- watchdog reset;
- MediaTek watchdog/AEE reset producers;
- vendor userspace writers of `sys.powerctl`;
- explicit reboot/reset syscalls or watchdog-device accesses.

No conclusion that a watchdog or panic actually occurred is made yet.
