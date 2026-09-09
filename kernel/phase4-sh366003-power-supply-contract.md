# SH366003 `3rd-gauge` power-supply contract

## Descriptor

- name: `3rd-gauge`
- type: `POWER_SUPPLY_TYPE_BATTERY`
- registration: `devm_power_supply_register`
- writeable properties: none (`set_property` and `property_is_writeable` are absent)
- notifications: stock imports no `power_supply_changed`; the periodic loop updates caches without emitting uevents
- external-power callback: queues monitor work immediately

## Exact ordered property list

| Order | Property | Stock behavior |
|---:|---|---|
| 0 | `POWER_SUPPLY_PROP_STATUS` | adapter state 1/2 yields `FULL` at 100% or `CHARGING`; otherwise `DISCHARGING` |
| 1 | `POWER_SUPPLY_PROP_PRESENT` | constant 1 |
| 2 | `POWER_SUPPLY_PROP_VOLTAGE_NOW` | cached register 0x08 in mV (nonstandard) |
| 3 | `POWER_SUPPLY_PROP_CURRENT_NOW` | cached absolute signed 0x0c multiplied by 1000 uA |
| 4 | `POWER_SUPPLY_PROP_CAPACITY` | cached register 0x2c percent |
| 5 | `POWER_SUPPLY_PROP_TEMP` | cached register 0x06 minus 2731, 0.1 °C |
| 6 | `POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN` | cached FCC register 0x12 in mAh (nonstandard) |
| 7 | `POWER_SUPPLY_PROP_TECHNOLOGY` | constant `POWER_SUPPLY_TECHNOLOGY_LION` |
| 8 | `POWER_SUPPLY_PROP_CYCLE_COUNT` | cached register 0x2a cycles |
| 9 | `POWER_SUPPLY_PROP_HEALTH` | constant `POWER_SUPPLY_HEALTH_GOOD` |

`ONLINE` is not in the `3rd-gauge` property list. Stock only reads `ONLINE` from the separate `primary_chg` supply.

Unknown properties return `-EINVAL`. Reads are cache-only and do not initiate I2C.

## Live ABI

The frozen snapshot reports:

```text
NAME=3rd-gauge
TYPE=Battery
STATUS=Charging
PRESENT=1
VOLTAGE_NOW=8397
CURRENT_NOW=13000
CAPACITY=79
TEMP=375
CHARGE_FULL_DESIGN=8594
TECHNOLOGY=Li-ion
CYCLE_COUNT=26
HEALTH=Good
```

## Relationship to Android battery

This is not telemetry-only. Stock `mt6375-battery.ko` repeatedly calls `power_supply_get_by_name("3rd-gauge")` from `battery_psy_get_property`, `battery_update_psd`, `battery_update`, `battery_update_routine`, and `mtk_battery_daemon_handler`. `mtk_charger_framework.ko:get_uisoc` also reads property 47 from `3rd-gauge` (a stock out-of-list STATUS/CAPACITY-style lookup path).

The live `battery` power supply mirrors SH366003 SOC 79, current 13,000 uA, cycle 26, voltage after ×1000, and FCC after ×1000. Android BatteryService consumes the republished MT6375 `battery` supply, while the MediaTek kernel battery/charging stack consumes `3rd-gauge` directly.
