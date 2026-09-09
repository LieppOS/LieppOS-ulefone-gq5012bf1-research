# SH366003 unit and scaling contract

All formulas below are relocation- and instruction-verified against stock. The module does not consistently convert to Linux power-supply base units.

| Quantity | Raw source | Stock cache / public conversion | Exposed/log unit |
|---|---|---|---|
| RSOC | SMBus word 0x2c | `cache = raw` | `%`; monitor prints integer |
| Voltage | SMBus word 0x08 | `cache = raw` | **mV even in `VOLTAGE_NOW`**; observed 8397/8398. This is nonstandard (Linux normally expects uV). MT6375 battery republishes it as 8,397,000 uV. |
| Current | SMBus word 0x0c interpreted `s16` | `cache = abs((s16)raw) * 1000` | `CURRENT_NOW` in uA, but sign is discarded; monitor separately re-reads and prints signed raw mA. Observed 13,000 uA and log `Curr=83`/`194`. |
| Pack temperature | SMBus word 0x06 | `cache = raw - 2731` | 0.1 °C; observed 375 = 37.5 °C |
| Internal temperature | SMBus word 0x28 | raw logged only | unknown raw diagnostic; not the public TEMP cache |
| SOH | SMBus word 0x2e | raw logged only | `%`; observed 94. The separate class `soh` attribute is a synthetic cycle-based value initialized at 100 and is not this register. |
| Cycle count | SMBus word 0x2a | identity | cycles; observed 26 |
| FCC | SMBus word 0x12 | identity | **mAh even in `CHARGE_FULL_DESIGN`**; observed 8594. MT6375 battery republishes 8,594,000 uAh. |
| Remaining capacity | SMBus word 0x10 | identity | mAh; observed 6715; monitor only |
| Charge voltage VCHG | SMBus word 0x30 | identity | mV; observed 8900; monitor only |
| Charge current ICHG | SMBus word 0x32 | identity | mA; observed 9500; monitor only |
| Cell voltages | MAC 0x0071 first two little-endian u16 | identity | mV; observed about 4198/4199 |

## SBS manufacture/profile date

For raw `d` returned by MAC 0x004d:

- day = `d & 0x1f`
- month = `(d >> 5) & 0x0f`
- year = `(d >> 9) + 1980`

`0x5a93` therefore means 2025-04-19 and doubles as the automatic profile-version gate.

## Synthetic class `soh`

The class attribute uses `cycle_count`, not register 0x2e:

- cycles 0..399: decrement the stored display value by `floor(cycles / 40)` on each read;
- cycles >=400: decrement by `10 + floor((cycles - 400) / 60)` on each read.

The stored value starts at 100. This stock stateful behavior can compound across repeated reads and is documented rather than normalized.
