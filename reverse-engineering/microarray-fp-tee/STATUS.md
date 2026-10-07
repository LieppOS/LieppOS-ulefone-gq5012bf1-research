# MICROARRAY-FP-TEE — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | DIRECT FAMILY DONOR (MicroArray v4.0.06, public) + ODM delta, byte-identical |
| parity | stripped rebuild = stock 69 296 B except 20-byte build-id; 27/27 functions, 47/47 data, `__versions` 66/66, `.modinfo`, sections, symtab; B1==B2 |
| providers | all natural; `tee_spi_transfer` 0x184ce7da from public TrustKernel `core/` |
| use | ACTIVE: `spi1.0` → `madev`, `/dev/madev0` |
| defect | unbounded `mmap` over 68 KiB buffer (SELinux-contained in stock) |
| boundary | secure world (SPI proxy TA, MicroArray TA); `tkcore.ko` (TRUSTKERNEL-TEE) |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/MICROARRAY-FP-TEE` →
`Reverse Engineer - DONE/MICROARRAY-FP-TEE` (moved, not copied).

* Added the v4.0.06 donor, six-file reconstruction, B1/B2 and stock parity,
  natural TrustKernel provider evidence, integration checker, corrected claims
  and classification rationale; retained the earlier pass as historical evidence.
* `REVERSE-ENGINEERING-STATUS.md`: PARTIAL row → DONE row plus change-log entry.
  Totals: **85 DONE / 45 PARTIAL / 3 BLOCKED / 0 TODO** (133).
* `COPY-MANIFEST.tsv`: component block rebuilt from 20 PARTIAL rows to **47 DONE
  rows**. All 47 pack files are registered.
* `manifest-audit.py`: 4153/4153 rows resolve; this component has zero drift and
  zero unregistered files. Workspace-wide pre-existing drift remains unchanged
  at 19 rows in five other components, with 408 unregistered files in nine
  other components and one pre-existing duplicate.
