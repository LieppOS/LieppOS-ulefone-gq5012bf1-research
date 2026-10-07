# MT6375-CHARGER — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | MTK ALPS 5e415e059253 / e38092245fb4 + GQ5012BF1 deltas (mt6375 IRQ-ack reconstructed; charger/battery from power-charging; battery line layout) |
| parity | mt6375, mt6375-adc, mt6375-auxadc, mt6375-charger, mt6375-battery: each identical to stock except build-id; B1==B2 |
| use | ACTIVE: `5-0034` bound, `battery` + `primary_chg` psys live |
| integration | 19/19 (DT, aliases, load order, live, CRC edges, yft_usb_flag, 3rd-gauge, PD notifier) |
| boundary | runtime charging traces/power; PD policy (DONE elsewhere) |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/MT6375-CHARGER` → `Reverse Engineer - DONE/MT6375-CHARGER` (moved),
via `reverse-engineering/scripts/promote-to-done.py`. The earlier build-only witness
`source/mt6375-charger.c` was kept as `notes/historical-mt6375-charger-abi-witness.c`.
Totals **87 DONE / 43 PARTIAL / 3 BLOCKED / 0 TODO**. `COPY-MANIFEST.tsv`: 8 → 26 rows;
0 drift, 0 unregistered files for this component.
