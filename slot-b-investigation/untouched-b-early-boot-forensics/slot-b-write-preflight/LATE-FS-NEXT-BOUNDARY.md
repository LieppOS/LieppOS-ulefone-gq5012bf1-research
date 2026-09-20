# Slot-B late-fs next boundary

V6 proved, from main init during late-fs:

    init.svc.servicemanager=running
    servicemanager.ready=true
    init.svc.hwservicemanager=running
    hwservicemanager.ready=true

The MediaTek MT6878 late-fs action is:

    wait_for_prop hwservicemanager.ready "true"
    ...
    mount_all --late
    ...

Therefore hwservicemanager readiness is no longer the leading blocker.

The next synchronous command in that MediaTek action is `mount_all --late`.

Before instrumenting V7, this audit records:

- the actual built fstab entries participating in late mounting;
- every installed `on late-fs` action;
- every `mount_all --late` call;
- Android init/fs_mgr semantics for late mounting.

`mount_all --late` is currently the leading candidate inside the MT6878
late-fs action, but it is not considered proven until the global late-fs
action set is checked.

PHONE_MODIFIED=0
