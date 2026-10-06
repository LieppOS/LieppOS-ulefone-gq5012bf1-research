# LieppOS porting contract — stock-compatible module loading

## Must preserve

1. **Module paths**: `/lib/modules` in the vendor_boot ramdisk (flat, no `<uname -r>` dir);
   `/vendor_dlkm/lib/modules`, `/system_dlkm/lib/modules`; `/vendor/lib/modules` →
   `/vendor_dlkm/lib/modules` symlink (rc files and the cfg use `/vendor/lib/modules`).
2. **Metadata**: `modules.load`, `modules.load.recovery`, `modules.dep`, `modules.softdep`,
   `modules.alias` in `/lib/modules`; `modules.load`, `modules.dep` (+ softdep/alias) in both
   DLKM dirs. `modules.dep` must list every loadable module with absolute paths.
3. **First stage**: every name in `modules.load` must load (strict → FATAL otherwise). Storage
   (`ufs-mediatek-mod`, `ufs-mediatek-dbg`, `phy-mtk-ufs`, `blocktag`, `rpmb`, `rpmb-mtk`,
   `cqhci`, `mtk_mmc`), clocks/PMIC/pinctrl/regulators, SMI/IOMMU, display, UART, PMIC keys,
   charger/FG and TEE (`tkcore`) are first-stage.
4. **fstab**: `vendor_dlkm`, `system_dlkm`, `odm_dlkm` with `first_stage_mount,slotselect,avb,logical`
   so the second-stage loader can see them at early-init.
5. **Loader**: `insmod_sh` service (`/vendor/bin/init.insmod.sh`, label
   `u:object_r:init_insmod_sh_exec:s0`, domain `init_insmod_sh`), cfg
   `/vendor/etc/init.insmod.mt6878.cfg` (= `ro.hardware`), started from `init.mtkgki.rc`
   at early-init; `/vendor/bin/modprobe` (toolbox).
6. **Readiness**: the 1→0→1 `vendor.all.modules.ready` protocol and the post-fs-data
   `wait_for_prop`; property context `vendor_mtk_device_prop`; `set_prop(init_insmod_sh, …)`.
7. `init.touch.rc` (or an equivalent) for `focaltech_touch_spi_ft3680`, `hynitron`,
   `tui-common` — touch is not in any `modules.load` except via the rear-display dep.
8. connsys rc `insmod` for `gps_pwr`, `gps_scp` on `vendor.connsys.driver.ready=yes`;
   `msync2_frd` on boot (if MSYNC is wanted).
9. **Recovery**: `modules.load.recovery` with the 13 recovery-only modules; touch must be
   added for a touch UI recovery.
10. **Slots**: kernel, init_boot, vendor_boot, vendor_dlkm, system_dlkm, vendor from the
    same slot and the same build; AVB descriptors consistent with modified images.

## Can safely simplify

- Drop the 16 absent touch names from `init.touch.rc`; drop `bt_drv` rc insmod (EEXIST),
  `msync2_dms` (ENOENT), `insmod_pstore_blk` (modules absent).
- Do not ship `met*`, `cmdq-test`, `emi-fake-eng`, `scheduler_ext` (never loaded).
- Remove the duplicate `vendor_dlkm/bluetooth.ko` (system_dlkm GKI copy always wins) and,
  for normal boot only, the vendor_dlkm copies of the 13 recovery duplicates (first stage or
  the recovery list provides them) — keep `modules.load`/`modules.dep` consistent.
- Fix the duplicate `mtk_dramc.ko` line and the malformed softdep (cosmetic).
- Replace `init.insmod.sh` by any loader that runs both modprobe passes and then sets
  `vendor.all.modules.ready=1` — the property does not depend on filenames; or drop the
  `wait_for_prop` together with `init.mtkgki.rc` if the replacement is synchronous
  (exec) — but then post-fs-data consumers (camera `/dev/*AF`, YFT sysfs, CCCI) must still
  run after the modules exist.
- META/factory trees can be ignored for a user ROM.
