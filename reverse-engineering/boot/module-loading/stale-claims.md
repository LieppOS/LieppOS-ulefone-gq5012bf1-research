# Corrections to earlier notes (MTK-MODULE-LOADER / INIT-INSMOD / VENDOR-ALL-MODULES-READY)

| # | earlier claim (location) | correction | evidence |
|---|---|---|---|
| 1 | MTK-MODULE-LOADER question: "whether an in-tree `mtk_module_loader.ko` exists" | **No such kernel module exists.** "MTK module loader" is the userspace chain `init.mtkgki.rc` → `insmod_sh` → `init.insmod.sh` + cfg → AOSP `modprobe`; first stage is pure AOSP | 457 shipped `.ko` + GKI Image searched |
| 2 | MTK-MODULE-LOADER README "Stock artifact: MTK modprobe" | `/vendor/bin/modprobe` is AOSP `toolbox` modprobe (libmodprobe), not MTK code | `toolbox` strings/NEEDED |
| 3 | INIT-INSMOD README question mentions `modules.load.rc` and `ueventd.rc` | neither participates: there is no `modules.load.rc`; ueventd modalias autoload is off and `kernel.modprobe` is emptied | init.rc:22, ueventd.rc |
| 4 | VENDOR-ALL-MODULES-READY `V8-MODULE-READY-STATIC-INTERPRETATION.md`: wait "is not a strong blocker candidate" because mt6878.rc sets 1 | superseded (already by `MTKGKI-INSMOD-READY-CHAIN.md`): `init.mtkgki.rc` resets it to 0 after mt6878.rc; only `insmod_sh` restores 1 | rc import order |
| 5 | implicit in V8/V13 notes: module load failure blocks the property | **No**: `init.insmod.sh` ignores modprobe exit status; only a missing cfg, an exec/label failure, a hung module init or a denied setprop keeps it at 0 | script text |
| 6 | V13 note: "The normal script performs … modprobe" (2 passes) as the whole loader | incomplete: `init.touch.rc` `vendor_modprobe` exec_background (parallel, not covered by the property), connsys/boot rc `insmod`s and pstore service are additional loaders | `init-insmod-map.tsv` |
| 7 | (any) "vendor modules load from vendor" | split is vendor_boot first stage 187 (normal) / 192 (recovery), system_dlkm 60, vendor_dlkm 191 new + 2 touch + 3 rc = 443 | `boot-phase-map.md`, `/proc/modules` capture |
| 8 | (any) generic AOSP assumption that system_dlkm is loaded by the system `modprobe` domain | on stock the MTK vendor script loads system_dlkm (domain `init_insmod_sh`) | sepolicy |
| 9 | VENDOR-ALL-MODULES-READY README "Still required: … replacement timing on hardware" | static timing proven from stock bootprof (START 3.749 s, last vendor initcall 6.117 s, DONE 11.245 s); hardware replacement testing is LieppOS validation, not RE scope | `live-loader-state.txt` |
