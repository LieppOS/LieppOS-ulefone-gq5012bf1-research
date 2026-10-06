# GQ5012BF1 stock kernel-module boot-phase map

Static sources: stock `init_boot` ramdisk (`/init`, sha256 `71158a84…`), `vendor_boot`
platform ramdisk fragment (`platform.cpio` sha256 `cef8c3a7…`), `vendor`, `vendor_dlkm`,
`system_dlkm`, `odm_dlkm`, `lk.img`; behaviour from AOSP android14 `system/core/init`,
`libmodprobe`, `toolbox/modprobe.cpp` (stock binaries carry the same source-path and log
strings). Runtime cross-checks: `slot-b-investigation/untouched-b-early-boot-forensics/mtk-watchdog-loader-chain-audit/live-loader-state.txt`
(bootprof + properties, stock slot A), `workspace/phase4-tkcore-island/phase3g/device-before/{proc-modules.txt,all-log-after-rollback.txt}`,
two recovery-mode `last_kmsg` captures.

Module count notation: *inserted* = new `finit_module` successes; repeats return EEXIST.

| # | phase | loader | input list | module root | dependency behaviour | failure policy | readiness signal |
|---|---|---|---|---|---|---|---|
| 1 | bootloader handoff | LK | — | — | — | — | normal boot: LK adds `androidboot.force_normal_boot=1`; META: `androidboot.init_rc=/system_ext/etc/init/hw/meta_init.system.rc`; kernel = GKI `Image` from `boot` (its ramdisk is empty) |
| 2 | first-stage init (`init_boot` `/init`, static, pid 1, before SELinux) | `LoadKernelModules()` → libmodprobe `LoadListedModules(strict=true)` sequential | `/lib/modules/modules.load` (184 lines, 183 unique; `mtk_dramc.ko` listed twice); recovery: `modules.load.recovery` (189/188) | `/lib/modules` (vendor_boot platform ramdisk; no `<uname -r>` subdir) | hard deps from `modules.dep` (reverse order) + `modules.softdep` pre/post (one malformed line ignored); 4 extra deps pulled in | strict: first failing entry stops the loop → `LOG(FATAL) "Failed to load kernel modules"` → init fatal reboot (no first-stage console configured) | `Loaded N kernel modules took X ms`; env → `ro.boottime.init.modules` (stock: 1389 ms) |
| 2a | — | — | — | — | normal: **187 inserted** (simulated); recovery: **192 inserted** (simulated **and** observed: `init: Loaded 192 kernel modules` in two recovery `last_kmsg`) | — | — |
| 3 | first_stage_mount | init fstab `/first_stage_ramdisk/fstab.mt6878` | — | — | mounts `system`, `system_ext`, `vendor`, `product`, `vendor_dlkm`, `system_dlkm`, `odm_dlkm` (all `wait,slotselect,avb,logical,first_stage_mount`), `/metadata` | missing/verity failure → first-stage failure | storage drivers (UFS/blocktag/rpmb, seq 115–124) must already be in step 2 |
| 4 | second-stage `early-init` | `init.mt6878.rc` then imported `init.project.rc`→`init.mtkgki.rc` | — | — | — | — | `vendor.all.modules.ready=1` (mt6878.rc) then `=0` (mtkgki.rc), bootprof `modprobe: Load_Module_START`, `start insmod_sh` |
| 5 | `insmod_sh` service (async, oneshot, root, domain `init_insmod_sh`) | `/vendor/bin/init.insmod.sh /vendor/etc/init.insmod.mt6878.cfg` | cfg line `modprobe|*` → for `system_dlkm` then `vendor`: `modprobe -a -d /<p>/lib/modules $(cat /<p>/lib/modules/modules.load)` | `/system_dlkm/lib/modules` (60), `/vendor/lib/modules` → symlink `/vendor_dlkm/lib/modules` (195) | each modprobe = new libmodprobe instance: hard deps + softdeps, EEXIST = already loaded | `-a` mode with list: per-module error logged, loop continues, exit code ignored by script | after both passes: cfg `setprop|vendor.all.modules.ready` → `setprop … 1` (retry ≤129) |
| 5a | — | — | — | — | system_dlkm pass **60 inserted**; vendor pass **≈191 inserted** (4 already in from step 2: `mtk_mbox`, `mtk_rpmsg_mbox`, `mtk_tinysys_ipi`, `yft_devinfo`; `bluetooth` already from system_dlkm) | — | stock run: insmod_sh started 3.745 s, last vendor initcall (`yft_tiny2c_usb`) 6.117 s |
| 6 | `init` | `init.touch.rc`: `exec_background u:r:vendor_modprobe:s0 -- /vendor/bin/modprobe -a -d /vendor/lib/modules <19 names>` | 19 touch drivers, only 3 exist (`tui-common`, `focaltech_touch_spi_ft3680`, `hynitron`) | `/vendor/lib/modules` | runs **in parallel** with step 5's vendor pass (bootprof: pid 495 loads `focaltech_touch_spi_ft3680` @4.279 s and `hynitron` @4.641 s while insmod_sh pid 493 loads `apusys`) | 16 missing names → logged, ignored; init does not wait | none |
| 7 | `post-fs-data` | `init.mt6878.rc:178` | — | — | — | `wait_for_prop vendor.all.modules.ready 1` — **no timeout** | bootprof `modprobe: Load_Module_DONE` (stock: 11.245 s; wait returned "already set") |
| 8 | vendor init / property triggers | init builtin `insmod` (domain `init`/`vendor_init`) | `init.gps_pwr.rc`, `init.gps_scp.rc` on `vendor.connsys.driver.ready=yes` (set by `conninfra_loader`); `init.bt_drv.rc` same trigger | `/vendor/lib/modules` | none (raw `finit_module`) | failure logged by init, ignored | — |
| 8a | — | — | `bt_drv_${ro.vendor.bt.platform}.ko` = `bt_drv_6878.ko` | — | — | **always EEXIST** (already in vendor `modules.load`): captured `finit_module … failed: File exists` | — |
| 9 | `boot` | init builtin `insmod` | `msync2_dms.ko` (absent → ENOENT), `msync2_frd.ko` | `/vendor/lib/modules` | none | logged, ignored | — |
| 10 | runtime / on demand | `insmod_pstore_blk` service (`persist.vendor.pstore.model=1`) | `/vendor/lib/modules/pstore_zone.ko`, `pstore_blk.ko best_effort=1` | — | — | both files absent on GQ5012BF1 → dead path | — |
| — | kernel autoload | none | `init.rc` writes empty `/proc/sys/kernel/modprobe`; ueventd has no `modalias_handling enabled` | — | `modules.alias` only matters for explicit names | — | — |

