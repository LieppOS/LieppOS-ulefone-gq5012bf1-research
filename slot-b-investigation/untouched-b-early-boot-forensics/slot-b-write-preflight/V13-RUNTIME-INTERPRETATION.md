# V13 runtime interpretation

V13 preserved the V12 system diagnostic and changed init.insmod.sh so that
only the system_dlkm module pass remained; the vendor module pass was skipped.

Observed fresh Slot-B markers:

    v10-after-keymaster=1
    v9-keymaster-passed=1
    v8-mtk-pfsd-start=1

Observed seed-only markers:

    v8-modules-ready-passed=0
    40-vendor-modules-ready=0

The exact system/vendor/root AVB state was unchanged after the trial.

Therefore skipping the entire vendor module pass was insufficient to make
vendor.all.modules.ready reach 1.

The remaining path before that property is:

    insmod_sh
      -> system_dlkm modprobe
      -> final setprop vendor.all.modules.ready 1

V13 does not by itself distinguish a system_dlkm modprobe stall from failure
before/during final property publication.

pstore was empty.
