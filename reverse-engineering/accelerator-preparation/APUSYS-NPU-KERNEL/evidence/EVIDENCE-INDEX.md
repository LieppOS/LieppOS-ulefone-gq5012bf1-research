# Evidence index — APUSYS-NPU-KERNEL

## Fixed stock operands

* `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/apu_top.ko` — SHA-256 `260d2bba5e481bae3228398aa85018c14b09dda795962b379a772daa05758469`.
* `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/apusys.ko` — SHA-256 `d74f1d4bddef24cea1cbeb36aba906632f3dbede51e8e3957287b7c35d78d8b6`.
* `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` — source of `dt-nodes.tsv` and `dt-providers.tsv`.
* stock modules/load/dep metadata and coverage-audit tables — source of ownership/load/user/firmware inventories.

## Reconstruction proof

* `reconstruction/acceptance/acceptance.json` — compact per-module counts, hashes, residue and verdict.
* `reconstruction/acceptance/functions-parity.tsv` — every defined function occurrence (duplicate local names retained).
* `reconstruction/acceptance/data-parity.tsv` — every defined data occurrence/BSS layout.
* `reconstruction/acceptance/sections-parity.tsv` — every ELF section and build-ID-only residue.
* `reconstruction/acceptance/abi-parity.tsv` — every import CRC, export bucket/CRC, KCFI ID and modinfo record.
* `reconstruction/acceptance/relocations-parity.tsv` — every raw and semantic relocation.
* `reconstruction/build/b1b2-final.txt` — independent clean clone, source assembly, provider derivation, B1/B2 and acceptance run.
* `reconstruction/build/INTERMEDIATE-SHA256SUMS`, `SHA256SUMS`, `SOURCE-TREE` — deterministic object/output/tree evidence.
* `reconstruction/build/provider-crc-witnesses.tsv` and `external-provider.symvers` — source-generated 13-provider ABI proof.
* root `SHA256SUMS` — integrity for every file above.

## Source preservation

* `../SOURCE.md` — canonical source location, pins and exact commands.
* `../source/android_kernel_modules_apusys_ulefone_gq5012bf1.bundle` — complete maintained-repository history through `924f66b779a64ae0b05f89e233ff2317866050ba`.
* `../source/SOURCE-PINS.tsv`, `patches/`, `reference/` — human-readable redundant pin/patch/hash copy.
* `../source-lineage.md` and `../stale-claims.md` — donor acceptance and corrections.

Original Qwen preparation inventories remain at the pack root as independent stock/source-discovery records. Accepted closure documents supersede only their former `UNKNOWN/PARTIAL` conclusions.
