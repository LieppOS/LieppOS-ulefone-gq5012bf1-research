# V8 runtime interpretation

V8 directly brackets the real MT6878 post-fs-data action:

    v8-mtk-pfsd-start
    wait_for_prop vendor.all.modules.ready 1
    v8-modules-ready-passed

Interpretation:

- start=1, modules-ready-passed=0:
  the MTK post-fs-data action started and main init was still blocked at
  vendor.all.modules.ready=1 when execution stopped progressing.

- start=1, modules-ready-passed=1:
  the module-ready wait completed and the blocker is later.

- start=0:
  execution did not reach the MTK post-fs-data action; an earlier action for
  the same event, or an earlier event/action, must be investigated.

The absence of usable Slot-B ADB is not used as evidence for any of these
boundaries.

PHONE_MODIFIED=0
