# GQ5012BF1 power / charging stack — source reconstruction to stock parity

Status: **DONE.** All 12 charger, gauge and algorithm modules that the stock
vendor ramdisk loads rebuild from source and match stock exactly at the
function level, the data level and the ABI level.

| module | funcs | data | ABI |
|---|---|---|---|
| adapter_class | 22/22 | 9/9 | exact |
| charger_class | 90/90 | 9/9 | exact |
| mtk_charger_algorithm_class | 21/21 | 6/6 | exact |
| mt6375-battery | 332/332 | 103/103 | exact |
| mt6375-charger | 78/78 | 43/43 | exact |
| mtk_chg_type_det | 8/8 | 7/7 | exact |
| mtk_charger_framework | 130/130 | 70/72 (*) | exact (export CRCs 4/4) |
| mtk_pd_adapter | 16/16 | 8/8 | exact |
| mtk_pd_charging | 51/51 | 14/14 | exact |
| mtk_pep | 40/40 | 14/14 | exact |
| mtk_pep40 | 68/68 | 14/14 | exact |
| mtk_pep50 | 98/98 | 33/33 | exact |

(*) The two unmatched data objects in `mtk_charger_framework` are the
`__UNIQUE_ID___addressable_{init,cleanup}_module<N>` symbols. Only the
compiler counter suffix `<N>` differs. Their contents and sizes match.

Per-module reports are in `binary-analysis/per-module/`:
`*.function-parity.tsv`, `*.data-parity.tsv` and `*.abi-parity.tsv`.

## Source

- Tree: `gki-12901745-workspace/kernel_device_modules-6.1`, under `drivers/power/supply`.
- Base: pristine MTK ALPS `e38092245fb4`, taken from the MediaTek history in
  the NothingOSS mt6878 repo (commit `f8e3f87`).
- The GQ5012BF1 (YFT) deltas are in `patches/0001-0006`, which come from
  `git format-patch f8e3f87..9647e3e`.

### mtk_pep50 (PE5.0) YFT deltas (patch 0006)

- `pe50_hal_get_soc`: SOC comes from `power_supply_get_by_name("3rd-gauge")`
  (the SH366003) and not from `bat_psy`.
- `get_boot_mode_from_dts()` is a copy of the log_store helper. It is stored
  in `data->boot_mode`. In KPOC with the algo in CC_CV, `pe50_get_ta_cap*`
  read VBUS/IBUS through the dvchg ADC instead of the TA measure.
- The display notifier (`mtk_disp_notifier_register("mtk_pe50")`) tracks
  `data->lcd_on`. While the screen is on, `pe50_get_ita_lmt()` caps ITA at
  2500 mA.
- `pe50_get_ita_lmt()` doubles the thermal current limits after a dual
  dvchg has been tried. The function is no longer inlined.
- `pe50_get_dvchg_ibusocp()` takes the floor from `idvchg_cc` instead of
  `desc->idvchg_term`, and adds a debug print.
- `pe50_set_dvchg_protection()` also sets VBATOVP and IBATOCP on the slave
  dvchg. When a slave is present, IBATOCP is `min(2*ibatocp, 24000)`.
  `PE50_IBATOCP_RATIO` is 250.
- `pe50_check_eoc()`: EOC triggers at `ibat < 2200 mA` and prints the
  "trigger eoc" message. The `ita_lmt < idvchg_term` stop has been removed.
- The safety check runs from a `const` `fn_descs[]` table, so the loop is
  fully unrolled, and `check_eoc` runs only while the algo is running. A
  debug print `++ goto err i=%d` was added.
- `pe50_check_slave_dvchg_off()` has been removed. Its four call sites now
  hold the `yft_drv_2..5` debug prints. In the TA-CV path, dual dvchg no
  longer disables the master first, and it starts when
  `idvchg_cc - 1000 <= ita_lmt`.
- `PE50_VBUS_CALI_THRESHOLD` is 350 mV. `stop_soc_max` defaults to 85.
  `set_current_limit` stores `cv*2`.
- `pe50_stop()` disables the slave dvchg only if it is enabled, and prints
  a `[blithe]` message. The `__LINE__` values 1219, 3788 and 3791 match stock.
- New sysfs nodes on the pe5 device: `pca_master` and `pca_slave` (dvchg
  IBUS), `pca_voltage` (VBUS) and `fast_charging` (3 while running, else 0).
  They are fed by `pe50_dump_charging_info()` and cleared on plug-out.
- The DT property is read only as `allow-not-check-ta-status`, with dashes.

## Reproduce

`scripts/build_dm.sh "drivers/power/supply/" -k` builds the modules with
the DM Kbuild, using `M=../kernel_device_modules-6.1` and the stock-derived
symvers. Then run `scripts/parity_pwr.sh <module...>`, which strips the
built module and runs `ko_parity.py` and `abi_parity.py` against the stock
`.ko` from `vendor-ramdisks/platform-extracted/lib/modules`.

`scripts/evdiff.sh <module> <func>` is the triage helper that was used for
the large inlined functions such as `pe50_algo_threadfn`. It diffs only the
sequence of string references, calls, globals and immediates.
