# hwservicemanager V5 result interpretation

V5 boot-test result:

    v5-sm-before=1
    v5-sm-running=1
    v5-hwsm-before=1
    v5-hwsm-running=1
    v5-complete=1

All markers have the fresh Slot-B boot timestamp.

Because `wait_for_prop` executes its builtin in main init, this establishes
that during post-fs main init observed:

    init.svc.servicemanager=running
    init.svc.hwservicemanager=running

Therefore the Slot-B failure is not explained by hwservicemanager simply never
being started.

This does not yet prove hwservicemanager remains running at late-fs. It could
start and subsequently exit/restart before the MT6878 late-fs wait for
`hwservicemanager.ready=true`.

Pstore remained empty.

Next step: V6 repeats the service-state checks from main init at late-fs and
then directly waits for `hwservicemanager.ready=true`.

PHONE_MODIFIED=0
