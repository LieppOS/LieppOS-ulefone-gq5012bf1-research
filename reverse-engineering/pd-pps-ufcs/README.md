# PD-PPS-UFCS — closure (2026-10-07, static)

Workspace component `Reverse Engineer - PARTIAL/PD-PPS-UFCS` → **DONE**.

## Scope

The charger-side **PD/PPS policy and adapter path**: `adapter_class`,
`mtk_pd_adapter` (`pd_adapter`), `mtk_charger_algorithm_class`,
`mtk_pd_charging` (PD algorithm), `mtk_pep`, `mtk_pep40` and `mtk_pep50`
(PE5 = PPS 2S direct charge through the SC8571 pumps).

Already DONE elsewhere:
* TCPC/PD protocol engine: TCPC-MT6375, TCPC-CLASS, USB-TYPEC.
* MT6375 charger: MT6375-CHARGER.
* Pumps: SC8571.

## Result

| module | functions | whole file vs stock (stripped) |
|---|---|---|
| adapter_class | 22/22 | identical except build-id |
| mtk_pd_adapter | 16/16 | identical except build-id |
| mtk_charger_algorithm_class | 21/21 | identical except build-id |
| mtk_pd_charging | 51/51 | identical except build-id |
| mtk_pep | 40/40 | identical except build-id |
| mtk_pep40 | 68/68 | identical except build-id |
| mtk_pep50 | 98/98 | identical except build-id |

* Source: KDM workspace tree (pristine ALPS e38092245fb4 + YFT patches
  0001–0006 in `../power-charging/patches/`).
* Deterministic: B1==B2 (`parity/b1-b2-build.txt`).
* Per-module detail: `parity/parity.txt` and `parity/<module>-parity.tsv`.
* Integration: 6/6 (`evidence/integration-checks.txt`).

## Protocol answer (the question this folder asked)

* **PD + PPS only.** Every DT `support-ta` list (3 nodes, including `/pe5`)
  is exactly `pca_ta_pps`, `pd_adapter`.
* Live `mtk-master-charger` advertises `SDP DCP CDP PD PD_PPS`.
* **UFCS is refuted.** There is no DT node or property, no shipped `*ufcs*`
  module (ALPS builds `mtk_ufcs_adapter`, stock does not ship it), and no
  live UFCS type.
* PE5 YFT deltas (3rd-gauge SOC, KPOC ADC path, LCD-on 2.5 A cap, dual-dvchg
  rules, `pca_*`/`fast_charging` sysfs) are documented in
  `../power-charging/README.md`.

## Boundaries

Live PD/PPS traces, negotiated APDOs and delivered power are runtime/physical
integration work, not module understanding.
