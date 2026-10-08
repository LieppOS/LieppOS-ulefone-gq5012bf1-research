# PRESERVE:STORAGE — ten GQ5012BF1 storage kernel modules

Source-certification package for the audit group `PRESERVE:STORAGE`
(`ufs-mediatek-mod`, `ufs-mediatek-dbg`, `phy-mtk-ufs`, `rpmb`, `rpmb-mtk`, `mtk-mmc`,
`mtk-mmc-dbg`, `cqhci`, `mtk-wp`, `blocktag`). **Static result: 10/10 byte-exact except the GNU
build ID; source class G → A.** The original reverse engineering is in `../../storage/` and is
preserved unchanged; this package converts it into reproducible source ownership.

| file | content |
|---|---|
| [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) | result table, recovered vs replaced inputs, classification |
| [SOURCE.md](SOURCE.md) | maintained repository, pins, licences, patches, build |
| [HISTORICAL-BUILD-RECOVERY.md](HISTORICAL-BUILD-RECOVERY.md) | why the 2026-10-04 build was exact; hidden inputs and their replacements |
| [BUILD-REPRODUCTION.md](BUILD-REPRODUCTION.md) | inputs, dependency order, clean-checkout B1/B2, build-ID offsets |
| [MODULE-OWNERSHIP.tsv](MODULE-OWNERSHIP.tsv) | identities, stock paths, owners, load lines, class before/after |
| [module-parity.tsv](module-parity.tsv) | per-module hashes and every parity axis |
| [FUNCTION-PARITY.tsv](FUNCTION-PARITY.tsv) / [DATA-PARITY.tsv](DATA-PARITY.tsv) | 380 functions / 386 data objects |
| [ABI-PARITY.md](ABI-PARITY.md) | imports/exports/CRC/KCFI/modinfo, providers |
| [DT-HARDWARE-CONTRACT.md](DT-HARDWARE-CONTRACT.md) | UFS/MSDC/RPMB topology with evidence classes |
| [EARLY-BOOT-DEPENDENCIES.md](EARLY-BOOT-DEPENDENCIES.md) | first-stage lists, dependencies, Slot B test conditions |
| [RPMB-SECURITY-BOUNDARY.md](RPMB-SECURITY-BOUNDARY.md) | normal-world RPMB transport vs TEE |
| [STALE-CLAIMS.md](STALE-CLAIMS.md) | corrected earlier statements |
| `evidence/` | acceptance ledgers, B1/B2 hashes, provider witnesses, build logs, `SHA256SUMS` |
| `source/` | git bundle of the maintained repository, pins, patches |

Registration: no component was created, moved or re-registered. Canonical owner remains
`UFS-RPMB-KERNEL` (DONE; co-owner `MICROSD-KERNEL`). Only the ten source classes in
`kernel-source-parity-audit/` changed.
