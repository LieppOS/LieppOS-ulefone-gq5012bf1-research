# CAMERA-S5KJN1 — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | BINARY-EQUIVALENT RECONSTRUCTION (s5kjn1, s5kjn1cts: no public source; ov32b40: MTK template) |
| parity | s5kjn1 32/32, s5kjn1cts 28/28, ov32b40 24/24 symbols identical to the shipped `imgsensor.ko`; module differs by 70 B, none in the slot; B1==B2 |
| use | s5kjn1 ACTIVE (`4-0010`, HAL [01] FRONT); s5kjn1cts UNREACHABLE (CTS gate); ov32b40 never probed (dormant BOM option) |
| defects | 4-cell user-sized-buffer overflow (shared with s5kjn1main2); close-path stream-off writes reg 0x0000 |
| boundary | tuning/3A/remosaic (CAMERA-HAL-ISP); EEPROM layout (CAMERA-EEPROMS); yft_devinfo |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/CAMERA-S5KJN1` → `Reverse Engineer - DONE/CAMERA-S5KJN1`
(moved, not copied).
* README regenerated. Added `reconstruction/imgsensor-parity/ov32b40_mipi_raw/`
  (previously missing) and `notes/{research-README,stale-claims,s5kjn1-family,CLASSIFICATION-CHANGE}.md`,
  parity, evidence and `scripts/`. PROVENANCE rewritten.
* `REVERSE-ENGINEERING-STATUS.md`: PARTIAL row → DONE row, plus a log entry.
  Totals: **84 DONE / 46 PARTIAL / 3 BLOCKED / 0 TODO** (133).
* `CAMERA-STACK-STATUS.md`: folder list and summary updated (only CAMERA-HAL-ISP
  remains PARTIAL in the camera stack).
* `COPY-MANIFEST.tsv`: the component's rows are rebuilt (5 → 63). All pack files
  are registered.
* `manifest-audit.py`: 4126/4126 rows resolve. Hash/size drift is unchanged at
  19 rows in 5 other components. Unregistered files 447 → 408 (this component
  now 0). Status counts 84/46/3/0.
