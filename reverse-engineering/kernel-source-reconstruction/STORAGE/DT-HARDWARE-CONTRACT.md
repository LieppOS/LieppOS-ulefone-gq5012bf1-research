# Storage hardware and device-tree contract

Detailed per-property maps already exist and are not duplicated:
`../../storage/hardware/topology.md`, `../../storage/ufs/dt-contract.md`,
`../../storage/ufs/power-state-machine.md`, `../../storage/microsd/dt-contract.md`,
`../../storage/rpmb/boundary.md`. This file classifies each relationship by its evidence and
adds what the source-certification work re-checked.

Operands:
* **S** static DT: stock merged base + overlay `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb`.
* **L** live DT: read-only capture `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`
  (decoded: `../../storage/hardware/live-dt-storage-nodes.txt`).
* **R** runtime capture of the same snapshot: process list (`services-processes.txt`),
  module-load capture (`reverse-engineering/boot/module-loading/module-classification.tsv`).
* **P** PL/LK log already in the research tree (`../../storage/hardware/topology.md` sources).
* **D** stock driver (the byte-exact source here). **REF** reference source only.

Classes: **ACTIVE AND PROVEN** · **ENABLED IN DEVICE TREE** · **PRESENT IN STOCK DRIVER** ·
**REFERENCE SOURCE ONLY** · **UNKNOWN**.

## Controllers

| block | node / driver | evidence | class |
|---|---|---|---|
| UFS host | `soc/ufshci@112b0000`, `mediatek,mt8183-ufshci`, no `status` (= okay) in S and L; `ufs-mediatek-mod` | R: kernel workqueues `ufs_mtk_eh_wq`, `ufs_mtk_rq_wq` (MTK vops init), `ufs_eh_wq_0`, `ufs_clk_gating_` (ufshcd host 0 init) exist in the running system, which boots and runs from UFS (`ro.boot.boot_devices` = `bootdevice, soc/112b0000.ufshci`) | **ACTIVE AND PROVEN** |
| UFS M-PHY | `soc/ufsphy@112a0000`, `mediatek,mt8183-ufsphy`, `mphy-ver=1`; `phy-mtk-ufs` | S/L: referenced by `phys = <&ufsphy>`; R: module loaded; host probe succeeded, and the driver returns `-EPROBE_DEFER` while a referenced PHY is unbound | **ACTIVE AND PROVEN** (by host probe) |
| UFS device | Micron `MT512GBCAV8U31`, UFS 3.1 (`wSpecVersion 0x0310`), 3 LUs + RPMB W-LU | P (JEDEC descriptors) | **ACTIVE AND PROVEN** |
| MSDC1 / microSD | `soc/mmc@11240000`, `host-index 1`, okay in S and L; `mtk-mmc` | R: IRQ threads `irq/360-11240000.mmc` and `irq/59-11240000.mmc cd` | **ACTIVE AND PROVEN** (host probed, CD IRQ registered; card presence not captured) |
| MSDC0 / eMMC | `soc/mmc@11230000`, `host-index 0`, `supports-cqe`, HS400 | **S: `status = "okay"`; L: `status = "disabled"`** — the bootloader disables it at boot on this UFS board | **ENABLED IN STATIC DT, DISABLED AT RUNTIME** |
| CQHCI | `cqhci` | only MSDC0 has `supports-cqe`; MSDC0 disabled in L | loaded (R), **PRESENT IN STOCK DRIVER**, not used |
| write-protect | `mtk-wp` | no `wp-gpios` on MSDC1; module parameters `wp_boot1/2`, `wp_user` unset in `modules.load`/bootconfig evidence | loaded (R); policy **UNKNOWN** at runtime (no sysfs capture) |
| blocktag | `blocktag` | R: loaded; consumers ufs-mediatek-mod, mtk-mmc, cqhci | **ACTIVE AND PROVEN** (as a loaded dependency); tracer output not captured |
| RPMB (UFS W-LU 0xC4) | `rpmb` core + `ufs-mediatek-rpmb.o` provider + `rpmb-mtk` `/dev/rpmb0` | R: `teed` (opens `--rpmbdev /dev/rpmb0`) and `mtk_storageproxyd -r /dev/0:0:0:49476` running; tkcore log reports RPMB size 16 MiB | **ACTIVE AND PROVEN** (transport in use; contents never accessed) |
| eMMC RPMB path | `mmc_rpmb_register` (rpmb-mtk), `emmc_rpmb_*` | MSDC0 disabled | **PRESENT IN STOCK DRIVER**, unused |
| iSE RPMB path | `ufs-mediatek-ise.c` (`ufs_mtk_ise_rpmb_probe`) | not linked into the shipped module (ise-dummy); built only as the build-only companion | **REFERENCE SOURCE ONLY** for this board |
| UFS feature (`ufsfeature`, `ufshid`, HPB, TW) | `drivers/ufs/vendor/ufs*.c` | not linked into the shipped module | **REFERENCE SOURCE ONLY** |

## UFS host resources (S = L)

