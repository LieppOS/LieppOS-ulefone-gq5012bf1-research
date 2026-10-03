# Sensors userspace map

All paths are inside the stock `vendor` partition
(`workspace/gq5012bf1/stock/partitions/vendor`).

## Service

`/vendor/bin/hw/android.hardware.sensors-service.multihal` — the AOSP AIDL
multi-HAL, declared in
`etc/vintf/manifest/android.hardware.sensors-multihal.xml` as
`android.hardware.sensors` **AIDL v2, `ISensors/default`** (no HIDL sensors
HAL is registered on this device).

`etc/init/android.hardware.sensors-service-multihal.rc`:

```
service vendor.sensors-hal-multihal /vendor/bin/hw/android.hardware.sensors-service.multihal
    class hal
    user system
    group system wakelock context_hub input uhid
    task_profiles ServiceCapacityLow
    capabilities BLOCK_SUSPEND
    rlimit rtprio 10 10
```

`context_hub` in the group list is the CHRE path (`scp_chre_manager` in
`scp.ko`); `wakelock` + `BLOCK_SUSPEND` back the wake-up proximity and
gesture sensors.

## Sub-HALs

`etc/sensors/hals.conf` contains exactly one line:

```
android.hardware.sensors@2.X-subhal-mediatek.so
```

| object | size | role |
|---|---|---|
| `lib64/hw/android.hardware.sensors@2.X-subhal-mediatek.so` | 51 400 | multihal sub-HAL shim; bridges to the MTK HAL below |
| `lib64/hw/sensors.mediatek.V2.0.so` | 206 368 | MediaTek sensor 2.0 HAL — opens `/dev/hf_manager`, does enable/batch/flush/calibration |
| `lib64/hw/sensors.mt6878.so` | symlink | → `sensors.mediatek.V2.0.so` |
| `lib64/hw/sensors.dynamic_sensor_hal.so` | 283 728 | AOSP dynamic sensor HAL (external/HID sensors); present but no dynamic sensors enumerated |

`sensors.dynamic_sensor_hal.so` is **not** listed in `hals.conf`, so the
multihal does not load it on this device.

## ODM calibration HAL

`etc/init/vendor.yft.hardware.sensorcali@2.0-service-lazy.rc`:

```
service sensorcali_hal /vendor/bin/hw/vendor.yft.hardware.sensorcali@2.0-service-lazy
    interface vendor.yft.hardware.sensorcali@2.0::ISensorCali default
    interface vendor.yft.hardware.sensorcali@1.0::ISensorCali default
    oneshot
    disabled
    class hal
    user system
    group system radio root bluetooth
```

Lazy (`oneshot` + `disabled`), started on hwservicemanager demand. Two HIDL
interface versions are registered, manifests
`etc/vintf/manifest/sensorcali_manifest_v1.xml` and `..._v2.xml`. This is the
Ulefone/YFT factory calibration path (gyro/accel/ALS/PS offsets) and is the
userspace counterpart of the `yft_devinfo` kernel registry described in
[`../notes/yft-deltas.md`](../notes/yft-deltas.md).

## Storage and init

`etc/init/hw/init.sensor_2_0.rc` (the MTK sensor 2.0 platform rc) only
provisions calibration storage:

```
on post-fs-data
    mkdir /data/vendor/sensor 0774 system system
    #chmod 0660 /dev/hf_manager
    #chown system system /dev/hf_manager
```

The `/dev/hf_manager` ownership lines are commented out — node permissions are
left to ueventd/sepolicy (`vendor_file_contexts`, `vendor_sepolicy.cil`).

## Enumeration result

22 sensors, all served by the single MediaTek sub-HAL; see
[`../hardware/sensor-inventory.tsv`](../hardware/sensor-inventory.tsv).
Six are physical (ICM4N607 accel+gyro, MMC5603 mag, STK3A5x ALS+PS, SPL07
baro), sixteen are SCP-side fusion/virtual sensors reported with vendor string
`mtk`.
