# Slot-B watchdog-core handoff audit

## Previous result

Working A has:

- `watchdogd-gsi` running;
- `/system/bin/watchdogd 10 20`;
- an open `/dev/watchdog` fd;
- approximately 10.002-second userspace feed cadence.

Current B has no matching watchdogd service or binary.

That differential is real.

## Important refinement

The differential is **not sufficient by itself** to prove watchdog expiry.

Live kernel watchdog-core parameters:

- `handle_boot_enabled=Y`
- `open_timeout=0`
- `stop_on_reboot=-1`

Exact local Linux watchdog-core source establishes:

- a boot-enabled running watchdog can be fed by the kernel before userspace
  opens the watchdog device;
- `open_timeout=0` maps the userspace takeover deadline to `KTIME_MAX`;
- therefore the pre-userspace feeding period has no finite takeover deadline.

Kernel-core protection classification:

`True`

The local MTK watchdog reference source also checks whether the WDT was
already enabled and marks such a device `WDOG_HW_RUNNING`.

Reference-source result:

`True`

Because the live `mtk_wdt` module is out-of-tree, that reference behavior is
not yet treated as proof of the exact Ulefone module.

## Watchdog timing correction

Working A runs:

`/system/bin/watchdogd 10 20`

AOSP watchdogd calculates requested watchdog timeout as:

`interval + margin`

so this command requests approximately a 30-second watchdog timeout while
feeding it every 10 seconds.

Therefore the approximately 9.454- and 10.815-second B cycles match the feed
cadence but **not** the timeout configured by working-A watchdogd.

## Kernel panic branch

Working A reports:

- `kernel.panic=-1`
- `kernel.panic_on_oops=1`

A negative panic value causes immediate reboot after panic.

With `panic_on_oops=1`, an ordinary kernel oops is therefore capable of an
immediate reboot and remains timing-compatible with the short B cycles.

## Current boundary

MISSING_WATCHDOGD_ALONE_STRONGLY_DEMOTED: the Linux watchdog core is configured to feed a boot-enabled hardware watchdog indefinitely before userspace opens it, and the local MTK reference driver marks an already-enabled WDT as WDOG_HW_RUNNING. The exact loaded Ulefone/MediaTek mtk_wdt module still needs equivalence/probe-timing verification.

The next discriminators are:

1. exact live Ulefone/MediaTek `mtk_wdt` driver behavior;
2. exact driver probe/load timing relative to Android USB;
3. whether it inherits a running bootloader watchdog and hands it to the
   generic watchdog core;
4. kernel oops/panic versus hard watchdog reset evidence.

## Safety

All device operations were read-only.

The audit did not open `/dev/watchdog`.

It did not issue a watchdog ioctl.

It did not write a watchdog keepalive.

It did not change any sysctl.

It did not boot Slot B or modify any partition or persistent phone state.
