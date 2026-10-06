# Ulefone/YFT and MediaTek deltas vs AOSP module loading

| # | AOSP / MTK reference | GQ5012BF1 behaviour | evidence | delta | confidence |
|---|---|---|---|---|---|
| 1 | AOSP GKI: second-stage vendor modules usually loaded by a vendor `modprobe` exec in `on early-init` (e.g. Pixel `vendor_modprobe` service) | MTK `insmod_sh` service runs `init.insmod.sh` with `init.insmod.mt6878.cfg`; loads system_dlkm then vendor_dlkm | vendor rc/script/cfg | MTK orchestration | PROVEN |
| 2 | — | MTK readiness protocol: `ready=1` (mt6878.rc) → `0` (mtkgki.rc) → `1` (script) ; `wait_for_prop` at post-fs-data | rc files | MTK | PROVEN |
| 3 | AOSP: system_dlkm modules loaded by system-side `modprobe` domain | MTK vendor script loads system_dlkm too (policy grants `init_insmod_sh` `module_load` on `system_dlkm_file`) | sepolicy | MTK | PROVEN |
| 4 | MTK touch template | `init.touch.rc` modprobes 19 names; only `tui-common`, `focaltech_touch_spi_ft3680`, `hynitron` ship (YFT kept the template, dropped 16 drivers) | rc + vendor_dlkm | YFT build config | PROVEN |
| 5 | MTK | `hynitron` is both in the touch list and a hard dep of `spi_tiny_co5300_lcd` (rear display) → two loaders race; first wins, the other gets EEXIST | `modules.dep`, bootprof pid 495 | YFT | PROVEN |
| 6 | MTK | 13 modules duplicated in vendor_boot and vendor_dlkm (needed by recovery from ramdisk; loaded from vendor_dlkm in normal boot); `bluetooth.ko` shipped in system_dlkm (GKI, signed) **and** vendor_dlkm (vendor build, unsigned, same srcversion) — system_dlkm copy wins | hashes, modules.load | MTK/YFT packaging | PROVEN |
| 7 | MTK connectivity | `init.bt_drv.rc` still insmods `bt_drv_6878.ko` though it is in `modules.load` → always "File exists" | captured init log | dead legacy rc | PROVEN |
| 8 | MTK | `init.mt6878.rc` `on boot` insmods `msync2_dms.ko` (not shipped) and `msync2_frd.ko` (shipped, not listed) | rc + vendor_dlkm | ENOENT/extra | PROVEN |
| 9 | MTK | `init.pstore.rc` `insmod_pstore_blk` needs `pstore_zone.ko`/`pstore_blk.ko` — not shipped | rc + vendor_dlkm | dead | PROVEN |
| 10 | MTK `ko_order_table` | `mtk_dramc.ko` listed twice in first-stage `modules.load`; malformed softdep `pre:mtk_dcm.ko` | lists | harmless build artefact | PROVEN |
| 11 | MTK | 14 debug/eng modules shipped but never loaded: `met*` (12), `cmdq-test`, `emi-fake-eng`, `scheduler_ext` | classification | baggage | PROVEN |
| 12 | MTK | YFT project modules are inserted in vendor_boot first stage (charger/FG/keys/devinfo/panel/fingerprint TEE) and vendor_dlkm (camera, LDO, rear display, thermal USB) | lists | YFT | PROVEN |
| 13 | MTK META | LK carries `androidboot.init_rc=/system_ext/etc/init/hw/meta_init.system.rc`; META tree imports `init.mtkgki.rc` (same loader) and does **not** parse `/vendor/etc/init/*.rc` (no touch modprobe, no gps/bt rc insmod) | lk.img, rc | MTK | PROVEN (static) |
| 14 | MTK factory | `factory_init.rc` contains the same ready protocol but no selector string for it exists in `lk.img` | lk.img | unreached on this build | STRONGLY SUPPORTED |
