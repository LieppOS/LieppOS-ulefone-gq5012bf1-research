# SH366003 ↔ charging framework boundary

**Measurement (this component):** `sh366003_fg` reads the gauge every 5 s and publishes the cached
values through psy `3rd-gauge` (`power-supply-interface.tsv`). It does no charging control: no
charger property is ever *set*, no current/voltage limit, no JEITA, no termination, no throttling.

**Its only input from the charging side:** `primary_chg` (MT6375 charger psy) `ONLINE` →
`adapter_status = 2`; used for `STATUS` and to refuse AFI programming while a charger is
attached. `adapter_status == 1` is tested but never assigned (template residue).

**Policy (other components, already closed elsewhere — not reopened):**

| consumer | what it takes from `3rd-gauge` | reference |
|---|---|---|
| mt6375-battery (`battery` psy → Android BatteryService/health HAL) | CAPACITY, CYCLE_COUNT, CURRENT_NOW/AVG, VOLTAGE_NOW, CHARGE_FULL_DESIGN, with ×1000 unit rescaling; all daemon SOC set/get overridden | `../yft-power-deltas.md` #14, #15; `../patches/0004-mt6375-battery-…` |
| mtk_charger_framework | `get_uisoc()` = 3rd-gauge CAPACITY | #1 |
| mtk_pep / mtk_pd_charging | start/stop SOC windows | #9, #18 |
| mtk_pep50 (PE5 via SC8571) | `pe50_hal_get_soc` | #19 |
| mt6375-charger | references psy name `3rd-gauge` (string present in stock module) | not analysed here |
| leds-rgb-aw2013 (charge LED) | references psy name `3rd-gauge` | not analysed here |
| SC8571 / SC8510 | no link to the gauge | — |
| thermal / low-battery throttling modules | no reference to `3rd-gauge` (string search over all 457 stock modules finds only the 7 modules above) | stock module scan |

Consequences of the gauge's units that the consumers handle:

- `VOLTAGE_NOW` is mV and `CHARGE_FULL_DESIGN` is mAh → mt6375-battery multiplies by 1000.
- `CURRENT_NOW` has no sign (|I|·1000); direction must come from elsewhere.
- During an AFI update (`fallback_flag = 1`) the module's internal `sh_fg_get_vbat/ibat` would
  return the SOC number (stock bug), but those functions are **not exported** and have no
  caller; the psy path reads `batt_*` caches directly, which the monitor stops refreshing while
  the fallback flag is set.

## Userspace

- Stock SELinux (`vendor_file_contexts`) labels `/sys/class/3rd-gauge/chipid`, `/sys/class/3rd-gauge/fw_version`
  and `…/9-0055/power_supply/3rd-gauge/health` as `yft_fmt_device` (YFT factory-test access); a
  second path `…/11d00000.i2c/i2c-1/1-0055/…` is also labelled (other board variant, not this DT).
- `sh_fg_get_soc/vbat/ibat/tbat` are global but **not exported** (0 exports): no module can call them.
