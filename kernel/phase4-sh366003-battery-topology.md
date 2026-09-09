# GQ5012BF1 battery topology around SH366003

## Evidence graph

```text
multi-cell battery pack
    |  PROVEN (cell-voltage pair from SH366003 MAC 0x0071)
    v
SH366003 pack gauge on I2C 9-0055
    |  PROVEN (stock driver registration)
    v
power_supply: 3rd-gauge
    |  PROVEN (literal lookup/call sites)
    +--> mt6375-battery.ko battery_psy_get_property / update paths
    |       |  PROVEN (live values are rescaled/re-published)
    |       v
    |   power_supply: battery
    |       |  STRONG
    |       v
    |   Android BatteryService
    |
    +--> mtk_charger_framework.ko:get_uisoc
            |  PROVEN
            v
        MediaTek charging policy/UISOC path

MT6375 PMIC coulomb-counter/gauge at I2C 5-0034
    |  PROVEN (DT/runtime/module)
    v
power_supply: mtk-gauge
    |  STRONG (normal MediaTek gauge plumbing)
    v
MT6375 battery/charging framework
```

## Conclusion

The strongest supported model is **pack gauge plus PMIC coulomb-counter**:

- SH366003 supplies pack-level, multi-cell telemetry and learned capacity/SOC.
- MT6375 provides the platform PMIC gauge and charging framework plumbing.
- The MediaTek battery module directly consumes `3rd-gauge` and republishes its values through the primary `battery` power supply; therefore SH366003 is not merely vendor telemetry.
- DAStatus1 exposes two cell-voltage words near 4.2 V each while pack voltage is about 8.4 V, strongly indicating a two-cell series pack (2S). This is strong electrical evidence, but the exact physical wiring and whether any parallel groups exist remain unknown.

`dual independent battery`, `main + auxiliary battery`, and `SH366003 only for passive telemetry` are not supported by the observed value flow.
