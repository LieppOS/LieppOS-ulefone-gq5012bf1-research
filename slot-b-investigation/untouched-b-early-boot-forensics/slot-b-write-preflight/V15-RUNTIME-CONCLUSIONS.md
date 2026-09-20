# V15 runtime conclusions

V15 produced the following fresh transitions:

    v15-mtkgki-early-init=1
    v15-after-ready-zero=1
    v15-after-insmod-start=1

while these service-state markers remained seed-only:

    v15-insmod-running=0
    v15-insmod-stopped=0

Therefore init executed and returned from:

    start insmod_sh

but the instrumentation did not observe the service entering either the
running or stopped init.svc state.

This strongly shifts investigation away from module-specific modprobe hangs
and toward failure to start/exec the insmod_sh service itself.

V15 also produced:

    v15-before-force-ready=1
    v15-after-force-ready=1
    v8-modules-ready-passed=1

Therefore the explicit init-side:

    setprop vendor.all.modules.ready 1

succeeded sufficiently for the subsequent:

    wait_for_prop vendor.all.modules.ready 1

to return.

The previous modules-ready barrier is therefore crossed diagnostically.

The stale:

    40-vendor-modules-ready=0

must not be interpreted as evidence that the setprop failed, because
wait_for_prop observed the required value.

The post-fs-data action:

    v15-ready-zero-at-postfsdata=1

executed later even though the forced value had already become 1. This is
consistent with an event/property-qualified action having been selected when
the post-fs-data event originally occurred while the property was still 0.

The next investigation must establish exact init action ordering and determine
why insmod_sh never reaches an observed running/stopped service state before
adding more runtime bypasses.

V12 system remains frozen.
V15 vendor pair remains the current Slot-B diagnostic vendor.
EXPERIMENT_PHONE_MODIFIED=1
CAPTURE_PHONE_MODIFIED=0
