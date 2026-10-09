# REGULATORS — four-module source closure

**Complete offline source certification:** exactly four stock identitiesD→A;48 functions,
174 data objects,100 imports,20 KCFI IDs and955 relocations exact. Only GNU build IDs differ.
Fresh committed clone independently reproduced B1/B2; no hardware operation or push.

Maintained source: `../android_kernel_modules_regulators_ulefone_gq5012bf1`, accepted commit
`33130d53c94404f65e1661ffa4113bde21cb4b08`.
This is a reconstruction/audit group, **not a registered component promotion**. All four
keep COVERED-GENERIC ownership. Source snapshots and recoverable recipe bundle are in source/.

- [Reconstruction report](RECONSTRUCTION-REPORT.md)
- [Source pins/preservation](SOURCE.md), [lineage](SOURCE-LINEAGE.md)
- [Build reproduction](BUILD-REPRODUCTION.md), [ABI/provider boundaries](ABI-PARITY.md)
- [Module parity](MODULE-PARITY.tsv), [function parity](FUNCTION-PARITY.tsv), [data parity](DATA-PARITY.tsv)
- [Rail/register behavior](POWER-RAIL-MAPPING.md), [DT supply graph](DT-SUPPLY-GRAPH.md)
- [Boot and deferred SlotB conditions](BOOT-DEPENDENCIES.md), [corrections](STALE-CLAIMS.md)
- [Audit closure, scope invariants and final tests](AUDIT-UPDATE.md)

Evidence includes complete raw/semantic relocation/section/ABI ledgers, exact raw difference
offsets, clean B1/B2 objects/config/tree hashes, provider CRC/KCFI-prefix witnesses, case-sensitive
DT descriptor checks,114 fdtget crosschecks,402 static/live controller property comparisons
and existing unbound RT6160 capture excerpt.9 verifier mutation tests pass. No firmware or
calibration is needed/accessed, and no stock.ko code is preserved inside the source recipe.

Graph:42 selected DT regulator nodes,32 genuine target supply links. Main PMIC slave4,
external buck slave6 with MT6315-compatible child, logical MT6878 DVFSRC and two RT6160
candidate nodes. **No operating voltage was measured.** Always-on/DT availability/source
capabilities are not hardware population/binding proof. Existing source-provider gaps and
runtime power transitions remain explicit; no removal or experimental voltage change is allowed.
