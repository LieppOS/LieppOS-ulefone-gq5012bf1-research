# Evidence index — CAMERA-ISP-KERNEL

Authoritative component:
`reverse-engineering/accelerator-preparation/CAMERA-ISP-KERNEL/`.

## Reconstruction acceptance

| artifact | scope |
|---|---|
| `../RECONSTRUCTION-REPORT.md` | human audit and per-module result |
| `../module-ownership.tsv` | 19-module ownership/source/result ledger |
| `../function-parity.tsv` | 2 971 function rows: 2 970 byte-identical, one proven semantic equivalent |
| `../data-parity.tsv` | 2 474 byte-identical data-object rows |
| `reconstruction/acceptance/acceptance.json` | per-module aggregate machine result |
| `reconstruction/acceptance/abi-parity.tsv` | 2 530 identical ABI rows |
| `reconstruction/acceptance/sections-parity.tsv` | 978 identical headers; 955 identical contents, 19 build-ID-only and four declared residue rows |
| `reconstruction/acceptance/relocations-parity.tsv.xz` | 71 990 raw + semantic identical rows and one proven moved byte-load relocation |
| `reconstruction/acceptance/imgsensor-residue-proof.md` | closed boolean domains, two literal call sites and four-case branch-equivalence proof |
| `reconstruction/manifest-validation.json` | aggregate invariants; `PASS` |
| `reconstruction/SHA256SUMS` | checksums for all retained reconstruction evidence |

## Reproduction

| artifact | scope |
|---|---|
| `reconstruction/build/b1b2-clean-checkout.log` | independent clean-checkout B1/B2 transcript |
| `reconstruction/build/post-build-verifier-audit.log` | current row-level verifier B1/B2 recheck plus tamper-rejection/build-ID regression tests |
| `reconstruction/build/B1-SHA256SUMS.txt` | B1 raw/normalized module hashes |
| `reconstruction/build/B2-SHA256SUMS.txt` | B2 raw/normalized module hashes |
| `reconstruction/build/B1-INTERMEDIATE-SHA256SUMS.txt` | all 225 participating B1 objects |
| `reconstruction/build/SOURCE-TREE` | assembled mtkcam/kdm tree ids |
| `reconstruction/build/config.sha256` | kernel config identity |
| `reconstruction/build/external-provider.symvers` | exact modpost provider ABI input |
| `reconstruction/build/provider-crc-witnesses.tsv` | 97 source-derived + 10 retained-provider CRC witnesses |

The maintained recipe is documented in `../SOURCE.md`; its complete git bundle is under
`../source/`. No stock module, firmware or proprietary userspace payload is carried there.

## Hardware and historical input evidence

* `../stock-modules.tsv` — exact stock hashes, load ordering, aliases and baseline counts;
* `../dt-nodes.tsv`, `../dt-providers.tsv` — decoded selected stock DT topology/resources;
* `../imports.tsv`, `../exports.tsv`, `../functions.tsv`, `../data-symbols.tsv` — original
  stock ELF inventories;
* `../abi-source-witnesses.tsv`, `../source-candidates.tsv` — discovery/source provenance;
* `../firmware-boundaries.tsv`, `../userspace-consumers.tsv` — retained binary boundaries;
* `../stale-claims.md` — superseded PARTIAL/preparation claims.

## Acceptance caveat

This evidence establishes deterministic static equivalence for the owned kernel modules.
No hardware command was executed. Runtime probe, firmware boot, streaming and image quality
remain NOT TESTED.
