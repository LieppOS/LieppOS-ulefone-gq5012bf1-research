# Sensors (GQ5012BF1 / Ulefone Armor 29 Pro Thermal)

Named scope for the MediaTek **sensor 2.0 (sensorhub)** stack on MT6878: the SCP
co-processor host, the Linux transceiver, the sensor 2.0 core and the userspace
multi-HAL that sits on top of them.

Authoritative files:

- [`STATUS.md`](STATUS.md) — phase audit, closure and boundaries.
- [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) — per-module parity.
- [`kernel/parity/`](kernel/parity) — full static parity reports (stock vs rebuild).
- [`hardware/sensor-inventory.tsv`](hardware/sensor-inventory.tsv) — shipped sensors.
- [`notes/scp-sensorhub-architecture.md`](notes/scp-sensorhub-architecture.md) — transport topology.
- [`notes/yft-deltas.md`](notes/yft-deltas.md) — Ulefone/YFT deltas against the donor.
- [`userspace/hal-map.md`](userspace/hal-map.md) — HAL services, subhals, calibration.
- [`reconstruction/`](reconstruction) — the reconstruction patch as applied.

## Architecture in one paragraph

No physical sensor driver runs under Linux. Every part (IMU, magnetometer,
ALS/PS, barometer) is driven by firmware executing on the **SCP** (MT6878
tinysys at `0x1c400000`, 2 cores, hart-pair, 1 MiB SRAM). Linux contributes
three modules: `scp.ko` boots and services the co-processor (IPI, 5 mailboxes,
DVFS, logger, recovery, CHRE), `sensorhub.ko` is the transceiver that owns the
share-memory rings and the SCP sensor IPI protocol, and `hf_manager.ko` is the
sensor 2.0 core exposing `/dev/hf_manager` to userspace. The AIDL multi-HAL
loads the MediaTek subhal, which talks to `/dev/hf_manager`; a separate YFT
(Ulefone ODM) lazy HAL owns calibration.

```
SCP firmware (scp partition, proprietary)
   | physical sensor drivers, fusion, batching, low-power triggers
   | SCP IPI + reserved share memory (mediatek,reserve-memory-scp_share)
scp.ko  <->  mtk_tinysys_ipi.ko / mtk-mbox.ko
   ^
sensorhub.ko (transceiver.c: share-memory rings, timesync, sensor_list, ready)
   |  hf_device ops
hf_manager.ko  ->  /dev/hf_manager        (+ yft_devinfo.ko registration)
   |
android.hardware.sensors@2.X-subhal-mediatek.so
   |  loaded via /vendor/etc/sensors/hals.conf
android.hardware.sensors-service.multihal  (AIDL ISensors/default v2)
   |
sensorservice  ->  22 enumerated sensors
```

## Shipped parts

Six physical sensing elements back 22 Android sensors; the remaining 16 are MTK
fusion/virtual sensors computed on the SCP:

| part | vendor string | role |
|---|---|---|
| ICM4N607 | `iven_sense` | 6-axis IMU (accelerometer + gyroscope), 12.5–400 Hz |
| MMC5603 | `memsic` | 3-axis magnetometer, 5–50 Hz, 4500-event FIFO |
| STK3A5x | `sensortek` | ALS + proximity combo; PS is the wake-up sensor |
| SPL07 | `goer` | barometric pressure, 1–10 Hz |

See [`hardware/sensor-inventory.tsv`](hardware/sensor-inventory.tsv) for the
full handle/type/rate/FIFO/wake matrix taken from live `dumpsys sensorservice`.

## Closure

All three Linux modules are reconstructed to source and rebuilt
**function- and data-byte-identical to the shipped stock modules**:

| module | functions | data objects | imports (modversion CRC) | exports |
|---|---|---|---|---|
| `hf_manager.ko` | 41/41 | 33/33 | 68/68 | 1/1 |
| `sensorhub.ko` | 102/102 | 82/82 | 87/87 | 0/0 |
| `scp.ko` | 196/196 | 178/178 | 138/138 | 1/1 |

Aggregate: **339/339 functions and 293/293 data objects byte-identical**,
`.modinfo` (including `vermagic` and `depends`) identical, ABI identical.

Build: exact GKI `6.1.115-android14-11-g945dff7bc1bf`,
`kernel_device_modules-6.1` commit `7d3c303` on top of the pristine NothingOSS
`device_modules` `957dac1` baseline (`0579490`).

Verification tool: [`../scripts/ko-pair-parity.py`](../scripts/ko-pair-parity.py).
