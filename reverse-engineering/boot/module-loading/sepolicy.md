# SELinux boundary (module loading only)

| subject | how it gets there | key permissions (stock `vendor_sepolicy.cil` / `plat_sepolicy.cil`) |
|---|---|---|
| first-stage init | kernel context, before policy load | n/a (`allow init rootfs:system module_load` kept for later) |
| `init` (`init_34_0`) | — | `capability sys_module`; `module_load` on `vendor_file`, `rootfs`, `system_file` (rc `insmod` builtins: gps_pwr, gps_scp, bt_drv, msync2_*) |
| `vendor_init` | rc commands from /vendor | `capability sys_module`; `module_load` on `vendor_file`; may set `vendor_mtk_device_prop` |
| `init_insmod_sh` (MTK) | `typetransition init init_insmod_sh_exec:process init_insmod_sh`; file context `/vendor/bin/init\.insmod\.sh u:object_r:init_insmod_sh_exec:s0` | `capability sys_module`; `system module_load` on `vendor_file` **and** `system_dlkm_file`; read `proc_modules`; exec `vendor_toolbox_exec` (modprobe/setprop) without transition; `set` `vendor_mtk_device_prop`; `key search` |
| `vendor_modprobe` (AOSP) | `exec_background u:r:vendor_modprobe:s0` from `init.touch.rc` | `module_load` on `vendor_file` (capability via AOSP base policy) |
| `ueventd` | — | `module_load` on `vendor_file` (AOSP); unused because ueventd `modalias_handling` is not enabled |
| `modprobe` (AOSP, system) | not used by stock rc | `module_load` on `system_dlkm_file` |
| `init_pstore_blk_sh` (MTK) | `init.pstore_blk.sh` | `module_load` on `vendor_file` (dead path) |
| `hal_wifi_default`, `mtk_hal_wifi` | — | `module_load` on `vendor_file` (no stock caller found) |

File labels: `/vendor_dlkm(/.*)?`, `/odm_dlkm(/.*)?` → `vendor_file` (`…/etc` →
`vendor_configs_file`); `/system_dlkm(/.*)?` → `system_dlkm_file`; vendor_boot `/lib/modules`
→ `rootfs`.

Property: `vendor.all.modules.ready u:object_r:vendor_mtk_device_prop:s0` (exact);
setters `init_insmod_sh`, `vendor_init`; readable by init (the only reader).

Stock runtime AVCs in `init_insmod_sh` (benign, captured): `proc_cmdline` read (libmodprobe
cmdline options), `key write`, `sys_nice`, `setsched` on kernel threads.
