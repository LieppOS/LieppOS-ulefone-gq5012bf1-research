# UFS health / thermal integration (static)

The live device was not queried. Existing captures were used.

## Health / lifetime

| interface | provider | notes |
|---|---|---|
| `/sys/bus/platform/devices/112b0000.ufshci/health_descriptor/{eol_info,life_time_estimation_a,life_time_estimation_b}` | **[UP]** GKI `ufs-sysfs.c` | standard JEDEC health descriptor |
| `ufs_mtk_ioctl` (SCSI-host ioctl, `ufs-mediatek-sysfs.c`) | **[MTK]** | user-space READ_DESC for device, configuration, interconnect, geometry, power and unit descriptors (**not** health), plus whitelisted attributes and flags |
| `/dev/ufs-bsg0` | **[UP]** `CONFIG_SCSI_UFS_BSG=y` | used by `libmtk_bsg.so` (boot-control `bBootLunEn` write) |
| PL/LK log | firmware | `pre_eol_info=1, life_time_est_a=1, life_time_est_b=1` = normal, 0–10 % used, **as of that capture only** |

## Temperature / thermal

| item | status |
|---|---|
| Device capability | ext-feature bits 4 and 5 (too-high / too-low temperature) are **set** (`0x800003BB`) |
| `CONFIG_SCSI_UFS_HWMON` | **not set** in GKI 12901745, so there is no hwmon temperature sensor and no thermal-zone binding |
| UFS exception-event temperature handling | upstream code only; no MTK hook |
| MTK thermal → UFS | none in `ufs-mediatek-mod` (no cooling device registered); live DT has no UFS thermal zone |
| Power throttling (low battery / battery OC) | **not wired** in the shipped object set (header include only) |

Result: storage temperature is **not exposed** and **not used for throttling** on stock GQ5012BF1. The device's own internal performance throttling (ext bit 9) is firmware-internal and is not visible to Linux.
