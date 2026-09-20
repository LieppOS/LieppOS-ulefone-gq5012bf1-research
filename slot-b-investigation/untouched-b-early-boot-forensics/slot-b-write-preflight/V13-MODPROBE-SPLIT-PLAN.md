# V13 module-loader binary split

## Proven starting point

V12 cleared the former synchronous keymaster boundary:

    v10-before-keymaster=1
    v10-after-keymaster=1
    v9-keymaster-passed=1

and reached:

    v8-mtk-pfsd-start=1

but did not reach:

    v8-modules-ready-passed=1

Therefore the observed boundary moved to:

    wait_for_prop vendor.all.modules.ready 1

The exact A/B provenance audit proved these files are byte-identical:

- /vendor/bin/init.insmod.sh
- /vendor/etc/init.insmod.mt6878.cfg
- /vendor/etc/init/hw/init.mtkgki.rc

The normal script performs, in order:

    modprobe -a -d /system_dlkm/lib/modules ...
    modprobe -a -d /vendor/lib/modules ...
    setprop vendor.all.modules.ready 1

V13 changes only that partition loop:

    system_dlkm vendor

becomes:

    system_dlkm

Thus V13 deliberately skips only the vendor-module modprobe pass for one
diagnostic Slot-B boot.

Interpretation:

- v8-modules-ready-passed remains 0:
  system_dlkm modprobe, or execution before final setprop, is still blocking.

- v8-modules-ready-passed becomes 1:
  system_dlkm returned and the normal final setprop executed; the previously
  observed blocker is therefore in the skipped vendor modprobe path.

This is diagnostic-only. Vendor modules are not permanently to be omitted.

V12 system remains unchanged.

PHONE_MODIFIED=0
