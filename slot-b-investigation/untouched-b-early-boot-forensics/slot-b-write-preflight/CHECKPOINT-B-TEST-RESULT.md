# Instrumented Slot-B boot result

The checkpoint-instrumented Slot B was activated successfully but did not
reach a usable Android environment. The user manually recovered the device to
Slot A through bootloader fastboot.

Persistent `/metadata/lieppos-slotb` markers were collected after returning to
safe Slot A. Marker value `1` means that init milestone was reached during the
B boot; `0` means the pre-seeded marker was not overwritten.

See `checkpoint-b-test-result.txt` for the raw checkpoint matrix and boot
control state.
