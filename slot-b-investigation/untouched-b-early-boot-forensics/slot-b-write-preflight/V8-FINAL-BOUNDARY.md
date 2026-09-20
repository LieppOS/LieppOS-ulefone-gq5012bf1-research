# V8 final boundary

Fresh Slot-B execution reached and completed late-fs instrumentation, but:

    v8-mtk-pfsd-start=0
    v8-modules-ready-passed=0

Both V8 files retained their pre-boot seed timestamps.

Android init parses the main system init.rc before processing its deferred
imports, including vendor init.mt6878.rc. Therefore the system init.rc
`on post-fs-data` action is registered ahead of the MT6878 post-fs-data action.

The late-init action queues post-fs-data before queued late-fs actions are
processed. Since fresh late-fs actions executed, the post-fs-data event had
already been queued.

Therefore V8 places the current boot boundary inside an earlier
post-fs-data action, with the main system init.rc action the primary boundary.

The MTK `wait_for_prop vendor.all.modules.ready 1` was not reached and is not
the immediate blocker in this boot.

The first executable command of the system post-fs-data action is:

    exec - system system -- /system/bin/vdc checkpoint prepareCheckpoint

V9 should instrument the system post-fs-data action directly.

PHONE_MODIFIED=0
