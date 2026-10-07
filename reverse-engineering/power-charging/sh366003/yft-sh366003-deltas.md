# SH366003 board / YFT deltas

There is no public donor of this exact template, so "donor behaviour" below is the
generic Sino Wealth/Linux power-supply convention (and `oplus_sh366002.c` where it shares code).
Every GQ5012BF1 behaviour is byte-proven by the exact rebuild. DT carries no tuning
(`dt-properties.tsv`), so all deltas are code/data deltas.

| # | donor / convention | GQ5012BF1 stock behaviour | change type | evidence | confidence |
|---|---|---|---|---|---|
| D1 | psy named after the chip/“battery” | psy and class both **`3rd-gauge`**; consumed by name by 7 stock modules | YFT code | rebuild, stock module string scan | PROVEN |
| D2 | standalone driver | calls `yft_fuelgauge_device_add(&drv, 0)` in init and `yft_set_fuelgauge_device_used("sh366003", 1)` in probe; writes `fuelgauge_fw_version` | YFT code | `yft-devinfo-boundary.md` | PROVEN |
| D3 | AFI/profile from DT (`battery_params` in sh366002) | AFI **compiled into the module** (`sinofs_afi_data`, 2142 B), single accepted name | YFT/vendor data packaging | rebuild | PROVEN |
| D4 | — | auto-update gate MAC 0x004D ≠ **0x5A93** or FCC < **3500** mAh; refused when `primary_chg` online, SOC < 11 or boot mode 8/9 | YFT policy constants | rebuild | PROVEN |
| D5 | — | boot-mode lookup is a copy of MTK `log_store` `/chosen atag,boot` reader | YFT copy | strings `log_store: …` | PROVEN |
| D6 | standard psy units (µV, µA signed, µAh, design capacity) | VOLTAGE_NOW **mV**, CURRENT_NOW **\|I\|·1000 unsigned**, CHARGE_FULL_DESIGN = **learned FCC mAh**; consumers (mt6375-battery) compensate | template/YFT code | rebuild, `power-supply-interface.tsv` | PROVEN |
| D7 | template with µV/µA caches | run-state reset test compares mV voltage with 4 000 000/3 850 000 and requires `batt_curr ≤ 0` while the cache is \|I\|·1000 ≥ 0; `term_volt` is never set → **MAC 0x0041 reset path is unreachable** in practice | template mismatch (dead code) | rebuild | PROVEN (static) |
| D8 | — | `fg_update_workfunc` fallback snapshot sets `fallback_volt` and `fallback_curr` to **SOC** | stock bug | rebuild (`fallback_flag = 1` first, then soc,soc,soc,temp) | PROVEN |
| D9 | — | probe "maybe upgrade failed": SOC 0 and V 0 with update pending → fake soc 4, 3600, temp 256, fallback on | stock code | rebuild | PROVEN |
| D10 | gauge SOH register | sysfs `soh` is synthetic from cycle count and **decreases on every read** (writes back `display_soh`) | YFT code | rebuild | PROVEN |
| D11 | — | date sysfs: store `YYYYMMDD` → raw I2C register 0x4D, MSB first, only if the stored date is 0; read uses MAC 0x004D LSB first | YFT code (byte-order asymmetry) | rebuild | PROVEN |
| D12 | — | `fg_read_sbs_word` CNTL branch: `mdelay(10)` **only if the subcommand write failed** | template code | rebuild | PROVEN |
| D13 | — | `fg_gauge_unseal` returns 0 even when OperationStatus says "unseal error" | template code | rebuild | PROVEN |
| D14 | — | `hal_fg_init` returns with `data_lock` held when `fg_init` fails | stock bug | rebuild | PROVEN |
| D15 | remove cancels work/destroys class | `sh_fg_remove` is empty; class `3rd-gauge` and delayed works are never torn down (rmmod unsafe; module is first-stage and never unloaded) | stock code | rebuild | PROVEN |
| D16 | log level by config | `fg_sh366003_log = 1` in `.data`: all `[sh366003]` notices on; monitor logs every 5 s | YFT config | data parity | PROVEN |
| D17 | — | `STATUS` uses `adapter_status` ∈ {1,2}; only 0/2 are ever assigned | template residue | rebuild | PROVEN |
| D18 | DT `clock-frequency` on the bus | 400 kHz written on the **child**, unconsumed; bus runs at the 100 kHz default | board DT quirk | `dt-properties.tsv` | STRONGLY SUPPORTED |
