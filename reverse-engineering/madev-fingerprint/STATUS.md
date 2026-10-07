# MADEV-FINGERPRINT — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | BINARY-EQUIVALENT RECONSTRUCTION (no public donor) |
| parity | stripped rebuild = stock 30 552 B except 20-byte build-id; 16/16 functions, 35/35 data, 18/18 imports, 10/10 export CRCs, sections, symtab; B1==B2 |
| use | ACTIVE: first-stage, used by `microarray_fp_tee` (captured `/proc/modules`) |
| boundary | secure world/TA, proprietary HAL; `tkcore.ko` (TRUSTKERNEL-TEE) |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/MADEV-FINGERPRINT` → `Reverse Engineer - DONE/MADEV-FINGERPRINT`
(moved, not copied), using `reverse-engineering/scripts/promote-to-done.py`.
Status index row moved and logged; totals **86 DONE / 44 PARTIAL / 3 BLOCKED / 0 TODO**.
`COPY-MANIFEST.tsv`: 17 → 31 rows, 0 drift and 0 unregistered files for this
component (`manifest-audit.py`: 4167/4167 rows resolve; pre-existing drift elsewhere unchanged).
