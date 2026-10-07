# CAMERA-S5KJN1MAIN2 — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | BINARY-EQUIVALENT RECONSTRUCTION (no public source; MTK static_ctx skeleton + verbatim stock data) |
| parity | TU 32/32 symbols identical to the shipped `imgsensor.ko`; module differs by 70 B, all outside this TU; B1==B2 |
| use | ACTIVE: `2-0010` bound via +1 pseudo-ID probe; HAL camera 2; 4-cell EEPROM read live; QSC dead; seamless inert |
| defect | `VIDIOC_MTK_G_4CELL_DATA` user-sized buffer gets a fixed 9492 B copy (heap overflow) |
| boundary | tuning/3A/remosaic (CAMERA-HAL-ISP); EEPROM layout (CAMERA-EEPROMS); main4_vcm (CAMERA-VCMS); yft_devinfo |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/CAMERA-S5KJN1MAIN2` → `Reverse Engineer - DONE/CAMERA-S5KJN1MAIN2`
(moved, not copied).
* README regenerated. Copied in: `notes/{research-README,stale-claims,s5kjn1-family,CLASSIFICATION-CHANGE}.md`,
  parity, evidence and `scripts/`. `notes/cameras.md` refreshed; PROVENANCE rewritten.
* `REVERSE-ENGINEERING-STATUS.md`: PARTIAL row → DONE row, plus a log entry.
  Totals: **83 DONE / 47 PARTIAL / 3 BLOCKED / 0 TODO** (133).
* `CAMERA-STACK-STATUS.md`: folder list and summary paragraph updated.
* `COPY-MANIFEST.tsv`: the component's rows are rebuilt (5 → 38). All pack files
  are registered.
* `manifest-audit.py`: 4068/4068 rows resolve. Hash/size drift is unchanged at
  19 rows in 5 other components. Unregistered files 467 → 447 (this component
  now 0). Status counts 83/47/3/0.
