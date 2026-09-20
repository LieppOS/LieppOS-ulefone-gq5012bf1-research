# V10 keymaster boundary proven

Valid V10 Slot-B runtime:

    v9-system-pfsd-start=1
    v9-checkpoint-passed=1
    v9-installkey-passed=1

    v10-after-bootchart-start=1
    v10-after-entropy-copy=1
    v10-after-tombstoned-start=1
    v10-after-default-mount-ns=1
    v10-after-keystore-restorecon=1
    v10-after-boot-level=1
    v10-before-keymaster=1

    v10-after-keymaster=0
    v9-keymaster-passed=0
    v8-mtk-pfsd-start=0

The `1` markers have fresh Slot-B timestamps around 23:19:42.892.
The zero markers retain their pre-boot seed timestamps around 23:19:14-15.

Therefore main init entered:

    exec - system system -- /system/bin/vdc keymaster earlyBootEnded

and did not regain control from that synchronous exec during the observed
Slot-B boot.

This localizes the immediate boot blocker to execution of the vdc keymaster
earlyBootEnded command.

It does not yet distinguish among:
- vdc-side blocking;
- connection/waiting on vold;
- vold keymaster command handling;
- Binder/RPC calls issued by vold;
- KeyMint/Keystore/TEE backend behavior.

pstore was empty.

PHONE_MODIFIED=0
