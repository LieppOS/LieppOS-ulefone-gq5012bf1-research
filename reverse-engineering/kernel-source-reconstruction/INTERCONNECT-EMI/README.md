# INTERCONNECT-EMI — GQ5012BF1 offline source closure

Three targets: **mmqos-common.ko, mmqos-mt6878.ko, mtk-emi.ko**.
Maintained source commit:e03fc92f55b2976c54b3461741fdcf55f870a3b9.
Complete stock parity except GNU IDs, independent fresh B1/B2; runtime deferred.
Existing owner:COVERED-GENERIC/N/A. This is a source-audit group, not a new component.

- [Reconstruction result](RECONSTRUCTION-REPORT.md) and [source/pins/patches](SOURCE.md)
- [Module parity](MODULE-PARITY.tsv), [functions](FUNCTION-PARITY.tsv), [data](DATA-PARITY.tsv)
- [ABI/provider proofs](ABI-PARITY.md) and [cross-component boundaries](CROSS-COMPONENT-DEPENDENCIES.md)
- [MMQoS implementation/topology](MMQOS-TOPOLOGY.md)
- [Actual EMI ownership](EMI-HARDWARE-CONTRACT.md)
- [DT provider/consumer graph](DT-INTERCONNECT-GRAPH.md)
- [Boot/runtime conditions](BOOT-DEPENDENCIES.md)
- [Independent reproduction](BUILD-REPRODUCTION.md)
- [Corrections/non-claims](STALE-CLAIMS.md)

Evidence includes the exact pre-build audit identities and stock paths/hashes/sizes,
complete generated ledgers, raw difference offsets, compile commands, all33 provider
witnesses, seven target reverse imports,16 private transport edges,166 MMQoS/38 EMI
records,97 DT paths and133 IOMMU records. Public45-file source snapshot and local source
bundle provide recovery. No stock/proprietary implementation is bundled in the recipe.

Offline only. No phone access, experimental module load, register/clock/voltage write,
performance test, reboot/flash/slot change, firmware operation or push.
