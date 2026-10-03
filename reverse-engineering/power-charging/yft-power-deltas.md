# YFT / Ulefone GQ5012BF1 power-stack deltas

The donor for the MTK modules is the pristine MTK ALPS `e38092245fb4`
(the MediaTek history in NothingOSS mt6878). For the SouthChip drivers it
is SouthChip's public SC8541 MTK template (LKML 2025-10-13).

Every delta below was **reconstructed and proven by exact stock parity**
of the containing module, unless the confidence column says otherwise.
Patches are in `patches/` (DM tree `f8e3f87..HEAD`) and in the DM history
commits named.

## mtk_charger_framework (`mtk_charger.c`, `mtk_basic_charger.c`, patch 0001/0005)

| # | upstream | stock GQ5012BF1 | evidence | confidence |
|---|---|---|---|---|
| 1 | UISOC from `gauge` phandle (`mtk-gauge`) | `get_uisoc()` reads `power_supply_get_by_name("3rd-gauge")` CAPACITY | 130/130 exact | exact |
| 2 | – | exports `bool yft_cam_open_flag __read_mostly = 0` (CRC 0x8f10a053) and `int yft_long_charger_flag = 0x1234` | export CRCs 4/4 | exact |
| 3 | – | when `yft_cam_open_flag` is set: input limit 1.55 A, and `high_voltage_supply_enable()` sets `VOLTAGE_MAX` on `mtk-master-charger` (HV off while a camera is open). Setter: `imgsensor.ko` `imgsensor_high_voltage_supply()`; also read by `charger_cooling.ko` | exact (framework); consumer relocations | exact |
| 4 | Type-C Rp 3.0 A → 3.0 A/3.0 A | Rp 3.0 A → AICR 1.9 A / ICHG 2.1 A | exact | exact |
| 5 | – | battery temperature < 0 °C → AICR = ICHG = 0.9 A | exact | exact |
| 6 | `sc_*`/thermal sysfs | `yft_charging_current` (RW: 0 = thermal ICHG limit 0 and indicator 5; 0x1234 = no limit and indicator 0x15) and `gftk_charger_type` (RO: 3 = PD/APDO, 0 = UFCS/unknown, 1 otherwise) | exact | exact |
| 7 | KPOC boot switch default | `charger_boot_switch=` parsed from `/chosen` bootargs (`p + 20` form) | exact | exact |
| 8 | – | `BAT_LOW_TEMP_PROTECT` path | exact | exact |

## mtk_pep (PE+) / mtk_pd_charging (patch 0003)

| # | upstream | stock | confidence |
|---|---|---|---|
| 9 | SOC from `gauge` phandle | `3rd-gauge` CAPACITY (pe and pd) | exact |
| 10 | PE+ only on DCP | PE+ on **DCP or CDP** | exact |
| 11 | `pe_hal_set_input_current` argument order | fixed icl/cc argument order | exact |
| 12 | PD algorithm only for `APDO_TA` | also for `WO_APDO_TA` | exact |
| 13 | PD: thermal/limit check before SOC waiver | SOC/VBAT **waiver evaluated first** | exact |

## mt6375-battery (patch 0004)

| # | upstream | stock | confidence |
|---|---|---|---|
| 14 | `battery` psy from the MT6375 GM3.0 gauge | CAPACITY, CYCLE_COUNT, CURRENT_NOW/AVG, VOLTAGE_NOW, CHARGE_FULL_DESIGN, … proxied from **`3rd-gauge` (SH366003)** with unit rescaling | exact 332/332 |
| 15 | daemon SOC from the GM3.0 algorithm | every daemon SET/GET SOC (RTC_UI_SOC, CON0_SOC, KERNEL_SOC, UI_SOC) overridden by `3rd-gauge` CAPACITY | exact |
| 16 | – | `BAT_TEMP` sysfs; `SHUTDOWN_GAUGE1_XMINS = 0` | exact |

## mt6375-charger (DM commits c1eef8d/d7c6e3d)

| # | upstream | stock | confidence |
|---|---|---|---|
| 17 | – | exports `yft_usb_flag` (GPL). It gates the BC1.2 / USB-PHY switching while the thermal camera (`yft_tiny2c_usb`) owns USB | exact 78/78 |
| 18 | – | TCPC PD notifier, CDP-on-PD, IEOC deglitch, `3rd-gauge` use | exact |

## mtk_pep50 (PE5) (patch 0006)

