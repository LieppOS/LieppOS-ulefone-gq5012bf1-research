# V9 final boundary

Fresh Slot-B V9 execution proved:

    v9-system-pfsd-start=1
    v9-checkpoint-passed=1
    v9-installkey-passed=1
    v9-keymaster-passed=0

Therefore:

- system `on post-fs-data` definitely begins;
- `vdc checkpoint prepareCheckpoint` returns;
- `installkey /data` returns;
- execution stops progressing somewhere after installkey and before the
  marker following `vdc keymaster earlyBootEnded`.

V9 does not prove the keymaster command itself is the blocker because several
commands exist between the installkey and keymaster markers.

V10 brackets that exact region.

PHONE_MODIFIED=0
