# Module-loading readiness dependency graph

```
LK ──(androidboot.force_normal_boot=1, slot_suffix, GKI Image from boot_X)──► kernel
 │
 ▼
first-stage /init (init_boot_X)                      [no SELinux, pid 1, sequential, strict]
 ├─ /lib/modules (vendor_boot_X platform ramdisk): modules.load → 187 inserted
 │    clocks/PMIC/pinctrl → SMI/IOMMU → DRM/panel → UART → UFS/MMC/RPMB/blocktag
 │    → charger/fuel gauge → fingerprint TEE …            (failure ⇒ FATAL reboot)
 └─ first_stage_mount (fstab.mt6878, slotselect, AVB)
      system, system_ext, vendor, product, vendor_dlkm, system_dlkm, odm_dlkm, /metadata
 ▼
second-stage init (SELinux)
 early-init:  init.mt6878.rc  ready:=1
              init.mtkgki.rc  ready:=0 ; bootprof Load_Module_START ; start insmod_sh ──┐
 init:        init.touch.rc   exec_background vendor_modprobe (touch, 3 present) ──────┐ │
 late-init / fs / mount_all (/data)  … proceeds in parallel …                         │ │
                                                                                       │ │
 insmod_sh (init_insmod_sh) ◄──────────────────────────────────────────────────────────┼─┘
   modprobe -a -d /system_dlkm/lib/modules (60) → modprobe -a -d /vendor/lib/modules (195)
   setprop vendor.all.modules.ready 1 ──┐                                              │
                                        ▼                                              │
 post-fs-data: init.rc, init.usb.rc actions run first                                  │
              init.mt6878.rc:178  wait_for_prop ready 1  ◄══ BARRIER (no timeout)      │
              ↓ then, in parse order: init.cgroup, init_conninfra, connectivity.common,│
                mt6878.usb, init.project (camera /dev/*AF chmod), init.aee, sensor_2_0,│
                init.yft (thermal/USB sysfs chmods), fingerprint, modem, …            │
 zygote-start → early-boot → boot (class_start core/main/hal)                          │
   conninfra_loader (class core) ─► vendor.connsys.driver.ready=yes                   │
        ├─ insmod gps_pwr.ko, gps_scp.ko                                               │
        └─ insmod bt_drv_6878.ko (EEXIST)                                              │
   on boot: insmod msync2_dms (ENOENT), msync2_frd                                     │
 touch modprobe completes asynchronously ◄─────────────────────────────────────────────┘
```

## Consumers gated by the barrier

Strictly, the barrier delays **every action queued after `init.mt6878.rc:178`**, because
`wait_for_prop` pauses the whole action queue. The direct reasons for the wait:

| consumer | trigger | why it waits | kernel dependency |
|---|---|---|---|
| `init.project.rc` post-fs-data | post-fs-data | chmod/chown `/dev/MAINAF`, `/dev/MAINAF2`, `/dev/SUBAF`, … | vendor VCM modules (`main_vcm`, `main2_vcm`, `sub_vcm`) |
| `init.yft.rc` post-fs-data | post-fs-data | chmod of YFT sysfs (thermal camera, devinfo, fm78100 leftovers) | `yft_tiny2c_usb`, `extcon-mtk-usb`, `yft_devinfo` … |
| `init.cccimdinit.rc` | post-fs-data | `chown radio radio /sys/kernel/ccci/boot` | `ccci_md_all` (vendor_dlkm) |
| `init_conninfra.rc`, `init.connectivity.common.rc` | post-fs-data | connsys device nodes | `conninfra`, `connfem`, `wlan_drv_gen4m_6878` |
| `init.fingerprint.rc` | post-fs-data | `/dev/focaltech_fp` permissions | (fp driver; vendor) |
| `init.modem.rc` | post-fs-data (last import) | modem start, `vold.post_fs_data_done` | CCCI stack |
| class core/main/hal services (`conninfra_loader`, camerahalserver, audio HAL, mtkrild, sensors HAL …) | boot / zygote-start | open vendor driver nodes | the vendor_dlkm drivers |
| `gps_pwr`/`gps_scp`/`bt_drv` rc insmod | `vendor.connsys.driver.ready=yes` | need conninfra driver up | `conninfra.ko` (vendor modules.load) |

Not gated: everything before post-fs-data (`early-init`, `init`, `late-init`, `fs`,
`post-fs`, `mount_all`), the touch modprobe, and first-stage modules.
