# Sensors

Full scope: [`reverse-engineering/sensors/`](../reverse-engineering/sensors/)
([status](../reverse-engineering/sensors/STATUS.md)).

## VERIFIED physical sensors

Stock `dumpsys sensorservice` exposed 22 hardware sensors and identified:

| Function | Android name | Vendor |
|---|---|---|
| Accelerometer | `icm4n607_acc` | `iven_sense` |
| Gyroscope | `icm4n607_gyro` | `iven_sense` |
| Magnetometer | `mmc5603` | `memsic` |
| Ambient light | `stk3a5x_als` | `sensortek` |
| Proximity | `stk3a5x_ps` | `sensortek` |
| Barometer | `spl07` | `goer` |

MediaTek fusion exposes orientation, gravity, linear acceleration, rotation
vectors, uncalibrated accelerometer/gyro/magnetometer, significant motion,
step detector/counter, tilt, wake gesture and device orientation. The stock
snapshot contains real accelerometer events, proving more than declaration.
Per-sensor handles, rates, FIFO depths and wake flags:
[`sensor-inventory.tsv`](../reverse-engineering/sensors/hardware/sensor-inventory.tsv).

Stock applications include `YftBarometer`, `YftStepRecord` and
`YftSensorCalibration`; preserving the sensor HAL without its calibration
contract is insufficient.

## VERIFIED stack ownership

No physical sensor driver runs under Linux. All six parts are driven by
firmware on the MT6878 **SCP** (`scp@1c400000`, dual core, 1 MiB SRAM, 5
mailboxes). The Linux side is three modules, all now reconstructed to source
and rebuilt byte-identical to stock (339/339 functions, 293/293 data objects):

| module | role | parity |
|---|---|---|
| `scp.ko` | tinysys remoteproc host: boot, IPI/mbox, DVFS, logger, recovery, CHRE | 196/196 funcs, 178/178 data |
| `sensorhub.ko` | SCP transceiver: share-memory rings, timesync, sensor list, event translation | 102/102 funcs, 82/82 data |
| `hf_manager.ko` | sensor 2.0 core, `/dev/hf_manager` | 41/41 funcs, 33/33 data |

Userspace is the AOSP AIDL multi-HAL (`ISensors/default` v2) loading the single
sub-HAL `android.hardware.sensors@2.X-subhal-mediatek.so` over
`sensors.mediatek.V2.0.so`; see
[`hal-map.md`](../reverse-engineering/sensors/userspace/hal-map.md).

Calibration ownership is resolved: storage is `/data/vendor/sensor` (created by
`init.sensor_2_0.rc`), the userspace owner is the lazy HIDL service
`vendor.yft.hardware.sensorcali@2.0-service-lazy` (v1 + v2 interfaces), and the
kernel counterpart is `yft_devinfo.ko`, which stock `hf_manager.ko` depends on
and calls from `hf_manager_device_info()`
([deltas](../reverse-engineering/sensors/notes/yft-deltas.md)).

## UNKNOWN

- SCP sensor firmware internals: physical sensor drivers, the fusion engine
  behind the 16 virtual sensors, batching and low-power trigger policy. The
  image lives in the signed `scp` partition (`vendor/firmware/remoteproc_scp`
  is a 32-byte stub) and no public source reproduces it.
- SCP-side I²C bus/slave assignment and board orientation matrices — expressed
  only inside that firmware, not in the Linux device tree.
- Full-ROM batching, wake-up, step persistence and calibration behavior require
  enforcing hardware tests.

## PRIMARY EVIDENCE

- `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/sensors.txt`
- `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/{hf_manager,sensorhub,scp,yft_devinfo}.ko`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/sensors/hals.conf`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/init/hw/init.sensor_2_0.rc`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/init/android.hardware.sensors-service-multihal.rc`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/init/vendor.yft.hardware.sensorcali@2.0-service-lazy.rc`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/vintf/manifest/android.hardware.sensors-multihal.xml`
- `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts` (`scp@1c400000`)
