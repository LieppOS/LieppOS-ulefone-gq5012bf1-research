# MTK watchdog module-handoff / panic-origin audit

## Correction to previous watchdog verdict

The previous result stated that generic watchdog starvation was strongly
closed.

That statement was too broad.

Exact live evidence shows that `mtk_wdt` is a loadable module:

`True`

Likewise:

- `mrdump` modular: `True`
- `aee_hangdet` modular: `True`
- `monitor_hang` modular: `True`

Therefore the Linux watchdog core cannot protect an inherited bootloader
hardware watchdog through the `mtk_wdt` driver until that module has actually
loaded, probed, and registered the watchdog device.

Once registration has happened, current watchdog-core settings strongly
protect against userspace takeover starvation:

- `handle_boot_enabled=Y`
- `open_timeout=0`

So the corrected boundary is:

`POST_REGISTRATION_STARVATION_CLOSED__PRE_REGISTRATION_MODULE_HANDOFF_OPEN`

## Exact MediaTek kicker identity

The prior audit proved that all eight `wdtk-*` threads execute:

`kwdt_thread [aee_hangdet]`

Therefore the repeated `[wdtk] kick watchdog` path is MediaTek
`aee_hangdet`, not PHH's userspace watchdogd.

## Why Slot B can still differ with identical boot/kernel

`boot_a` and `boot_b` are byte-identical, so the kernel payload is identical.

However Slot B has a different `init_boot` ramdisk.

Module-loading orchestration and first-stage userspace can therefore differ
even though the kernel bytes are the same.

The high-value question is not whether the driver binary differs, but whether
B reaches `mtk_wdt` / `aee_hangdet` registration before any inherited watchdog
deadline.

## vendor_dlkm

Existing repo evidence for A/B vendor_dlkm identity found:

`True`

That makes different module *content* less likely.

It does not by itself prove identical module *load timing*.

## Panic path

Live state:

- `kernel.panic=-1`
- `kernel.panic_on_oops=1`

Compiled kernel panic timeout:

`-1`

Classification:

`SAME_KERNEL_COMPILED_IMMEDIATE_PANIC_PATH_PROVEN`

Current-B init files explicitly set `panic_on_oops=1`.

If the compiled/default `panic=-1` setting is confirmed, identical A/B kernel
bytes mean B inherits the same immediate-panic policy unless changed before
the failure.

## Current priorities

1. Determine exact boot-stage/load order for `mtk_wdt`, `mrdump`,
   `aee_hangdet`, and `monitor_hang`.
2. Determine whether B's different init_boot can delay or skip that loading.
3. If watchdog registration is proven early enough, close pre-registration
   starvation and pivot to:
   - kernel oops/panic;
   - `aee_hangdet` intentional reset;
   - `monitor_hang` intentional reset.

## Safety

This audit is entirely read-only.

It does not open `/dev/watchdog`.

It does not issue watchdog ioctls.

It does not write sysctls.

It does not boot B.

It does not modify partitions or slot state.
