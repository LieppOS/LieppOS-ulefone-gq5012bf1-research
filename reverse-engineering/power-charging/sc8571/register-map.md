# SC8571 register map as used by the GQ5012BF1 stock driver

Sources:
- the stock-exact `reg_field` table (`sc8571_reg_fields[]`, 58 fields, data object byte-identical);
- the exact `val2reg()` ranges;
- the exact ADC tables;
- the board DT (`gq5012bf1-merged.dts`).

Regmap: 8-bit register / 8-bit value, `max_register = 0x42`, no cache.
`DEVICE_ID` (0x22) must read `0x41`, otherwise probe fails with `-EINVAL`.
The "not find" log prints `ret`, not the ID; this bug is inherited from the
template.

## Protection and threshold fields (programmed from DT at init, and by PE5 at run time)

| idx | field | reg | bits | encoding (exact `val2reg`) | DT master | DT slave | decoded |
|---:|---|---|---|---|---:|---:|---|
| 0 | VBAT_OVP_DIS | 0x00 | 7 | bool | 0 | 0 | enabled |
| 1 | VBAT_OVP | 0x00 | 6:0 | `7000 mV + 20 mV·code`, 7000–9540 | 90 | 90 | **8800 mV (2S pack)** |
| 2 | VBAT_OVP_ALM_DIS | 0x01 | 7 | bool | 1 | 1 | alarm disabled |
| 3 | VBAT_OVP_ALM | 0x01 | 6:0 | same as VBAT_OVP | 70 | 70 | 8400 mV |
| 4 | IBAT_OCP_DIS | 0x02 | 7 | bool | 0 | 0 | enabled |
| 5 | IBAT_OCP | 0x02 | 6:0 | `100 mA·code`, 0–12700 | 81 | 81 | 8100 mA |
| 6 | IBAT_OCP_ALM_DIS | 0x03 | 7 | bool | 1 | 1 | alarm disabled |
| 7 | IBAT_OCP_ALM | 0x03 | 6:0 | | 80 | 80 | raw |
| 8 | IBUS_UCP_DIS | 0x05 | 7 | bool | 0 | 0 | UCP enabled |
| 9 | VBUS_IN_RANGE_DIS | 0x05 | 2 | bool | 0 | 0 | the **slave is forced to 1** after init |
| 10 | VBUS_PD_EN | 0x06 | 7 | bool | 0 | 0 | |
| 11 | VBUS_OVP | 0x06 | 6:0 | `14000 mV + 100 mV·code`, 14000–26700 | 64 | 38 | master 20.4 V / slave 17.8 V |
| 12 | VBUS_OVP_ALM_DIS | 0x07 | 7 | bool | 1 | 1 | |
| 13 | VBUS_OVP_ALM | 0x07 | 6:0 | same as VBUS_OVP | 64 | 34 | 20.4 V / 17.4 V |
| 14 | IBUS_OCP_DIS | 0x08 | 7 | bool | 0 | 0 | enabled |
| 15 | IBUS_OCP | 0x08 | 4:0 | `1000 mA + 250 mA·code`, 1000–8000 | 25 | 25 | 7250 mA |
| 16 | TSHUT_DIS | 0x0a | 7 | bool | 1 | 1 | **die thermal shutdown disabled** |
| 17 | TDIE_ALM_DIS | 0x0a | 4 | bool | – | – | allocated, not written |
| 18 | TSBUS_FLT_DIS | 0x0a | 3 | bool | 1 | 1 | disabled |
| 19 | TSBAT_FLT_DIS | 0x0a | 2 | bool | 1 | 1 | disabled |
| 20 | TDIE_ALM | 0x0b | 7:0 | raw | 200 | 200 | raw |
| 21 | TSBUS_FLT | 0x0c | 7:0 | raw | 21 | 21 | |
| 22 | TSBAT_FLT | 0x0d | 7:0 | raw | 21 | 21 | |
| 23 | VAC1_OVP | 0x0e | 7:5 | raw | 7 | 7 | max |
| 24 | VAC2_OVP | 0x0e | 4:2 | raw | 7 | 7 | max |
| 25 | VAC1_PD_EN | 0x0e | 1 | bool | 0 | 0 | |
| 26 | VAC2_PD_EN | 0x0e | 0 | bool | 0 | 0 | |
| 33 | FSW_SET | 0x10 | 7:5 | raw | 4 | 4 | |
| 34 | WD_TIMEOUT | 0x10 | 4:3 | raw | 0 | 0 | |
| 35 | WD_TIMEOUT_DIS | 0x10 | 2 | bool | 1 | 1 | **watchdog disabled** |
| 36 | SET_IBAT_SNS_RES | 0x11 | 7 | bool | 1 | **0** | master and slave use different sense-R settings |
| 37 | SS_TIMEOUT | 0x11 | 6:4 | raw | 7 | 7 | |
| 38 | IBUS_UCP_FALL_DG | 0x11 | 3:2 | raw | 1 | 1 | |
| 39 | VOUT_OVP_DIS | 0x12 | 7 | bool | 1 | 1 | disabled |
| 40 | VOUT_OVP | 0x12 | 6:5 | raw | 3 | 3 | |
| 41 | MS | 0x12 | 1:0 | master/slave strap | – | – | allocated, not written |
| 50 | SS_TIMEOUT_DIS | 0x41 | 7 | bool | 0 | 0 | |
| 51 | VBUS_OVP_DIS | 0x41 | 6 | bool | 0 | 0 | |
| 52 | PMID2OUT_OVP_DIS | 0x41 | 5 | bool | 0 | 0 | |
| 53 | PMID2OUT_UVP_DIS | 0x41 | 4 | bool | 0 | 0 | |
| 54 | PMID2OUT_UVP | 0x42 | 7:5 | raw | 7 | 7 | |
| 55 | PMID2OUT_OVP | 0x42 | 4:2 | raw | 7 | 7 | |

