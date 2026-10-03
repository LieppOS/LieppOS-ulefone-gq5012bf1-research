# GQ5012BF1 battery architecture: 2S

## Verdict

The pack is **2S** (two cells in series), nominal about 7.7 V and about
8.8 V charged. It is gauged at pack level by the SH366003. The MT6375 /
MTK framework works in **1S-equivalent** units, and the conversion between
the two domains is explicit in software.

## Evidence (all static; no new runtime action)

| # | evidence | source | domain shown |
|---|---|---|---|
| 1 | SC8571 `VBAT_OVP = 90` → 7000 + 90·20 = **8800 mV** on both charge pumps | DT + exact `val2reg` | pack (2S) |
| 2 | PE5 `vbat-cv = 8750 mV`, `start-vbat-max = 8600`, `force-ta-cv-vbat = 9000`, `swchg-off-vbat = 4250` | DT `pe5` | pack (2S); `swchg-off-vbat` is in 1S units |
| 3 | mtk_charger `battery-cv = 4450000 µV`; JEITA CVs 4.25–4.35 V; `min-charger-voltage = 4.5 V` | DT `charger` | 1S-equivalent |
| 4 | **YFT `pe50_set_current_limit()` stores `cv * 2`** (the framework's 1S CV → the 2S CV checked against the SC8571 VBAT ADC) | exact `mtk_pep50` (98/98) | conversion 1S → 2S |
| 5 | SH366003 MAC 0x0071 DAStatus1 shows two cell-voltage words near 4.2 V each while SBS 0x08 voltage is about 8.4 V; MAC 0x0060 block read sums two cell maxima (`maxvoltage = (%d)+(%d)`) | stock driver + earlier read-only sysfs snapshot (`kernel/phase4-sh366003-battery-topology.md`) | 2 cells, series |
| 6 | SC8510 DT names `v2x-*` (2× side) and `v1x-*` (1× side) protections | DT | 2S ↔ 1S bridge exists |
| 7 | PE5 `vta-cap 13.6–20 V` into a 2:1 pump → 6.8–10 V at output, consistent only with 2S | DT + SC8571 silicon class | 2S |

## Representation

- **Capacity:** the SH366003 reports mAh at pack level (FCC/RC in mAh, live
  `8594` mAh). `mt6375-battery` republishes it as µAh. For a 2S pack, the
  mAh figure is the series-string capacity; the Wh figure is about
  2 × 3.85 V × mAh. Marketing "mAh" claims are not used here.
- **Cell voltages:** individually visible **only inside the gauge**
  (DAStatus1, maxvoltage block). They are not exported to Android, apart
  from the stock `/sys/class/3rd-gauge/*` and log lines.
- **Voltage seen by each IC:**

  | IC | sees |
  |---|---|
  | SC8571 | VBAT = pack |
  | SH366003 | pack and cells |
  | SC8510 | pack on V2X, 1S rail on V1X |
  | MT6375 | 1S rail (cell-equivalent). Its CV 4.45 V is applied to the 1S node that SC8510 doubles |

## Unknowns (require teardown/schematic)

- **Protection IC:** the protection front end (pack-side protector/FETs) is
  not visible to software. The SH366003 SafetyAlert/SafetyStatus/PF words
  are read and logged by the stock driver, which suggests gauge-side
  protection logic. The FET ownership is unproven.
- **Balancing:** no driver configures or reports balancing. Whether the
  SH366003 or a protector balances is unknown.
- **Thermistors:**
  - SH366003 `CMD_ExtTemperature` (SBS 0x06), the pack NTC, is used as the
    battery temperature;
  - `CMD_IntTemperature` (0x28) is the die;
  - SC8571 TSBUS/TSBAT faults are disabled in DT (`ts*-flt-dis = 1`), so no
    pump-side NTC protection is active;
  - MT6375 BAT_TEMP is used by mt6375-battery (YFT exposes a BAT_TEMP sysfs).
- **Parallel groups inside each "cell":** unknown.
