# hwservicemanager V6 runtime result

Slot B was boot-tested with the V6 late-fs main-init probe.

V6 checks, in order:

    init.svc.servicemanager=running
    servicemanager.ready=true
    init.svc.hwservicemanager=running
    hwservicemanager.ready=true

Persistent markers identify the exact wait that completed or blocked.

The raw result is stored in `hwsm-v6-runtime-result.txt`.

PHONE_MODIFIED=0
