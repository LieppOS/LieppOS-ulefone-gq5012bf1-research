# External MediaTek WDK corroboration

Historical MediaTek kernel source in `wd_common_drv.c` is relevant as
architecture/background evidence, not as proof of the exact MT6878 binary.

That source:

- creates one kernel thread per CPU named `wdtk-%d`;
- maintains local CPU watchdog-kicker state;
- periodically calls the MediaTek watchdog restart/kick path;
- uses a kernel-side WDK independent of Android's userspace watchdogd.

The current Ulefone runtime exposes eight kernel tasks named:

`wdtk-0` through `wdtk-7`

in addition to:

- the generic Linux watchdog-core worker `[watchdogd]`; and
- PHH's userspace `/system/bin/watchdogd 10 20`.

Therefore the recurring kernel message:

`[wdtk] kick watchdog`

must not automatically be attributed to PHH's userspace watchdog daemon.

The thread naming and historical MediaTek implementation strongly support a
separate MediaTek kernel WDK/kicker path.

This is corroborating historical MediaTek source evidence. Exact MT6878
function/symbol/stack evidence from the live Ulefone kernel remains preferred
where available.
