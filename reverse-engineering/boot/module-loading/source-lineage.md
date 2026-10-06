# Source lineage of the stock module-loading chain

| layer | stock artifact | lineage | evidence |
|---|---|---|---|
| first-stage loader | `init_boot` `/init` (static, Android 34, sha256 `71158a84…`) | **AOSP** android14 `system/core/init/first_stage_init.cpp` `LoadKernelModules`/`GetModuleLoadList` + `libmodprobe` | strings `Failed to load kernel modules`, `Unable to open /lib/modules, skipping module loading.`, `modules.load.recovery`, `First stage mount skipped (recovery mode)`, `androidboot.force_normal_boot=1` built inline; matches `/mnt/SamsungSSD/android/lineage-22.2/system/core/init/first_stage_init.cpp`. This build has no `modules.load.charger` and no `load_modules_parallel` strings → sequential, normal/recovery only |
| modprobe | `/vendor/bin/modprobe` → `toolbox` (sha256 `7003448e…`) | **AOSP** `system/core/toolbox/modprobe.cpp` + `libmodprobe` (static) | strings `system/core/libmodprobe/libmodprobe.cpp`, `…_ext.cpp`, `-d, --dirname`, `use-blocklist`; NEEDED only libbase/libc++/libc/libm/libdl; no thread APIs |
| insmod | `/vendor/bin/insmod` → `toybox_vendor` | **AOSP** toybox | used by init.pstore_blk.sh and the cfg `insmod` action (unused on GQ5012BF1) |
| init `insmod`, `exec_background`, `wait_for_prop` builtins | `/system/bin/init` | **AOSP** | builtins.cpp |
| `init.insmod.sh` + `init.insmod.<hw>.cfg` | vendor | **MediaTek** ALPS (`mtkgki`) generic loader; cfg grammar `insmod|setprop|enable|modprobe` | header comment in script; same files on every MT68xx GKI vendor; `ro.vendor.mediatek.version.release=alps-mp-u0.mp1.rc-V10.29_esun.u0mp1rc.k6989v1.64_P8` |
| `init.mtkgki.rc` | vendor | **MediaTek** (`ready=0`, bootprof START, start insmod_sh) | — |
| `init.mt6878.rc` ready=1 + post-fs-data wait + bootprof DONE | vendor | **MediaTek** platform rc ("prevent NOT GKI project blocked") | — |
| SELinux `init_insmod_sh`, `vendor_mtk_device_prop` | vendor policy | **MediaTek** | `vendor_sepolicy.cil` |
| `vendor_modprobe` domain + `exec_background u:r:vendor_modprobe:s0` | policy: AOSP; rc: **MediaTek** touch template | AOSP `vendor_modprobe` domain; `init.touch.rc` lists 19 reference-board touch drivers |
| `modules.load` content/order | generated at build time | **MediaTek** build (`ko_order_table.csv`, see `init.connfem.rc` comment "Move insmod connfem.ko cmd to ko_order_table.csv") + **YFT** project additions | YFT modules in lists: `yft_devinfo`, `yft_gpio_keys`, `yft_tpd_gesture`, `yft_tiny2c_usb`, `sh366003_fg`, `sc851x/sc8571_charger`, `spi_tiny_co5300_lcd`, `custom_ldo_wl2868`, `panel-ky-vtdr6115…`, `microarray_fp_tee`, `aw883xx`, `aw3651x`… |
| `modules.dep/alias/softdep` | depmod at build | Kleaf/`kernel_device_modules` | absolute partition paths |

Searched: NothingOSS/`nt6878.git`, `nkm.git`, `volla6878.git`, `kdm.git` (public MTK
kernels: kleaf `mgk_64_k61.bzl` module lists only, no `init.insmod.sh`/`ko_order_table`),
local GKI workspace `kernel_device_modules-6.1`, Lineage tree, `kernel-research/`. No public
copy of the MTK ALPS `ko_order_table.csv` generator was found; the script/cfg/rc are taken
verbatim from the stock image (byte-identical copies already in `vendor_ulefone_gq5012bf1`
and the LieppOS device tree cfg).

No kernel module implements loading: there is no `mtk_module_loader.ko` (or similar) in any
of the 457 shipped modules or the GKI Image.
