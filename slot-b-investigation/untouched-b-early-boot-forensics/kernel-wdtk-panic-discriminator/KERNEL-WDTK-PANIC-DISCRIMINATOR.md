# Slot-B kernel WDTK / panic discriminator

## PHH watchdogd correction

Working A's `watchdogd-gsi` is defined in a PHH/Treble-GSI-specific
`vndk.rc`.

That same file contains PHH-specific services and properties.

Current B is not that PHH GSI system and does not contain this compatibility
layer.

Therefore absence of `watchdogd-gsi` from B is not independently a packaging
defect.

## Kernel-side watchdog architecture

Working A exposes:

- generic kernel watchdog worker: `True`
- MediaTek `wdtk-*` kernel thread count: `8`
- MediaTek/live WDK symbol evidence: `True`
- watchdog pre-userspace handling enabled:
  `Y`
- watchdog userspace open timeout:
  `0`

Historical MediaTek source independently corroborates that MediaTek WDK
implementations create per-CPU `wdtk-%d` threads and use them to kick the
hardware watchdog.

Thus `[wdtk] kick watchdog` should be treated as kernel-side MediaTek WDK
evidence, not as proof that PHH's userspace watchdogd generated the kick.

## A/B kernel identity

Raw boot partitions identical:

`True`

Kernel payload identical:

`True`

Boot partition SHA256 values:

`{
  "boot_a": "8648d0c9f071603ff601b49a656e1f52b5a6bae762772a4fd2cd8d73feb44927",
  "boot_b": "8648d0c9f071603ff601b49a656e1f52b5a6bae762772a4fd2cd8d73feb44927"
}`

Kernel extraction result:

`{
  "boot_a": {
    "kernel_sha256": "IMPLIED_BY_IDENTICAL_BOOT_PARTITION"
  },
  "boot_b": {
    "kernel_sha256": "IMPLIED_BY_IDENTICAL_BOOT_PARTITION"
  }
}`

## mtk-wdt integration

Driver bound:

`True`

Module sysfs absent:

`False`

Built-in config detected:

`False`

Built-in classification:

`False`

## Generic watchdog-starvation classification

GENERIC_WATCHDOG_STARVATION_STRONGLY_CLOSED: A and B use the same kernel payload, the generic watchdog core is configured for indefinite pre-userspace feeding, and the live kernel contains both its watchdog worker and MediaTek wdtk threads. Absence of PHH watchdogd-gsi on B is not a sufficient reset cause.

This classification does **not** close MediaTek hang detection or an
intentional WDK-triggered reset.

It closes/demotes the narrower theory that B simply resets because nobody
starts PHH's userspace `watchdogd-gsi`.

## Panic path

Live stock-kernel state:

- `kernel.panic=-1`
- `kernel.panic_on_oops=1`

Classification:

`IMMEDIATE_OOPS_PANIC_PATH_OPEN`

With `panic=-1` and `panic_on_oops=1`, an oops can produce an immediate
reboot without waiting for a multi-second userspace crash counter.

Current-B static panic/sysctl override hit count:

`3`

## Current priority

If kernel identity and watchdog-core feeding are both proven, the next
high-value branches are:

1. kernel oops/panic;
2. MediaTek WDK/hangdet intentionally forcing reset because a CPU or subsystem
   stops responding;
3. MediaTek AEE/mrdump reset handling.

Generic watchdog starvation and PHH watchdogd packaging should not consume
further bring-up time without new contradictory evidence.

## Safety

Everything in this audit is read-only on the phone.

Boot partitions are only hashed/read.

No watchdog device is opened.

No watchdog ioctl is issued.

No watchdog keepalive is written.

No sysctl is changed.

No Slot-B boot or partition write is performed.
