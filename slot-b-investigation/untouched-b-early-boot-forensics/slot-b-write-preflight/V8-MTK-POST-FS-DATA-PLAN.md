# V8 exact MTK post-fs-data boundary

V7 proved the real MT6878 late-fs action completes, including mount_all --late.

The old LieppOS 50-post-fs-data marker cannot prove that the post-fs-data
event itself was never dispatched because other actions for that event can run
before the checkpoint action.

The MT6878 post-fs-data action begins with:

    wait_for_prop vendor.all.modules.ready 1

V8 instruments that real action directly.

Markers:

    v8-mtk-pfsd-start
    v8-modules-ready-passed

Interpretation:

- start=0:
  MTK post-fs-data action was not reached. Either an earlier post-fs-data
  action blocked or the event itself was not reached.

- start=1, modules-ready-passed=0:
  main init entered the MTK post-fs-data action and blocked specifically at
  vendor.all.modules.ready=1.

- both=1:
  vendor.all.modules.ready is not the immediate MTK post-fs-data blocker.

PHONE_MODIFIED=0
