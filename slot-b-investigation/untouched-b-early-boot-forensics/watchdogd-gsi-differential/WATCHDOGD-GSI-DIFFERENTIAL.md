# Slot-B watchdogd-gsi / MTK hardware watchdog differential

## Important correction: kernel panic timeout

The previous audit classified:

`SHORT_KERNEL_PANIC_TIMEOUT=0`

because it only considered positive panic values.

That interpretation was incorrect.

Live working A reports:

`kernel.panic=-1`

Linux semantics are:

- `0`: remain in panic indefinitely;
- positive: reboot after that many seconds;
- negative: reboot immediately.

Therefore:

`NEGATIVE_PANIC_MEANS_IMMEDIATE_REBOOT=True`

Current `panic_on_oops`:

`1`

Thus an oops on this configuration would enter panic and immediately reboot:

`True`

This makes a standard kernel oops/panic timing-compatible with a fast reset,
although it does not prove that an oops actually occurred.

## Generic kernel watchdog sysctl correction

`/proc/sys/kernel/watchdog=0` controls Linux's generic lockup detectors.

It does not establish that the MediaTek hardware watchdog is disabled.

Working A separately exposes `/dev/watchdog` and loads `mtk_wdt`.

## Working-A watchdog daemon

`init.svc.watchdogd-gsi` state:

`running`

Process owns an existing `/dev/watchdog` or `/dev/watchdog0` file descriptor:

`True`

This inspection did not open the watchdog device itself.

## Current-B watchdog material

Current-B watchdogd rc references:

`0`

Current-B files named watchdogd:

`0`

## AOSP watchdogd behavior

Local source checks:

- default interval 10 seconds: `True`
- default margin 10 seconds: `True`
- opens `/dev/watchdog`: `True`
- requests timeout `interval + margin`: `True`

The exact runtime argv is recorded in:

`live-a-watchdogd-process.txt`

and must be used instead of assuming the defaults.

## Historical B timing

Short preloader-to-preloader cycle durations:

`10.815s, 9.454s`

The approximately ten-second short cycles are a correlation only.

They do not independently establish a watchdog timeout.

## Classification

STRONG_WATCHDOGD_GSI_DIFFERENTIAL: working A has a running watchdogd-gsi that owns the hardware watchdog device, while current B has no watchdogd service definition in its mounted Android files. This can plausibly allow the MTK hardware watchdog to expire during B boot and must be resolved before further generic userspace debugging.

## Safety

The audit is read-only on working Slot A and host-side for current-B files.

It did not open `/dev/watchdog`.

It did not issue a watchdog ioctl.

It did not change kernel sysctls.

It did not boot Slot B.

It did not modify partitions, slot metadata, `/data`, `/metadata`, or other
persistent phone state.
