# LN2403 safety and power contract

## Kernel-enforced behavior

- Probe and OFF establish all five raw GPIO values low and GPIO22 low; the
  module assumes GPIO directions are already configured.
- Every camping mode transition first cancels any gate timer and disables PWM;
  PWM paths and timer-gated paths are mutually selected by the mode store.
- Brightness is signed-capped only at 94; normal maximum request therefore uses
  threshold 6/100. Fixed HIGH mode uses threshold 1/17 and is electrically a
  different hard-coded path.
- Nonzero camping and warning modes hold separate wakeup sources; only their
  corresponding explicit 0 stores relax them.
- No thermal sensor, current sensor, battery check, runtime limit, regulator,
  LED-class maximum, hardware kill switch, shutdown callback or suspend callback
  exists in this module.

## Userspace policy only

The Outdoor app defaults to 5-minute auto-off and offers 5/10/20/30-minute or
indefinite duration. It limits repeated seekbar values >90 with a 10-minute
cooldown/warning and displays low-power warnings. Power-saving framework policy
forces camping mode and brightness to 0. Red/blue service lifecycle writes 0.
None of these protections applies to arbitrary root/sysfs writers.

## Preserved hazards

Negative brightness and out-of-range warning-mode quirks are retained. Camping
mode rejects values >=6 but accepts negative modes, powers the stage, caches the
negative value and can make its show path hit the compiler bounds trap. Direct
brightness writes do not
cancel a running camping timer. Remove/unload does not cancel timers, turn
off outputs, or release wake resources. GPIO requests are never freed. Therefore
module unload while active and untrusted access to chmod-0777 stock sysfs nodes
are unsafe. These are exact stock defects and explicit acceptance constraints,
not implicit guarantees of this reconstruction.
