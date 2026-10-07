# MADEV-FINGERPRINT — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | BINARY-EQUIVALENT RECONSTRUCTION (no public donor) |
| parity | stripped rebuild = stock 30 552 B except 20-byte build-id; 16/16 functions, 35/35 data, 18/18 imports, 10/10 export CRCs, sections, symtab; B1==B2 |
| use | ACTIVE: first-stage, used by `microarray_fp_tee` (captured `/proc/modules`) |
| boundary | secure world/TA, proprietary HAL; `tkcore.ko` (TRUSTKERNEL-TEE) |
