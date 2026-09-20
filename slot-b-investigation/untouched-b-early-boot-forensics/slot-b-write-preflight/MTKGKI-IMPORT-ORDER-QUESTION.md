# MTK GKI import/order question

The MT6878 insmod cfg is present and byte-identical to the repaired source.

`init.insmod.sh` processes `modprobe|*` before the final
`setprop|vendor.all.modules.ready`.

The script does not terminate merely because modprobe returns a nonzero
status. A failure to reach the final setprop therefore requires an earlier
script exit or a command that does not return.

Before interpreting the post-fs-data wait, the exact early-init action order
must be established. `init.mt6878.rc` imports `init.project.rc`, which imports
`init.mtkgki.rc`. Both mt6878 and mtkgki define early-init actions that write
the same readiness property.

The working Slot-A control also currently reports an empty
vendor.all.modules.ready value, so its actual init files and boot logs must be
compared with the built Slot-B vendor rather than assuming identical behavior.

PHONE_MODIFIED=0
