# Fast-charge routing on GQ5012BF1: compiled support vs runtime configuration

The oracle is the source-closed, stock-exact charging framework (12 modules),
plus `modules.load` and the merged DT.

## 1. What is actually instantiated

A `chg_alg` registers only if its module is in vendor_boot `modules.load`
and a DT node matches its compatible.

| algorithm | module | in `modules.load`? | DT node | runtime |
|---|---|---|---|---|
| **pe5** (MTK PE5.0, PPS direct charge) | `mtk_pep50.ko` | yes (141) | `/pe5` `mediatek,charger,pe5` | **ACTIVE** |
| **pd** (PD/PPS through the switching charger) | `mtk_pd_charging.ko` | yes (142) | `/pdc` `mediatek,charger,pd` | **ACTIVE** |
| **pe** (PE+ 1.x, VBUS pulse 7/9/12 V) | `mtk_pep.ko` | yes (143) | `/pe` | **ACTIVE** |
| pe4 | `mtk_pep40.ko` | yes (140) | **no `pe4` node** | **NOT PROBED**: module loaded, platform driver never binds |
| pe45 | `mtk_pep45.ko` | **no** | `/pe45` | absent |
| pe2 | `mtk_pep20.ko` | **no** | `/pe2` | absent |
| pe5p | `mtk_pep50p.ko` | **no** | `/pe5p` | absent |
| hvbp | `mtk_hvbpc.ko` | **no** | `/hvbp` | absent |
| UFCS | `ufcs_class` / `ufcs_adapter` | **no module, no adapter** | none | **compiled support only** |

There are `ufcs_adapter` strings in `mtk_charger_framework` / `mtk_pep40`,
but `get_adapter_by_name("ufcs_adapter")` returns NULL at runtime. **UFCS
is not used on GQ5012BF1.**

The PE5 DT lists `support-ta = "pca_ta_pps", "pd_adapter"`. No module
registers `pca_ta_pps`, so PE5 uses only **`pd_adapter`** (`mtk_pd_adapter.ko`
on TCPC `type_c_port0`, MT6375 TCPC).

**Framework selection order** (`mtk_charger.c` exact): pe5p → hvbp → **pe5**
→ pe45 → pe4 → **pd** → pe2 → **pe**. The effective order is
**PE5 → PD → PE+ → basic (MT6375 AICR/ICHG)**.

## 2. Per-protocol path

| protocol | adapter interface | target VBUS | target current | power path | charge pumps |
|---|---|---|---|---|---|
| **PPS (PD 3.0 APDO), PE5** | `pd_adapter` (`MTK_PD_APDO`), authenticated through `pe50_hal_authenticate_ta` | `vta-cap` 13.6–20.0 V; CC/CV loop at about 2×VBAT + Rcable·I | ITA single `ita-level` 3000/2500/2000/1500 mA; dual `ita-level-dual` 6000/4500/3400/2000 mA by Rcable class; ≥ `ita-cap-min` 2000 mA | VBUS → SC8571 master (DVCHG1, i2c-11@0x66), plus SC8571 slave (DVCHG2, i2c-6@0x67) when the dual condition holds → 2S pack. MT6375 `swchg-aicr=0`, i.e. the switching charger is off in PE5 | **YES** |
| **PD fixed / APDO, `pd` algo** | `pd_adapter` (`MTK_PD` / `MTK_PD_APDO`; **YFT: also `WO_APDO_TA`**) | `pd-vbus-low-bound` 5 V – `pd-vbus-upper-bound` 9 V | `sc-input-current` 3.2 A, `sc-charger-current` 3.0 A (1S-equivalent) | VBUS → MT6375 buck → 1S node → (SC8510 1:2) → pack | no |
| **PE+ 1.x** | VBUS pulse on MT6375 | 7/9/12 V (`ta-9v-support`) | 12 V 3.2 A, 9 V / 7 V 1.75 A input; `pe-charger-current` 3.0 A | MT6375 buck | no |
| BC1.2 DCP/CDP / Type-C Rp | MT6375 BC1.2 / TCPC | 5 V | AC 2.1 A ICHG / 1.9 A AICR; **YFT Rp-3A: 1.9 A AICR / 2.1 A ICHG** | MT6375 buck | no |

## 3. PE5 state and path (exact code)

```
TCPC PD contract with APDO → pd_adapter (MTK_PD_APDO)
 → mtk_charger_framework selects pe5 (if is_algo_ready == ALG_READY)
   YFT: is_algo_ready returns ALG_TA_NOT_SUPPORT when TA isn't ready
        (prints "yft_drv:[pe50_is_algo_ready] ta_rdy fail")
   start SOC: start-soc-min 2 % … start-soc-max 80 % (DT), SOC from 3rd-gauge (YFT)
 → pe50_start → init_chip(DVCHG1[,DVCHG2]) = SC8571 REG_RST + DT re-program
 → measure Rcable → select ITA level (single, or dual if slave exists)
 → set_dvchg_protection: VBUSOVP/IBUSOCP/VBATOVP/IBATOCP
       (YFT: VBATOVP + IBATOCP also on the slave; IBATOCP=min(2x,24 A) with slave;
        PE50_IBATOCP_RATIO 250 %)
 → enable DVCHG1 (SC8571 master CHG_EN=1); SS (soft-start) by TA voltage steps
 → dual: when ita_measure ≥ idvchg-ss-init (1000 mA) and
         idvchg_cc − 1000 ≤ ita_lmt (YFT) → enable DVCHG2 (slave) directly
         (YFT: master is NOT disabled first)
 → CC → CV (vbat_cv 8750 mV, stored cv·2 by YFT) → EOC
       (YFT: soc ≥ stop_soc_max (default 85) && vbat > cv − gap && ibat < 2200 mA)
 → pe50_stop → CHG_EN=0 on slave (YFT: only if enabled) and master; TA back to 5 V
```

Thermal limits enforced by PE5 (from DT, all exact):

- TA connector temperature `tta-level-def` 25/75/85/90/95 °C with
  `tta-curlmt` 0/500/1000/1500/stop mA;
- battery `tbat-level-def` 5/25/48/50/52/54 °C;
- dvchg die `tdvchg-level-def` 5/25/90/92/94/96 °C;
- YFT: the curlmts are doubled after a dual-charger attempt;
- YFT: **while the screen is on, ITA is capped at 2500 mA** (display notifier);
- framework JEITA: 0/10/45/50 °C, `max-charge-temp` 55 °C;
- YFT: below 0 °C the framework sets AICR=ICHG=900 mA, and
  `BAT_LOW_TEMP_PROTECT` applies.

**Camera interaction (YFT):** `imgsensor.ko` sets `yft_cam_open_flag` when
a camera opens. `mtk_charger_framework` then disables HV (it sets
`VOLTAGE_MAX` on `mtk-master-charger`) and caps the input at 1.55 A.
`charger_cooling.ko` also gates `VOLTAGE_MAX` on `!yft_cam_open_flag`.

**Fallback:**

- If PE5 is not ready (TA not PPS-capable, SOC/VBAT/temperature outside the
  window, or the YFT `ta_rdy` failure), the framework moves on to `pd`, then
  `pe`, then basic charging.
- On a PE5 error, `pe50_stop` resets the TA to 5 V (and hard-resets it when
  needed). The framework then re-runs selection.
