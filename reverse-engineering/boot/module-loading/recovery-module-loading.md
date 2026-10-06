# Recovery / fastbootd module loading

There is no recovery partition. Recovery is `vendor_boot` + `init_boot`:

- `vendor_boot` carries two ramdisk fragments: **platform** (`platform.cpio`, 65.9 MB:
  `/lib/modules` with all 196 `.ko` + metadata, `first_stage_ramdisk/fstab.mt6878`,
  `system/bin/recovery`, `fastbootd`, recovery `init.rc`) and **recovery**
  (`recovery.cpio`, 6.0 MB: `init.recovery.mt6878.rc`, `first_stage_ramdisk/fstab.emmc`,
  resources). Modules exist **only** in the platform fragment.
- Because `/system/bin/recovery` is present in the ramdisk, first-stage init is always in
  recovery mode unless LK passes `androidboot.force_normal_boot=1` (it does for normal boot;
  string in `lk.img`, value captured in a live bootconfig).

| | normal | recovery / fastbootd |
|---|---|---|
| list | `/lib/modules/modules.load` (184/183 unique) | `/lib/modules/modules.load.recovery` (189/188 unique) |
| inserted | 187 (simulated) | **192** (simulated and observed twice: `init: Loaded 192 kernel modules took 1446/1484 ms`, followed by `First stage mount skipped (recovery mode)`) |
| first_stage_mount | yes (vendor_dlkm, system_dlkm, …) | **skipped** → no vendor_dlkm/system_dlkm modules, no insmod_sh, no `vendor.all.modules.ready` |
| rc module loading | insmod_sh, init.touch.rc, rc insmod | none (`init.recovery.mt6878.rc`/`init.recovery.project.rc` have no insmod/modprobe) |

Recovery-only list entries (13; in normal boot these come from vendor_dlkm or as first-stage
dependencies): `mtk-mbox`, `mtk_rpmsg_mbox`, `mtk_tinysys_ipi`, `mtk-mmdvfs-v3-start`,
`mtk_battery_oc_throttling`, `mtk_dynamic_loading_throttling`, `mtk_low_battery_throttling`,
`mtk_mdpm`, `mtk_pbm`, `reboot-mode`, `syscon-reboot-mode`, `spmi-mtk-mpu`, `yft_devinfo`.
Reason: vendor_dlkm is not mounted in recovery, so reboot-mode (reboot reasons), the
power-throttling chain and the tinysys IPI stack must come from the ramdisk.

Normal-only list entries (8): `adsp`, `arm_dsu_pmu`, `mediatek-cpufreq-hw`,
`mtk-dvfsrc-devfreq` (still loaded in recovery as `mtk_dvfsrc` post-softdep),
`mtk-dvfsrc-helper`, `mtk-swpm-perf-arm-pmu`, `mtk_slbc`, `vcp_status`.

## Implications for OrangeFox / full recovery

- Display (`mediatek-drm`, panel `panel-ky-vtdr6115-dphy-cmd`), UFS, USB device/host
  (`mtu3`, `xhci-mtk-hcd-v2`, `phy-mtk-xsphy`, `extcon-mtk-usb`), Type-C/charger/fuel gauge,
  keys (`mtk-pmic-keys`, `yft_gpio_keys`) and TEE (`tkcore`) are in `modules.load.recovery`.
- **Touch is not**: `focaltech_touch_spi_ft3680` and `hynitron` live only in vendor_dlkm and
  are loaded by `init.touch.rc`. A touch-driven recovery must add them (and `tui-common`
  if needed) to the vendor_boot ramdisk and to `modules.load.recovery`, with deps from the
  vendor_dlkm `modules.dep`, or mount vendor_dlkm and modprobe them itself.
- The rear display (`spi_tiny_co5300_lcd`) is vendor_dlkm-only as well.
- Any recovery that replaces `vendor_boot` must keep `/lib/modules` + `modules.load.recovery`
  + `modules.dep`/`softdep`/`alias` consistent; a missing listed module is FATAL in first stage.
