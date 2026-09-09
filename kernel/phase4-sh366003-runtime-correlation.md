# SH366003 frozen runtime correlation

No new device interaction was performed. Evidence is limited to `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/`.

| Frozen observation | Reconstructed source path | Interpretation |
|---|---|---|
| `9-0055 -> sh366003` | OF/I2C tables and probe | exact bus/address binding |
| `POWER_SUPPLY_NAME=3rd-gauge` | power-supply descriptor | exact public name |
| `RSOC=79` | `fg_read_SOC`, SBS 0x2c | 79% |
| `Volt=8397` / `VOLTAGE_NOW=8397` | `fg_read_Voltage`, SBS 0x08 | 8,397 mV; deliberately nonstandard direct property unit |
| `Curr=83` or `194` | monitor's direct signed SBS 0x0c reread | mA log; public cache is absolute value ×1000 uA |
| `CURRENT_NOW=13000` | `fg_read_Current` | 13 mA exposed as 13,000 uA |
| `Temp=375` | `fg_read_ExtTemperature`, SBS 0x06 | 37.5 °C after subtracting 2731 |
| `SoH=94` | monitor SBS 0x2e | 94% gauge SOH |
| `cycnt=26` | monitor SBS 0x2a | 26 cycles |
| `FCC=8594` | SBS 0x12 | 8,594 mAh |
| `RM=6715` | SBS 0x10 | 6,715 mAh remaining |
| cells ≈4198/4199 and pack ≈8398 | MAC 0x0071 + SBS 0x08 | two series-cell telemetry |
| monitor lines ≈5 s apart | requeue 1,250 jiffies at HZ=250 | exact recurring cadence |

The live main `battery` supply mirrors capacity, current, cycle count and temperature; voltage and FCC appear rescaled by 1000. This corroborates direct MT6375 consumption rather than an unused secondary telemetry node.

Safety: the snapshot was read-only. No register write, AFI trigger, bind/unbind, module load/unload, reset, flash, reboot, or slot change was performed.