## Control and status fields

| idx | field | reg | bits | driver use |
|---:|---|---|---|---|
| 27 | REG_RST | 0x0f | 7 | written 1, then 10 ms sleep, at the start of every `init_device` (probe and PE5 `init_chip`) |
| 28 | OTG_EN | 0x0f | 5 | **never written** (no reverse/OTG use of SC8571) |
| 29 | CHG_EN | 0x0f | 4 | `charger_ops.enable`, psy `ONLINE` set |
| 30 | MODE | 0x0f | 3 | never written (bypass/2:1 select is left at the reset default) |
| 31/32 | ACDRV1/2_STAT | 0x0f | 1/0 | never used |
| 42 | CP_SWITCHING_STAT | 0x17 | 6 | `charger_ops.is_enabled`, psy `ONLINE` get |
| 43 | VBUS_ERRORHI_STAT | 0x17 | 4 | not read |
| 44 | VBUS_ERRORLO_STAT | 0x17 | 3 | `charger_ops.is_vbuslowerr` |
| 45 | DEVICE_ID | 0x22 | 7:0 | probe check (0x41) and `/sys/class/fastcharge_<n>/chipid` |
| 46 | ADC_EN | 0x23 | 7 | set before every ADC read, cleared after; cleared at shutdown |
| 47–49 | ACDRV_MANUAL_EN / ACDRV1_EN / ACDRV2_EN | 0x40 | 6/5/4 | never written (external AC-OVP FET drivers are not driven) |
| 56/57 | PMID2OUT_UVP_FLAG / OVP_FLAG | 0x42 | 1/0 | not read (seen only in the IRQ register dump) |

Interrupt/fault flag registers (0x18–0x1c) are not decoded. The IRQ handler
only dumps 0x00–0x42 and calls `power_supply_changed()`.

