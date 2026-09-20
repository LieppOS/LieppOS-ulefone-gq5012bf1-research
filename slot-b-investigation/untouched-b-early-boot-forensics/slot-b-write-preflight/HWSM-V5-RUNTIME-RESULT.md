# hwservicemanager V5 runtime result

Slot B was boot-tested with the V5 main-init `wait_for_prop` instrumentation.

V5 probes:

- `init.svc.servicemanager=running`
- `init.svc.hwservicemanager=running`

Persistent markers surround both waits so the exact blocking boundary can be
determined after returning to Slot A.

The raw runtime evidence is stored in `hwsm-v5-runtime-result.txt`.

PHONE_MODIFIED=0
