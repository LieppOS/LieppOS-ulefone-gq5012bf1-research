# UFS / block performance features (GQ5012BF1)

Classification uses only static evidence: exact module code, live DT, GKI 12901745 `.config` (Kleaf `kernel_aarch64_config`), stock fstab/props, and the PL/LK device-descriptor log.

| feature | status | evidence |
|---|---|---|
| Gear / lanes | **ENABLED (negotiated)**; value **UNKNOWN** | host offers HS-G5, Rate B, 2 lanes. A UFS 3.1 device (`wSpecVersion 0x0310`) supports ≤ G4. No PA attribute capture exists |
| Clock scaling (devfreq, gear scaling) | **DISABLED** | DT lacks `ufs_sel_max_src`/`ufs_sel_min_src`, so `UFSHCD_CAP_CLK_SCALING` is cleared. The `clkscale_control`/`upthreshold`/`downdifferential` sysfs and the min-gear-G4/200 ms/40/20 tuning are dormant |
| WriteBooster | **ENABLED** | `UFSHCD_CAP_WB_EN` [MTK]. Device ext features `0x800003BB` include bit 8. `bWriteBoosterBufferType` 0 (LU-dedicated), LU2 `dLUNumWriteBoosterBufferAllocUnits = 0x1E00`, preserve-user-space 1. Flush happens during hibern8 (`SKIP_MANUAL_WB_FLUSH_CTRL`), threshold 80 % remaining |
| HPB | **AVAILABLE BUT UNUSED** | device has HPB 2.0 and LU2 has `bLUEnable = 2` (HPB LU), but GKI `# CONFIG_SCSI_UFS_HPB is not set` and the vendor `ufsshpb.o` is not linked into stock `ufs-mediatek-mod` |
| MTK UFS feature pack (`ufsfeature`/TW/HID/ringbuf) | **NOT BUILT** | symbols absent from stock; object set proven by exact rebuild |
| BKOPS | **ENABLED (upstream default)** | GKI ufshcd auto-BKOPS on urgent exception events. MTK only exposes `bBKOPSStatus` / `fBackgroundOpsEn` query access through the SCSI-host ioctl `ufs_mtk_ioctl` (ufs-mediatek-sysfs.c) |
| Auto-hibern8 | **ENABLED, 2 ms** | no `ufs-disable-ah8`; Micron table entry |
| Clock gating | **ENABLED** | `UFSHCD_CAP_CLK_GATING` |
| Runtime PM | **ENABLED, 500 ms autosuspend** | `UFSHCD_CAP_RPM_AUTOSUSPEND`, `MTK_RPM_AUTOSUSPEND_DELAY_MS` |
| Command queueing | **ENABLED (SDB, 32 tags)** | `bQueueDepth 0x20`, legacy doorbell |
| MCQ | **DISABLED** | `mediatek,ufs-disable-mcq`; `ufshcd_core.poll_queues=0` |
| CPU latency QoS | **ENABLED** | `mediatek,ufs-qos`: `cpu_latency_qos` = 0 while clocks are on |
| IRQ affinity | **DEFAULT** | MTK affinity code (cpu0 IRQ moved to cpu3) is MCQ-only, so unused. The `smp_affinity` sysfs attribute exists (`ufs-mediatek-sysfs`) |
| Inline crypto | **ENABLED** | see [`../crypto/inline-crypto.md`](../crypto/inline-crypto.md) |
| Crypto DVFS boost | **DISABLED** | no `mediatek,ufs-boost-crypt` |
| I/O scheduler | GKI: mq-deadline, kyber, BFQ built in. The selected scheduler is set by userspace (`init.rc`), and the per-queue value was **not captured**, so it is UNKNOWN |
| Read/write boost hint (EARA-IO) | **AVAILABLE** | `blocktag` exports `/proc/blocktag/eara_io`, `eara_io_boost` and `earaio_ctrl` boost state to the MTK perf framework; the consumer is outside the kernel |
| Power throttling (low-battery/OC) | **NOT USED by UFS** | headers only; no registration in the shipped object set |
| zram swap | **ENABLED** | `fstab.enableswap` `zramsize=100%`, GKI `zram.ko`/`zsmalloc.ko` (system_dlkm) |
| f2fs compression | kernel **AVAILABLE**, data **DISABLED** | GKI `CONFIG_F2FS_FS_COMPRESSION=y`; `vold.has_compress = 0` |

Flash endurance and performance are **not** claimed: none of the above is a benchmark.
