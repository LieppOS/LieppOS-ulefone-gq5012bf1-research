# V15 insmod lifecycle + forced modules-ready diagnostic

## Proven V14 result

V14 executed zero modprobe operations while preserving the stock final:

    setprop vendor.all.modules.ready 1

Nevertheless:

    v8-mtk-pfsd-start=1
    v8-modules-ready-passed=0
    40-vendor-modules-ready=0

Therefore neither system_dlkm nor vendor module loading is required to
reproduce the modules-ready barrier.

The remaining candidate path is:

    init.mtkgki.rc
      -> early-init action
      -> start insmod_sh
      -> init.insmod.sh execution
      -> cfg access/parsing
      -> setprop vendor.all.modules.ready 1

V15 instruments that service lifecycle.

V15 also forces:

    setprop vendor.all.modules.ready 1

from init immediately before the MTK post-fs-data wait. This is diagnostic
only and is intended to cross the already isolated modules-ready barrier.

## Existing later boundary

V14 reached:

    v9-odsign-key-done=1
    v9-snapshotde-passed=1

before:

    v8-mtk-pfsd-start=1

while:

    v9-before-odsign-verify=0

remained old.

If V15 crosses the MTK wait, existing later markers may reveal the next
blocking action.

The V12 system pair remains unchanged.
PHONE_MODIFIED=0
