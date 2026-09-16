# Slot-B USB PID 0x201C interpretation

Factory MT6878 USB init configuration exposes PID `0x201C` through two paths:

1. ordinary ADB-only configuration; and
2. charger/KPOC ADB configuration.

The ordinary ADB path sets `vendor.usb.pid=0x201C` when
`sys.usb.config=adb` and `vendor.usb.acm_cnt=0`, then binds the gadget only
after `sys.usb.ffs.ready=1`.

The KPOC ADB path also uses `0x201C`, but requires:

- `ro.bootmode=charger`
- `ro.debuggable=1`
- `ro.vendor.usb.kpoc_adb=1`

When KPOC ADB is disabled, the charger path instead selects `kpoc_midi`,
whose product ID is `0x2046`.

Current Slot-B vendor content is the exact factory V15 vendor payload, whose
known property value is `ro.vendor.usb.kpoc_adb=0`. Subject to confirming that
there is no duplicate property authority elsewhere, the August `0e8d:201c`
events therefore strongly favor ordinary ADB-only configuration rather than
charger/KPOC ADB.

In either 0x201C path, FunctionFS ADB readiness was reached before gadget
binding. The observed failure boundary is therefore downstream of basic kernel
entry and Android init USB setup.
