# hwservicemanager lifecycle V2 boot result

Slot B was booted with the V2 lifecycle-instrumented vendor image.

The device did not provide usable ADB and was manually recovered to Slot A
through bootloader fastboot.

Persistent `/metadata/lieppos-slotb` markers were collected after returning
to safe Slot A.

The V2 instrumentation records:

- servicemanager running;
- vndservicemanager running;
- hwservicemanager stopped/stopping/restarting/running states;
- the last observed `init.svc.hwservicemanager` value;
- `hwservicemanager.ready` false/last value;
- explicit `hwservicemanager.disabled=true`;
- the original early-boot milestone checkpoints.

See `hwsm-v2-test-result.txt` for raw values and timestamps.
