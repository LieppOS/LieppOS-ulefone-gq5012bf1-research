# GQ5012BF1 kernel-module loading (stock)

**Answer.** Stock loads kernel modules in four mechanisms:

1. **First-stage init** (AOSP, `init_boot` `/init`) loads `vendor_boot`'s `/lib/modules`
   `modules.load` (normal, 187 insertions) or `modules.load.recovery` (192) strictly and
   sequentially, then mounts `vendor_dlkm`/`system_dlkm`/`odm_dlkm` (first_stage_mount).
2. **MTK `insmod_sh`** (`init.mtkgki.rc`, early-init, async) runs `/vendor/bin/init.insmod.sh`
   with `init.insmod.mt6878.cfg`: AOSP `modprobe -a` over `/system_dlkm/lib/modules/modules.load`
   (60) then `/vendor/lib/modules/modules.load` (195 → 191 new), then
   `setprop vendor.all.modules.ready 1`.
3. **`init.touch.rc`** (`on init`, `exec_background` in `vendor_modprobe`): touch drivers
   (3 of 19 names exist), in parallel with step 2.
4. **rc `insmod`**: `gps_pwr`/`gps_scp` (and EEXIST `bt_drv_6878`) after
   `vendor.connsys.driver.ready=yes`; `msync2_frd` on boot.

`vendor.all.modules.ready` goes 1 (`init.mt6878.rc`) → 0 (`init.mtkgki.rc`) → 1 (insmod_sh
after both modprobe passes); `init.mt6878.rc` `post-fs-data` waits for it with no timeout.
Total 443 modules = captured stock `/proc/modules`. ueventd/kernel autoload is off. No
kernel module implements loading.

| file | content |
|---|---|
| `module-metadata.tsv` | every metadata file per partition: entries, sha256, semantics, consumer, phase |
| `boot-phase-map.md` | phase-by-phase loader/list/root/deps/failure/readiness |
| `resolved-load-order.tsv` | authoritative dependency-resolved insertion order (443) |
| `load-order-summary.md` | subsystem view and landmarks |
| `module-classification.tsv` | every shipped module: listed / dependency-only / rc / never loaded; capture check |
| `init-insmod-map.tsv` | every init-driven insertion path |
| `vendor-all-modules-ready.md` | setter/reader/timing/coverage |
| `readiness-dependency-graph.md` | barrier and gated consumers |
| `failure-semantics.md` | missing/CRC/vermagic/dup/init-error/hang behaviour |
| `recovery-module-loading.md` | recovery/fastbootd differences, OrangeFox implications |
| `slot-ab-behavior.md` | A/B ownership, KMI, AVB/dm-verity boundary |
| `sepolicy.md` | domains, labels, property permissions |
| `source-lineage.md`, `yft-module-loading-deltas.md` | AOSP vs MTK vs YFT |
| `lieppos-porting-contract.md`, `custom-kernel-implications.md` | porting guidance |
| `stale-claims.md` | corrections to the three workspace components |
| `scripts/` | `modprobe_sim.py`, `module_metadata.py`, `classify_modules.py`, `subsystem_summary.py` |
| `parity/` | why no `.ko` parity applies; behavioural parity |

Key stock hashes (sha256 prefix, bytes): `init.insmod.sh` 8685a096 1244; `init.insmod.mt6878.cfg`
683d5f45 345; `init.mtkgki.rc` 0c676a47 293; `init.project.rc` 19c1725e 2149; `init.mt6878.rc`
12b5aed8 37909; `init.touch.rc` 1ebb0d51 417; `init.bt_drv.rc` cff00682 397; `init.gps_pwr.rc`
e4efb746 100; `init.gps_scp.rc` be0ea191 100; `init.pstore.rc` cb742499 246; `toolbox`
(modprobe) 7003448e 130968; `toybox_vendor` (insmod) 7e1c324a 527952; init_boot `/init`
71158a84; `vendor_boot` platform fragment cef8c3a7, recovery fragment fbfa50e3.

Reproduce: `python3 scripts/modprobe_sim.py <stock>/partitions <platform-ramdisk>/lib/modules resolved-load-order.tsv`
(platform ramdisk = `cpio -id < workspace/gq5012bf1/stock/vendor-ramdisks/platform.cpio`).
