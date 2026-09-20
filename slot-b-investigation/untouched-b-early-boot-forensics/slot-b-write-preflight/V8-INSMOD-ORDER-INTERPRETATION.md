# V8 MTK GKI module-ready ordering

Android init defers imports until the importing file reaches EndFile().

Therefore init.mt6878.rc registers its early-init action before its imported
init.project.rc -> init.mtkgki.rc actions.

Effective early-init order:

    init.mt6878.rc:
        setprop vendor.all.modules.ready 1

    init.mtkgki.rc:
        setprop vendor.all.modules.ready 0
        start insmod_sh

The oneshot insmod_sh then processes:

    modprobe|*
    setprop|vendor.all.modules.ready

init.insmod.sh expands modprobe|* into module loading from system_dlkm and
vendor. Only after those modprobe commands return does the script execute:

    setprop vendor.all.modules.ready 1

Thus a non-returning modprobe operation can leave the property at 0 and make
the MT6878 post-fs-data wait block indefinitely.

Working Slot A control:

    vendor.all.modules.ready=1
    init.svc.insmod_sh=stopped

Its init.project.rc, init.mtkgki.rc, init.insmod.sh and repaired
init.insmod.mt6878.cfg match the current build.

The earlier empty property observation was from a context denied access to
vendor.all.modules.ready; the root control reads 1.

V8 directly brackets the MT6878 post-fs-data wait and can now distinguish this
hypothesis at runtime.

PHONE_MODIFIED=0