Totals (simulated with `scripts/modprobe_sim.py`, normal boot): 187 + 60 + 191 + 2
(touch) + 3 (gps_pwr, gps_scp, msync2_frd) = **443 modules**, equal to the 443 stock
entries in the captured `/proc/modules` (444 lines incl. the user-added `kernelsu`). Every
expected module is present and nothing stock is loaded outside these paths.

## Ordering facts that matter

- Imports are parsed after the importing file ends, so at `early-init` the order is
  `init.mt6878.rc` (`ready=1`) → `init.mtkgki.rc` (`ready=0`, `start insmod_sh`). Directory
  scripts in `/vendor/etc/init/` (e.g. `init.touch.rc`) are parsed after the whole
  `init.rc` import tree.
- `insmod_sh` is started, not exec'd: init continues with `init`, `late-fs`, mount_all
  while modules load. Only `post-fs-data` blocks on the property.
- File order ≠ insertion order: 140 first-stage and 266 vendor `modules.dep` edges point
  "forward" in their `modules.load` (dependency listed after its user), so those
  dependencies are inserted early, out of file order (e.g. UFS/rpmb are pulled in by
  `mtk_mmc`, `mediatek-drm` by the `mtk_afe_external` post-softdep).
  Authoritative resolved order: `resolved-load-order.tsv`.