| # | upstream | stock | confidence |
|---|---|---|---|
| 19 | `pe50_hal_get_soc` from the gauge | `3rd-gauge` CAPACITY | exact |
| 20 | – | `get_boot_mode_from_dts()`. In KPOC with CC_CV, `pe50_get_ta_cap*` use the dvchg ADC VBUS/IBUS instead of TA measurements | exact |
| 21 | – | display notifier `mtk_pe50`: **ITA ≤ 2500 mA while the LCD is on** | exact |
| 22 | thermal curlmt subtracted once | doubled after dual-dvchg was tried | exact |
| 23 | IBUSOCP floor `idvchg_term` | floor `idvchg_cc`, with a debug print | exact |
| 24 | protection on the master only | **VBATOVP + IBATOCP also programmed on the slave**; with a slave, IBATOCP = min(2·x, 24000 mA); `PE50_IBATOCP_RATIO` 110 → **250** | exact |
| 25 | EOC `ibat < 2·idvchg_term`; stop when `ita_lmt < idvchg_term` | EOC `ibat < 2200 mA` with a log; the ita_lmt stop is removed | exact |
| 26 | `fn_descs[]` table non-const, EOC not checked while running | const table (fully unrolled); `check_eoc` runs while the algo runs; `++ goto err` debug print | exact |
| 27 | `pe50_check_slave_dvchg_off()` (4 sites) | **removed**; the sites hold `yft_drv_2..5` debug prints | exact |
| 28 | TA-CV dual start: disable the master first; `idvchg_cc ≤ ita_lmt` | master left on; `idvchg_cc − 1000 ≤ ita_lmt` | exact |
| 29 | `PE50_VBUS_CALI_THRESHOLD` 150 mV; `stop_soc_max` 99; CV stored as is | 350 mV; **85**; **`cv * 2`** (1S → 2S) | exact |
| 30 | stop disables the slave unconditionally | only if enabled; `[blithe]` log | exact |
| 31 | – | sysfs `pca_master` / `pca_slave` (dvchg IBUS), `pca_voltage` (VBUS), `fast_charging` (3 while running) | exact |
| 32 | `is_algo_ready` returns the adapter state when TA is not ready | returns `ALG_TA_NOT_SUPPORT` with a `yft_drv` log | exact |
| 33 | DT `allow_not_check_ta_status` or `allow-not-check-ta-status` | dash form only | exact |

## sc8571_charger (SouthChip template → stock)

| # | template (SC8541) | stock | confidence |
|---|---|---|---|
| 34 | IRQ decodes flag registers and sends `charger_dev_notify` | IRQ only dumps registers 0x00–0x42 and calls `power_supply_changed` (no notify to PE5) | exact 34/34 |
| 35 | `dump_reg` in `init_device` | `dump_reg` after every `CHG_EN` write | exact |
| 36 | – | `/sys/class/fastcharge_<n>/chipid` class + `gftk chg_dev_name` log (YFT naming style) | exact |
| 37 | no shutdown hook | shutdown clears `ADC_EN` | exact |
| 38 | `VBAT_OVP` 3840 + 10 mV (1S part) | 7000 + 20 mV / 9540 max (SC8571 2S ranges); `VBUS_OVP` 14000 + 100 | exact |

## sc851x_charger (SC8510)

| # | stock | confidence |
|---|---|---|
| 39 | no charger/psy registration; IRQ logs FLAG1–3; shutdown clears `AUDIO_EN` ("close AUDIO_EN") | exact 11/11 |

## sh366003_fg (SinoWealth driver, YFT integration)

| # | stock | confidence |
|---|---|---|
| 40 | registers psy **`3rd-gauge`** (the name every YFT consumer above uses) | stock oracle |
| 41 | `depends=yft_devinfo`: `yft_fuelgauge_device_add(driver)`, `yft_set_fuelgauge_device_used("sh366003")`, writes `fuelgauge_fw_version` (`"Vno:0x%02x-%s(%02d%02d)"`) | stock oracle |
| 42 | AFI update gated on adapter status, SOC and boot mode (`not Update FW!! adapter_status=…`); KPOC/boot mode read from `/chosen atag,boot` | stock oracle |
| 43 | the `primary_chg` psy is read in the monitor loop (`fg_check_charge_type`) | stock oracle |
| 44 | before an AFI program the fallback quartet is filled as soc/**soc**/**soc**/temp (voltage and current fallbacks hold the SOC value) | stock disassembly |
| 45 | when an update is needed and soc = volt = 0, probe forces soc 4 %, 3600 mV, 25.6 °C and `use_fallback = 1` ("maybe upgrade failed") | stock disassembly |
| 46 | `/sys/class/3rd-gauge/soh` writes its result back into `display_soh` (100 at probe), so SOH decreases on every read | stock disassembly |
| 47 | `fg_sh366003_log = 1` in `.data` (verbose gauge logging on in production) | stock .data |

## Device tree (board-specific values, not code)

- PE5: dual-dvchg ITA levels 6000/4500/3400/2000 mA; `vbat-cv` 8750;
  `start-soc-max` 80; `vta-cap` 13.6–20 V; `support-ta` includes
  `pca_ta_pps`, which has no provider.
- SC8571: the slave's VBUS_OVP is lower (17.8 V vs 20.4 V); the slave's
  `ibat-sns-r` is 0 vs the master's 1; TSHUT, TS faults, VOUT_OVP and the
  watchdog are disabled.
- The `pe4` node is absent although `mtk_pep40.ko` is loaded. pe2, pe45,
  pe5p and hvbp nodes exist, but their modules are not loaded.
