# CAMERA-OV64B — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | BINARY-EQUIVALENT RECONSTRUCTION (NothingOSS MT6878 `ov64b_mipi_raw` + ODM edits + verbatim stock data) |
| parity | TU 27/27 symbols identical to the shipped `imgsensor.ko`; module differs by 70 B (build-id plus `yft_ctrl_nightled_by_idx`, proven equivalent); B1==B2 |
| use | ACTIVE: `4-0020` bound by chip-ID read; HAL camera 3; IR LEDs follow sensor4 init/power-off |
| boundary | ISP tuning/3A (CAMERA-HAL-ISP); LED driver internals; yft_devinfo implementation |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/CAMERA-OV64B` → `Reverse Engineer - DONE/CAMERA-OV64B`
(moved, not copied).
* README regenerated. Copied in: `notes/{research-README,stale-claims,CLASSIFICATION-CHANGE}.md`,
  parity, evidence and `scripts/`. `notes/cameras.md` refreshed from research;
  PROVENANCE rewritten.
* `REVERSE-ENGINEERING-STATUS.md`: PARTIAL row → DONE row, plus a log entry.
  Totals: **82 DONE / 48 PARTIAL / 3 BLOCKED / 0 TODO** (133).
* `CAMERA-STACK-STATUS.md`: folder list and summary paragraph updated.
* `COPY-MANIFEST.tsv`: the component's rows are rebuilt (5 → 40). All 40 pack
  files are now registered, including the 23 that were never registered.
* `manifest-audit.py`: 4035/4035 rows resolve. Hash/size drift is unchanged at
  19 rows in 5 other components. Unregistered files 490 → 467 (CAMERA-OV64B
  now 0). Status counts 82/48/3/0.
