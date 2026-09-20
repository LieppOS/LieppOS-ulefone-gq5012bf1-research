# V9 runtime interpretation

V9 instruments the main system init.rc post-fs-data action.

The first important pair is:

    v9-system-pfsd-start
    v9-checkpoint-passed

If start=1 and checkpoint-passed=0, main init entered system post-fs-data but
did not return from:

    /system/bin/vdc checkpoint prepareCheckpoint

If checkpoint-passed=1, the first subsequent fresh V9 marker that remains 0
narrows the blocker to the preceding command region.

Seed timestamps must not be interpreted as execution.

PHONE_MODIFIED=0
