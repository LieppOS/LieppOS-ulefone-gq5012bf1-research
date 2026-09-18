# Slot-B kernel/watchdog/reset-producer audit

## Investigation boundary

The Android init paths previously prioritized are now bounded:

- BoringSSL: statically closed as the prioritized reset cause.
- BPF: statically closed/demoted.
- zygote fatal path: strongly demoted because no critical-window assignment
  was found and `window=off` prevents `SVC_CRITICAL` from being set.
- ordinary bare-critical fatal loops: incompatible with the shortest observed
  B reset cycles because at least ~20 seconds are required to reach the fifth
  crash.
- missing hwservicemanager: closed; the executable is present, and an actually
  missing executable fails before fork and cannot increment the crash counter.
- known init `reboot_on_failure` branches: exhausted by previously closed or
  substantially demoted paths.

## Timing

Preserved B observations include reset intervals of approximately:

- 5.623 seconds after one 201C observation;
- 4.256 seconds after another 201C observation.

These timings do not prove a watchdog or panic timeout because 201C
enumeration is not the fault timestamp.

They do justify checking reset mechanisms capable of acting after a single
fault.

## Live stock-kernel panic setting

`/proc/sys/kernel/panic`:

`-1`

Short positive panic timeout (<=10 s):

`False`

## Watchdog infrastructure

Watchdog device visible on working A:

`True`

High-signal current-B userspace binaries containing watchdog/power-control
markers:

`0`

Current-B kernel module candidates:

`1`

Historical unique `wdt_status` values located:

`0x800`

## Classification

WATCHDOG_RESET_INFRASTRUCTURE_PRESENT: direct producer still requires isolation.

## Important limitation

Working-A kernel/watchdog settings are a control. They are relevant because
the physical B boot/kernel path has previously been shown to use the stock
kernel-side payload, but a live-A value is not itself proof of the exact
runtime state immediately before a failed-B reset.

Historical returned-A bootreason properties are likewise not treated as
failed-B evidence.

## Safety

This audit is read-only on working Slot A and host-side for current-B files.

No B boot was performed.
No binary was executed from B.
No partition or slot metadata was modified.
No persistent phone state was changed.
