# V14 no-modprobe diagnostic

V14 tests whether the remaining Slot-B stall requires the system_dlkm
modprobe pass.

V13 already skips the vendor module pass.

V14 changes the cfg action, preserving line length:

    modprobe|*

to:

    skipload|*

`init.insmod.sh` has no `skipload` case, so that line performs no module
loading. The following existing cfg entry remains unchanged:

    setprop|vendor.all.modules.ready

Interpretation:

- fresh v8-modules-ready-passed=1:
  the system_dlkm modprobe path is required for the previous stall.

- v8-modules-ready-passed remains seed-only 0:
  neither system_dlkm nor vendor modprobe is required; investigate
  insmod_sh execution, cfg parsing, or final setprop.

This is diagnostic only.

The V12 system pair remains unchanged.
PHONE_MODIFIED=0
