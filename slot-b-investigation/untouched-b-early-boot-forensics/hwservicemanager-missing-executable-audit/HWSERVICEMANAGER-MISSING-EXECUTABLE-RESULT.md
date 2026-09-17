# Slot-B hwservicemanager missing-executable audit

## Zygote-property correction

The previous critical-service audit reported:

`ZYGOTE_STATIC_WINDOW_SETTER=1`

That label was incorrect.

The previous script counted textual references to
`zygote.critical_window.minute` inside `critical window=...` declarations as
though they were assignments.

This audit distinguishes references from real assignments.

Reference count:

`3`

Actual assignment count:

`0`

Corrected result:

`NO_ACTUAL_ZYGOTE_WINDOW_ASSIGNMENT_FOUND`

Working Slot A currently has:

`zygote.critical_window.minute=ABSENT`

Because Android init returns from `ParseCritical()` when the expanded window
is `off` before setting `SVC_CRITICAL`, absence of an assignment materially
demotes zygote-fatal.

## hwservicemanager anomaly

Current B defines `hwservicemanager` as a bare critical service.

Current B also contains explicit `start hwservicemanager` actions.

A search across all mounted B logical partition trees found an executable
named exactly `hwservicemanager`:

`False`

Number of matching named files:

`0`

Static verdict:

`STRONG_MISSING_HWSERVICEMANAGER_CANDIDATE`

## Why this matters

Bare critical services participate in Android init's crash counter.

Before `sys.boot_completed=1`, repeated abnormal exits are counted regardless
of the normal fatal-crash time window.

Android init's default failed-service restart period is five seconds.

Once the critical crash count exceeds four, init enters its fatal reboot
path, unless the corresponding `init.svc_debug.no_fatal.<service>` escape is
set or the 24-hour fatal-reboot throttle applies.

Therefore a missing executable for an explicitly started critical service can
produce an asynchronous restart/fatal sequence while other init actions
continue far enough for USB state to advance.

## Working-A control

Working A contains and runs hwservicemanager.

See:

`live-a-hwservicemanager-control.txt`

## Historical evidence

Non-fallback Tier3 evidence was searched specifically for:

- hwservicemanager;
- critical-process fatal messages;
- failed exec;
- failed restart.

Direct matches:

`0`

Absence of preserved direct logs does not close this candidate because the B
attempt did not preserve a complete live logcat across reset.

## Safety

This audit was read-only on working Slot A and host-side for Slot-B files.

No B executable was run.
No Slot-B boot was performed.
No partition or slot metadata was modified.
No persistent phone state was modified.
