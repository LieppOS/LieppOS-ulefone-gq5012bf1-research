# Slot-B immediate-reset authority boundary

## hwservicemanager correction

The preceding `STRONG_MISSING_HWSERVICEMANAGER_CANDIDATE`
classification was incorrect.

The current-B `system_ext` logical partition contains:

`/system_ext/bin/hwservicemanager`

Host path:

`/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/untouched-b-early-boot-forensics/b-mounts/system_ext/bin/hwservicemanager`

Present:

`True`

SHA256:

`89f2497e83b4677259c110c48ff39fb566939abff5dbaa8ef168126637d31e43`

The previous broad filename-discovery pass failed to include this executable,
while the direct path-mapping pass correctly showed that it exists.

Android runtime path aliases/mounts must not be inferred directly from the
separate host logical-partition mount layout.

## More important init semantic correction

Even a genuinely absent service executable would not, by itself, produce the
critical crash loop previously proposed.

`Service::Start()` checks the executable with `stat()` before fork.

If the executable cannot be found:

- the service is marked disabled;
- `Start()` returns an error;
- no child is created;
- `Service::Reap()` is not entered;
- the critical crash counter is not incremented.

Thus the missing-executable fatal-loop theory is closed independently of the
fact that the B executable actually exists.

## Zygote

Actual current-B assignments to:

`zygote.critical_window.minute`

found:

`0`

Working-A current value:

`ABSENT`

Android init's `window=off` handling returns before setting `SVC_CRITICAL`.

Static effective-noncritical result:

`True`

Absent contrary early property evidence, the zygote-fatal crash-counter path
is strongly demoted.

## Bare critical-service timing bound

Android init clamps abnormal service restarts to at least five seconds.

Fatal handling occurs only when the critical crash count exceeds four.

Therefore the earliest theoretical fatal action from a continuously crashing
bare-critical service is approximately:

`20 seconds`

after its first abnormal exit.

Fastest preserved 201C-to-next-preloader interval:

`4.256 seconds`

Compatibility with that minimum:

`False`

The total first quick B attempt from the preserved preloader observation at
+5.048 s to the next preloader observation at +15.863 s is only 10.815 s,
which is itself shorter than the minimum five-crash sequence.

Therefore ordinary bare-`critical` crash loops such as lmkd,
servicemanager, or hwservicemanager do not explain the shortest observed B
reset cycles.

## Current priority

The investigation now prioritizes reset mechanisms that can act on a single
failure or explicit action:

- `reboot_on_failure`;
- `sys.powerctl`;
- explicit reboot/shutdown actions;
- vendor/MediaTek watchdog or fatal reset mechanisms.

Open immediate-reset authorities discovered by this run:

- none

## Safety

All B analysis was host-side.

The phone remained on working Slot A.

No Slot-B boot was performed.
No partition or slot metadata was modified.
No persistent phone state was changed.
