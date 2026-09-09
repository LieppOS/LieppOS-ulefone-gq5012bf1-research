# SH366003 periodic-monitor contract

## Scheduling

- Probe initializes `monitor_work` and queues its first run after **2,500 jiffies**.
- Exact GKI `CONFIG_HZ=250`, so initial delay is **10 seconds**.
- Each completed monitor run requeues itself after **1,250 jiffies = 5 seconds** on `system_wq` with `WORK_CPU_UNBOUND`.
- `external_power_changed` cancels no work; it queues the same delayed work with delay zero.
- The module never calls `power_supply_changed`.

## Ordered run

1. Obtain `primary_chg` with `power_supply_get_by_name`.
2. Read `POWER_SUPPLY_PROP_ONLINE`; set cached adapter state to 2 when nonzero, else 0.
3. Read SBS 0x30 `VCHG` and 0x32 `ICHG`.
4. Read SBS 0x0a `BatteryStatus`.
5. Refresh public voltage (0x08), current (0x0c), and pack temperature (0x06).
6. Read SOH (0x2e), cycle count (0x2a), remaining capacity (0x10), and FCC (0x12).
7. Read MAC words 0x0050..0x0057 in order: SafetyAlert, SafetyStatus, PFAlert, PFStatus, OperationStatus, ChargingStatus, GaugingStatus, ManufacturingStatus.
8. Read 32-byte MAC block 0x0071 (DAStatus1); log the first two little-endian cell-voltage words.
9. Re-read SBS current 0x0c directly for signed monitor logging.
10. Log cached RSOC, voltage, signed raw current, temperature, SOH, cycle count, FCC, remaining capacity, VCHG, ICHG, BatteryStatus and status words, then requeue in 1,250 jiffies.

Each failed diagnostic read logs an error and leaves the corresponding prior/zero cache. Telemetry helper failures likewise preserve existing public cache values. I2C operations are serialized by the I/O mutex.

## Runtime correlation

Frozen stock lines such as:

`RSOC=79, Volt=8397, Curr=194, Temp=375, SoH=94, cycnt=26, FCC=8594`

map directly to 0x2c %, 0x08 mV, signed 0x0c mA, 0x06-2731 deci°C, 0x2e %, 0x2a cycles, and 0x12 mAh. Consecutive logs are about five seconds apart.
