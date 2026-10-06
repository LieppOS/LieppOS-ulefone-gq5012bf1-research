# MediaTek V4L2 lens framework (as shipped on GQ5012BF1)

## Components

| piece | kind | role |
|---|---|---|
| `main_vcm`, `main2_vcm`, `main4_vcm` (+ unused `main3_vcm`, `sub_vcm`) | generic MTK, I2C V4L2 subdev | one lens entity each (`MEDIA_ENT_F_LENS`), devnode `/dev/v4l-subdevN` |
| `camera_af_media` (`mtk-composite.c`, compatible `mediatek,mtk_composite_v4l2_2`) | generic MTK, platform driver | owns a `media_device` + `v4l2_device`, async-notifier over its DT ports, registers the subdev nodes when all bound |
| DT `mtk-composite-v4l2-2` | board config | port 0 → `camera-af-main@a`, 1 → `camera-af-main-two@b`, 2 → `camera-af-main-four@d`, 3 → `camera-ois-main@e` (DW9781C) |

The lens subdevs are **not** linked to sensor entities; the HAL pairs them by
name through `libcameracustom.lens.so` (see `../userspace/hal-lens-map.md`).

## Kernel interface (per lens subdev)

| operation | mechanism | behaviour |
|---|---|---|
| open | `v4l2_subdev_internal_ops.open` | `power_on` (dummy regulators, no pinctrl → no electrical effect) |
| configure / init | `VIDIOC_MTK_S_LENS_INFO` = `_IOWR('V', BASE_VIDIOC_PRIVATE + 3, struct mtk_vcm_info)`; `mtk_vcm_info = { VcmDriverConfig *p_vcm_info }` | `copy_from_user` 208 bytes → `g_vcmconfig`; sleep `ctrl_delay_us`; set `client->addr`; replay init table |
| move | `V4L2_CID_FOCUS_ABSOLUTE`, range 0..1023, step 1 | encode `pos` through `I2Cfmt[0..I2CSendNum-1]`, `i2c_master_send` each |
| release / power-down | `internal_ops.close` | park to `origin_focus_pos` in `move_steps`, replay `wr_rls_table`, `power_off` |
| motor info / AF status query | **none in kernel** | the HAL's `GetDriverCapability` / `GetFocusInformation` are answered from its own state |
| compat ioctl | none beyond the V4L2 core | `VcmDriverConfig` has no pointers, `mtk_vcm_info` holds one user pointer (64-bit HAL only) |

Unknown ioctls return `-ENOIOCTLCMD`. There is no read-back of position or status.

## Generic vs actuator-specific vs Ulefone-specific

| layer | generic MTK | actuator-specific | Ulefone/GQ5012BF1-specific |
|---|---|---|---|
| kernel drivers | all six modules (exact ALPS) | nothing | nothing in source |
| DT | node schema | — | three lens nodes on i2c-7/4/2, composite port wiring, no supplies |
| HAL lens table | `VcmDriverConfig` format, `GetVcmDriverName` | DW9800W init/move/release values | sensor_id → subdev mapping, init variant `07=79` |
| power | imgsensor `HW_ID_AFVDD` | — | `custom_afvdd` channels 5/6 on the YFT custom-LDO (WL2864C) path |
| packaging | MTK list builds 20 lens modules | — | only the 5 generic `*_vcm` + `camera_af_media` shipped |
