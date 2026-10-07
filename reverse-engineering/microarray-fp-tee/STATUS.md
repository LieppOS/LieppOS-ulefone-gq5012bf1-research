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