## ADC (registers 0x25 + 2·ch, big-endian 16 bit, one-shot: ADC_EN=1, msleep(50), read, ADC_EN=0)

| ch | name | scale (`raw·m/l`) | unit | charger_class channel | accuracy reported |
|---:|---|---|---|---|---:|
| 0 | IBUS | ×25/10 | mA | `ADC_CHANNEL_IBUS` | 150000 |
| 1 | VBUS | ×625/100 | mV | `ADC_CHANNEL_VBUS` | 35000 |
| 2 | VAC1 | ×625/100 | mV | – | 35000 |
| 3 | VAC2 | ×625/100 | mV | – | 35000 |
| 4 | VOUT | ×25/10 | mV | `ADC_CHANNEL_VOUT` | 20000 |
| 5 | VBAT | ×25/10 | mV | `ADC_CHANNEL_VBAT` | 20000 |
| 6 | IBAT | ×3125/1000 | mA | `ADC_CHANNEL_IBAT` | 200000 |
| 7 | TSBUS | ×9766/100000 | % | – | 0 |
| 8 | TSBAT | ×9766/100000 | % | – | 0 |
| 9 | TDIE | ×5/10 | °C | `ADC_CHANNEL_TEMP_JC` (not ×1000) | 4 |

`mtk_sc8571_get_adc()` multiplies the result by 1000 to get µV/µA, except
for TDIE. Any other charger_class channel maps to internal channel 10, which
returns `-EINVAL`. The return value is ignored and the output is left
unchanged.

## PE5 → charger_class → SC8571 register writes

| PE5 HAL call (`mtk_pe5_hal.c`) | charger_class op | SC8571 effect |
|---|---|---|
| `pe50_hal_enable_charging(DVCHG1/2, en)` | `enable` | 0x0f bit 4 `CHG_EN` = en, then a full register dump |
| `pe50_hal_set_vbusovp(DVCHGx, uV)` | `set_vbusovp` | 0x06[6:0] = val2reg(uV/1000; 14000..26700, /100) |
| `pe50_hal_set_ibusocp(DVCHGx, uA)` | `set_ibusocp` | 0x08[4:0] = val2reg(uA/1000; 1000..8000, /250) |
| `pe50_hal_set_vbatovp(DVCHGx, uV)` | `set_vbatovp` | 0x00[6:0] = val2reg(uV/1000; 7000..9540, /20) |
| `pe50_hal_set_ibatocp(DVCHGx, uA)` | `set_ibatocp` | 0x02[6:0] = val2reg(uA/1000; 0..12700, /100) |
| `pe50_hal_set_vbatovp_alarm` | `set_vbatovp_alarm` | 0x01[6:0] (same encoding as VBAT_OVP) |
| `pe50_hal_set_vbusovp_alarm` | `set_vbusovp_alarm` | 0x07[6:0] (same encoding as VBUS_OVP) |
| `pe50_hal_reset_vbatovp_alarm` / `reset_vbusovp_alarm` | `reset_*_alarm` | log only, no I2C |
| `pe50_hal_is_vbuslowerr` | `is_vbuslowerr` | read 0x17 bit 3 |
| `pe50_hal_get_adc(DVCHGx, chan)` | `get_adc` | ADC one-shot (above) |
| `pe50_hal_init_chip(DVCHGx)` | `init_chip` | REG_RST, then all 40 DT fields in the stock order; the slave also sets VBUS_IN_RANGE_DIS=1 |
| `charger_dev_is_enabled` (framework psy) | `is_enabled` | read 0x17 bit 6 |

The YFT PE5 changes that act on this map:

- `pe50_set_dvchg_protection()` also programs VBATOVP and IBATOCP on DVCHG2
  (the slave).
- When a slave is present, IBATOCP is `min(2·ibatocp, 24000 mA)`. The
  master's 7-bit field then clamps at 12700 mA.
- `PE50_IBATOCP_RATIO` is 250%.
