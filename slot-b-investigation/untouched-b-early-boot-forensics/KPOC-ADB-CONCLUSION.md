# KPOC ADB hypothesis conclusion

The searched factory MT6878 property authority contains one assignment:

`ro.vendor.usb.kpoc_adb=0`

Occurrences of `ro.vendor.usb.kpoc_adb=1` are init trigger conditions, not
property assignments.

Factory USB init logic selects `kpoc_midi` when charger mode is active and
`ro.vendor.usb.kpoc_adb=0`. The `kpoc_adb` path that exposes PID 0x201C
requires the property to equal 1.

Therefore the August Slot-B observations of USB PID `0e8d:201c` are classified
with high confidence as ordinary ADB/FunctionFS USB setup rather than KPOC ADB.

This moves the observed failure boundary downstream of second-stage Android
USB initialization.

Current Slot-A boot properties after recovery are:

- `ro.boot.bootreason=reboot`
- `sys.boot.reason=reboot,shell`
- `ro.bootmode=normal`

These describe the recovery boot into A and do not independently identify the
cause of the preceding Slot-B reset.

Bootstat event files on this device are zero-length; their metadata/timestamps,
not file contents, contain the useful event information.
