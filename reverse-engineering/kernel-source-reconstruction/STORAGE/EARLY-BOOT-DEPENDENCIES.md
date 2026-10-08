# First-stage boot dependencies

Operands: stock `vendor_boot` platform ramdisk `lib/modules/{modules.load (184),
modules.load.recovery (189), modules.dep}`, the module-load capture
(`reverse-engineering/boot/module-loading/module-classification.tsv`) and the audit
dependency graph.

## Are all ten in the first-stage loader?

**Yes, all ten are listed literally** in both `modules.load` and `modules.load.recovery`, and the capture
records all ten as loaded.

| module | modules.load line | recovery line | resolved seq (deps first) | pulled in by |
|---|---:|---:|---:|---|
| blocktag | 114 | 112 | 115 | dep of cqhci |
| cqhci | 105 | 103 | 116 | modules.load |
| mtk-mmc-dbg | 106 | 104 | 117 | modules.load |
| ufs-mediatek-dbg | 113 | 111 | 118 | dep of mtk-mmc |
| rpmb | 110 | 108 | 119 | dep of mtk-mmc |
| ufs-mediatek-mod | 112 | 110 | 120 | dep of mtk-mmc |
| rpmb-mtk | 111 | 109 | 121 | dep of mtk-mmc |
| mtk-mmc | 107 | 105 | 122 | modules.load |
| mtk-wp | 108 | 106 | 123 | modules.load |
| phy-mtk-ufs | 109 | 107 | 124 | modules.load |

`modprobe` loads `modules.dep` dependencies first, so `mtk-mmc` (line 107) pulls in the whole
UFS/RPMB chain before itself. **`modules.dep` lists `rpmb-mtk.ko: ufs-mediatek-mod.ko …`**
(depmod resolves the export among *shipped* modules). The `.modinfo depends=` string
`ufs-mediatek-mod-ise` is not used by modprobe, so the absent `-ise` module is harmless.

## Providers that load earlier (by modules.load line)

| line | module | relation | certification |
|---:|---|---|---|
| 2 | mrdump | export to blocktag, mtk-mmc-dbg, ufs-mediatek-dbg | D |
| 3 | aee_aed | export to ufs-mediatek-dbg | D |
| 7 | irq-dbg | export to ufs-mediatek-dbg, ufs-mediatek-mod | D |
| 20–21 | pinctrl-mtk-v2, pinctrl-mt6878 | MSDC1 pins, CD GPIO | D |
| 22–31 | clk-common, clk-mt6878, clk-mt6878-peri, … | UFS/MSDC clocks (DT) | **A** (BOOT-CLOCK-CORE) |
| 38–39 | mt6363-regulator, mt6369-regulator | UFS VCC/VCCQ, MSDC1 VMMC/VQMMC (DT) | D / G |
| 100–101 | tkcore, tkcore_drv | TrustKernel driver; `teed` later uses `/dev/rpmb0` | (other owners) |
| 104 | pinctrl-mtk-common-v2_debug | export to mtk-mmc | D |

## Loaded after the storage modules

| line | module | effect |
|---:|---|---|
| 161 | reset-ti-syscon | provider of the three UFS resets; the UFS driver tolerates their absence (see `DT-HARDWARE-CONTRACT.md`) |

## What first-stage init needs

* `ro.boot.boot_devices = bootdevice, soc/112b0000.ufshci`. First-stage mount of
  `super`/`metadata`/`userdata` from UFS requires `ufs-mediatek-mod` (with `phy-mtk-ufs`,
  `ufs-mediatek-dbg`, `rpmb`, `blocktag` as hard symbol dependencies) and its clocks,
  regulators and PHY to probe. **Boot-critical by function: ufs-mediatek-mod, phy-mtk-ufs,
  and by symbol dependency: ufs-mediatek-dbg, rpmb, blocktag.**
* `rpmb-mtk` is not needed to mount storage. It is the `/dev/rpmb0` transport that TrustKernel `teed` opens
  (`--rpmbdev /dev/rpmb0`) for TA secure storage. Whether a TA that userdata unlock depends on
  (e.g. KeyMint) needs RPMB before first unlock is proprietary TEE behaviour: **UNKNOWN**.
  Treat `rpmb-mtk` as required for a normal boot until proven otherwise.
* `mtk-mmc`, `mtk-mmc-dbg`, `cqhci`, `mtk-wp` serve the removable microSD. They are not boot
  storage, but `mtk-mmc` is the `modules.load` entry that pulls in the UFS chain through
  `modules.dep`. Removing it from the list would change load order, not dependencies.
* Recovery uses the same relative order.

The load order was not changed.

## Runtime tests still required (separately authorized Slot B only; not performed)

1. Replace only these ten files in the Slot B `vendor_boot` ramdisk with the B1 outputs (same names and order),
   Slot A untouched and known-good, rollback rehearsed. Capture pstore/ramoops and bootprof.
2. Pass criteria: first-stage mount from UFS; same `/sys/class/ufs*`/`ufshcd` state as stock
   (gear, lanes, WB, auto-hibern8 2 ms, RPM 500 ms); no `ufs_mtk_eh` events; `/proc/ufs_debug`
   and `/proc/blocktag` present.
3. `teed` reaches ready state and opens `/dev/rpmb0` (observe only: **no RPMB write, no key
   programming, no counter read beyond what stock boot does itself**).
4. microSD insert/remove with the active-high CD; UHS-I switch; suspend/resume with and without a card.
5. Inline-crypto (FBE) unlock of userdata; reboot cycles.
6. Record whether `ufs_mtk_init_reset_control` acquires the resets (`dmesg` "Failed to get reset control").
7. Abort on any probe deferral loop, UFS error-handler activity or a missing `sdc` block device.
