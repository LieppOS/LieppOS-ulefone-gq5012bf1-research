# Camera HAL map (stock vendor, MTK mtkcam AIDL provider)

All file facts from `workspace/gq5012bf1/stock/partitions/vendor`; runtime
facts from the 2026-08-31 frozen capture. Machine-readable:
`../userspace/camera-services.tsv`, `camera-userspace-dependencies.tsv`
(774 ELFs), `camera-userspace-edges.tsv` (10 830 edges),
`camera-sensor-specific-files.tsv`, `tuning-db-inventory.tsv`.

## Services (PROVEN)

| interface | instance | impl | notes |
|---|---|---|---|
| android.hardware.camera.provider.ICameraProvider AIDL v2 | internal/0 | camerahalserver → `libmtkcam_hal_aidl_provider.so` | the live provider (HIDL 2.4-2.6 `-impl-mediatek` present but not served) |
| vendor.mediatek.hardware.camera.isphal.IISPModule AIDL v1 | internal/1 | `vendor.mediatek.hardware.camera.isphal_aidl@1.0-impl.so` | MTK ISP reprocess HAL |
| vendor.mediatek.hardware.camera.atms.IATMs | default | `…atms_aidl@1.0-impl.so` | |
| vendor.mediatek.hardware.camera.bgservice.IBGService | default | `…bgservice_aidl@1.0-impl.so` | background capture service |
| aovservice V2 | (linked) | `libmtkcam_hal_aov.so` | always-on-vision client lib |

`camerahalserver`: `/vendor/bin/hw/camerahalserver`, class main, user
cameraserver, groups audio camera input drmrpc sdcard_rw system media
graphics, `ioprio rt 4`, SELinux `u:r:mtk_hal_camera:s0`;
`/proc/ppb/ppb_camera_power` chmod 666 on post-fs-data.

## Camera IDs (PROVEN, dumpsys media.camera)

| Android ID | physical | DRVNAME | facing / orientation | flash | HFR configs |
|---|---|---|---|---|---|
| 0 | IMX989 | SENSOR_DRVNAME_IMX989_MIPI_RAW | BACK 90 | yes | 3840×2160 ≤120, 1920×1080 ≤240, 1280×720 ≤120 |
| 1 | S5KJN1 | SENSOR_DRVNAME_S5KJN1_MIPI_RAW | FRONT 270 | no (torch NOT_AVAILABLE) | none |
| 2 | S5KJN1 (main2) | SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW | BACK (wanted 270 / setup 90) | yes | none |
| 3 | OV64B | SENSOR_DRVNAME_OV64B_MIPI_RAW | BACK (wanted 270 / setup 90) | yes | none |

4 physical + 4 virtual devices, 1:1 (no logical multi-camera is exposed);
multi-open maximum 2. All four: `availableOpticalStabilization=[0]`,
AE fps ranges {10,15,20,24,5-30,30}. Camera 0 pixel array 4096×3072
(binned); cameras 1/2 8160×6144.

## Library layers (STRONG; from DT_NEEDED + embedded-string edges)

1. AIDL front: `libmtkcam_hal_aidl_{provider,device,common,utils}`.
2. Pipeline: `libmtkcam_pipeline*`, `libmtkcam_pipelinemodel_{session,
   capture,utils}`, `libmtkcam_pipelinepolicy*`, `libmtkcam.featurepipe.
   {capture,streaming,p2g,depthmap,vsdof.wrapper}`, `libmtkcam_hal_core_
   featurepolicy`, `libfeaturepolicy*`.
3. Sensor: `libcam.halsensor(.hwintegration)`, `libmtkcam_sensorcontrol`,
   `libcam.sensor_mode_helper(_custom)`, `libcameracustom.imgsensor.core`
   (compiled sensor list = imx989, imx989cts, ov64b, s5kjn1, s5kjn1cts,
   s5kjn1main2, s5kgm2sp, s5kgn1sp, mtk000), `libcameracustom_camera_db_ext`
   (`*_SENSOR_ID` names).
4. Static metadata: `libmtkcam_metastore` (`constructCustStaticMetadata_
   PLATFORM_{AVAILABLE_KEYS,CUSTOM,PROJECT}_SENSOR_DRVNAME_*`),
   `libmtkcam.logicalmodule`, `libcam.halsensor` (`COMMON_SENSOR_*`,
   `PLATFORM_LENS_*`). Includes entries for absent variants
   (IMX989LITE, IMX989RYYB, OV32B40SUB2, OV64B_ALPHAVSDOF) — MTK template.
5. Lens/OIS: `libcameracustom.lens` (`vcm_list_0`: 0x989/0x988/0x8E1 →
   main_vcm, 0x38E2 → main4_vcm, 0x566442 → main2_vcm; `ois_list_*` all
   Dummy), `libcam.hal3a.lensdrv`, `libcam.hal3a.oisdrv`.
6. 3A: `libcam.hal3a*` (ae/awb/af/flash/flicker/lsc/pd/stt/tone/sensor),
   `lib3a.*` algorithm cores, `libaaa_*`, AF-assist PD converters
   `libcamera.custom.af_assist_buf_mgr` (`PD_IMX989MIPIRAW`,
   `PD_S5KJN1MAIN2MIPIRAW` — the two PDAF sensors, consistent with kernel
   `pdaf_cap`).
7. ISP: see `isp-stack.md`.
8. Tuning: `libcameracustom.so` dlopens `<sensor>_mipi_raw_IdxMgr.so`;
   `<sensor>_mipi_raw_tuning.so`; SQLite DBs under
   `/vendor/bin/crossbuild/DataSet/SQLiteModule/db/`.

`/vendor/lib64/mt6878/` duplicates `/vendor/lib64/` byte-for-byte (283
reached ELFs).

## Board-variant handling

`libcameracustom.imgsensor.core.so` and IdxMgr list include s5kgm2sp but
there is **no `s5kgm2sp_mipi_raw_tuning.so` and no s5kgm2sp tuning DB**
(INFERRED: GM2 never shipped). `ov32b40` tuning DB is the untouched MTK
2023 template (ISP_mapping.db identical to imx350/376/586/616) (INFERRED:
OV32B40 front never tuned/shipped).

## Open source status

None of the userspace camera HAL has source locally or publicly
(MTK proprietary `vendor/mediatek/proprietary/hardware/mtkcam*`, path
strings visible in the blobs). Replacement options are therefore
re-use-the-blobs or a different HAL (libcamera's mtkisp7 pipeline in
`/mnt/SamsungSSD/…/external/libcamera` targets mt8188 Chromebooks, not
MT6878 phone ISP7sp — unusable as is).