| resource | specifier | provider node → module | class |
|---|---|---|---|
| 3 topckgen clocks (`ufs_sel`, `ufs_fde`, `ufs_mbist`) | `<&topckgen 41/40/42>` | `syscon@10000000` → `clk-mt6878` (BOOT-CLOCK-CORE, A) | ENABLED IN DT; probe success implies acquired |
| 6 UFSCFG_AO gates | `<&ufscfg_ao 0..5>` | `syscon@112b8000` → `clk-mt6878-peri` (A) | ENABLED IN DT |
| 4 UFSCFG_PDN gates | `<&ufscfg_pdn 0..3>` | `syscon@112bb000` → `clk-mt6878-peri` (A) | ENABLED IN DT |
| resets `unipro_rst`, `crypto_rst`, `hci_rst` | `<0xb9 0/1/2>` | `reset-controller` child of `syscon@112bb000`, `ti,syscon-reset` → **`reset-ti-syscon.ko`** (class D, loaded at `modules.load` line 161, after UFS at 112) | ENABLED IN DT; **acquisition at probe UNKNOWN** (see below) |
| PHY | `phys = <&ufsphy>` | `phy-mtk-ufs` | ACTIVE AND PROVEN |
| `vcc-supply` | MT6363 `vemc` | `mt6363-regulator.ko` (D, line 38) | ENABLED IN DT |
| `vccq-supply` | MT6363 `vufs12` | `mt6363-regulator.ko` | ENABLED IN DT |
| IRQ | GIC SPI 393 | GIC (built-in) | ENABLED IN DT |
| DMA | no `iommus`; `/soc` `dma-ranges = <0 0 0 0 0x10 0>` (64 GiB 1:1) | DMA API, no IOMMU binding | ENABLED IN DT (no IOMMU) |
| power domain | none (`power-domains` absent); MTCMOS through SiP `UFS_MTK_SIP_MTCMOS_CTRL` (`mediatek,ufs-rtff-mtcmos`) | ATF | PRESENT IN STOCK DRIVER + ENABLED IN DT; SiP behaviour UNKNOWN (firmware) |
| crypto (inline, FBE) | SiP `UFS_MTK_SIP_CRYPTO_CTRL`, `UFSHCD_CAP_CRYPTO` | ATF + GKI blk-crypto | PRESENT IN STOCK DRIVER (`../../storage/crypto/`) |
| boot mode | `bootmode = <&chosen>` (`atag,boot`, `atag,ufs`) | LK | ENABLED IN DT; `atag,ufs` RPMB-key-state blob consumed only by the iSE variant |

**Reset acquisition.** `ufs_mtk_init_reset_control()` treats any `devm_reset_control_get()`
error (including `-EPROBE_DEFER`) as "no reset" and continues. The reset provider
`reset-ti-syscon.ko` is listed 49 lines after `ufs-mediatek-mod.ko`. Unless the UFS probe is
retried later, the stock host probably runs with NULL reset controls, so
`ufs_mtk_host_reset()` does not pulse them. This is a static inference from load order and
the exact source. No boot log exists to confirm it (runtime ring buffer begins at about 180 s): **UNKNOWN**.

## MSDC1 resources (S = L, except CD polarity vs the donor, see microsd/dt-contract.md)

| resource | specifier | provider → module | class |
|---|---|---|---|
| clocks `source`, `bus_clk` | `<&topckgen 27/28>` | clk-mt6878 (A) | ENABLED IN DT |
| clocks `source_cg`, `macro`, `hclk`, `pclk_cg`, `axi_cg` | `<&pericfg_ao 24/20/25/27/26>` | clk-mt6878-peri (A) | ENABLED IN DT |
| `vmmc` / `vqmmc` | MT6369 `vmch-eint-low` / `vmc` | `mt6369-regulator.ko` (G, line 39) | ENABLED IN DT |
| pins GPIO77–82, `cd-gpios = <&pio 14 0>` | `pinctrl-mt6878.ko` (D, line 21) | ENABLED IN DT; CD IRQ ACTIVE AND PROVEN |
| GPIO register dump on error | `gpio_dump_regs_range` | `pinctrl-mtk-common-v2_debug.ko` (D) | PRESENT IN STOCK DRIVER |
| IRQ | GIC SPI 388 | | ACTIVE AND PROVEN |

## Power management, errors, thermal

| behaviour | class | where |
|---|---|---|
| UFS runtime PM autosuspend 500 ms, clock gating, auto-hibern8 2 ms (Micron) | PRESENT IN STOCK DRIVER (+ device id from P) | `../../storage/ufs/power-state-machine.md` |
| UFS suspend: VCC LPM via SiP, VCCQ LPM bypassed (`bypass-vccqx-lpm`) | PRESENT IN STOCK DRIVER + ENABLED IN DT | same |
| UFS error handling: `ufs_mtk_eh_*` (ufs-mediatek-dbg), AEE warnings, mrdump extra dump, IRQ dump (`mt_irq_dump_status`) | PRESENT IN STOCK DRIVER | exact `ufs-mediatek-dbg` |
| UFS thermal/health: device temperature notification, `bPreEOLInfo` | device features from P; `../../storage/ufs/health-thermal.md` | PRESENT IN STOCK DRIVER; runtime UNKNOWN |
| negotiated UFS gear/lanes | not captured | UNKNOWN |
| MSDC suspend/resume, UHS voltage switch (`state_uhs`) | PRESENT IN STOCK DRIVER + ENABLED IN DT | |
| MSDC autok tuning (`CONFIG_MMC_AUTOK`) | separate module/owner | not in scope |
