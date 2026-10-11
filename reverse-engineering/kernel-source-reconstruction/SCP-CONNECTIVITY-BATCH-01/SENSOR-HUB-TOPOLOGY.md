# GQ5012BF1 sensor-hub topology (Linux view)

Labels as in `SCP-HOST-INTERFACES.md`. Prior research reused: `reverse-engineering/sensors/`.

## Chain

```text
physical sensors --(SCP-side buses, firmware drivers)--> SCP RV55 firmware (fusion, batching, wake logic)
   --share-memory ring + tinysys IPI--> sensorhub.ko (transceiver, timesync, sensor_list, ready)
   --hf_device--> hf_manager.ko (/dev/hf_manager, client rings) --> sensors multi-HAL (userspace)
hf_manager.ko --first-seen registration--> yft_devinfo.ko (Ulefone hardware-info registry)
sensorhub.ko <--display blank notifier-- mtk_disp_notify.ko (timer stubs are log-only)
```

## Sensors actually reported by stock firmware (PROVEN_RUNTIME, live `dumpsys sensorservice`)

| Android type | Part | Notes |
|---|---|---|
| accelerometer / gyroscope | TDK InvenSense ICM4N607 6-axis IMU | 12.5–400 Hz |
| magnetic field | Memsic MMC5603 | 5–50 Hz |
| light / proximity | Sensortek STK3A5x ALS/PS combo | proximity is the wake-up sensor |
| pressure | Goertek SPL07 | 1–10 Hz |
| virtual sensors | MTK fusion: orientation, gravity, linear acc, rotation vectors, step, tilt, significant motion, device orientation, wake gesture | computed in SCP firmware |

Full matrix: `reverse-engineering/sensors/hardware/sensor-inventory.tsv`. The physical sensor drivers run
**in SCP firmware**. No Linux driver exists for them, and the AP-side device tree carries no sensor
bus nodes for them (UNKNOWN which SCP-side I2C/SPI controller and pins they use).

## Kernel interfaces (STOCK_BINARY_IMPLEMENTATION, now source-identical)

| Function | Implementation |
|---|---|
| Enumeration | `sensor_list.c`: `SENS_COMM_CTRL_*` IPI commands; one `hf_device` per reported sensor |
| Host manager | `hf_manager.c`: registry, client rings, enable/batch/flush/calibration/custom_cmd/rawdata |
| Hub transport | `ipi_comm.c`, `sensor_comm.c` over `mtk_ipi_send`/`mtk_ipi_register` (mtk_tinysys_ipi), `scp_ipidev` |
| Shared memory | `share_memory.c` rings in the SCP share region (`scp-mem-tbl`) |
| Event dispatch | `transceiver_translate()` → `hf_manager_event`; sensor-type switch tables depend on the YFT `hf_sensor_type.h` enum (patch 0002) |
| Time sync | `timesync.c`: SCP→AP timestamp mapping |
| Batching | batch/flush commands forwarded; FIFO reservations per sensor (runtime table above) |
| Interrupts | IPI notification (SCP mbox IRQs); no AP-side sensor GPIO IRQ |
| Recovery | `ready.c`: SCP ready/reset handshake via `scp_A_register_notify`; re-enables active sensors after SCP recovery |
| Power | screen-blank notifier registered (`mtk_disp_notifier_register`), but `transceiver_stop/restart_timer` are log-only stubs in stock |
| ODM registry | `yft_{acc,m,alsps,baro,sar}sensor_device_add` + `*_set_*_used` into `yft_devinfo` (first-seen device per class) |

## Module loading (PROVEN_RUNTIME)

`mtk_tinysys_ipi` → `scp` → `hf_manager` → `sensorhub` (vendor_dlkm insmod order 307/391/392). All are
`RECORDED_LOADED`. The `yft_devinfo` dependency is resolved through `modules.dep`.

## Not established

Sensor accuracy, calibration values (`/data/vendor/sensor`, device-unique and deliberately not read) and
SCP-side bus wiring are not established. A source-certified Linux module does not imply that a sensor
works or is populated beyond the runtime list above.
