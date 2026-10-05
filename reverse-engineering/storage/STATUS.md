# Storage status (2026-10-04)

| scope | state | basis |
|---|---|---|
| UFS host + PHY + debug kernel modules | **CLOSED (exact)** | 3 modules byte-identical except build-id; DT contract and PM fully mapped |
| blocktag (UFS/MMC I/O tracer) | **CLOSED (exact)** | 88/88 |
| RPMB kernel transport (`rpmb`, `rpmb-mtk`, UFS RPMB provider) | **CLOSED (exact)** | GQ5012BF1 ioctl ABI reconstructed and cross-checked against stock `teed` |
| microSD / MSDC1 kernel + DT | **CLOSED (exact)** | 4 modules exact; DT contract proven; CD polarity and VMCH variant are the only board deltas |
| inline crypto / FBE (Linux side) | **MAPPED** | GKI built-in plus the exact MTK enable path; TEE/KeyMint are proprietary |
| A/B, VAB, boot control, DM | **MAPPED (static)** | VABC + XOR + userspace snapshots, hybrid BCB + UFS `bBootLunEn`; runtime OTA not validated |

Runtime validation was not performed (by rule):

- SD insert/remove
- OTA apply/merge
- negotiated UFS gear
- I/O scheduler selection
- WriteBooster flush behaviour

## Open (not claimed)

- Negotiated UFS gear/lanes: no PA attribute capture exists.
- Text of the 69 padded lines in `ufs-mediatek-dbg.c` (only the count is proven).
- Names of the TrustKernel ioctl constants (the numbers are proven, the names are reconstructed).
- Which TEE owns RPMB regions 1 and 2.
- The OEM OTA client and server (proprietary), plus payload production and validation (workspace `OTA-AB-UPDATE`).
- Minor-partition ownership and rollback-index ownership (workspace `PARTITION-OWNERSHIP`).

## Workspace classification (2026-10-04)

Recorded in the organized workspace (`../../../Reverse Engineer - *`, indexed by `REVERSE-ENGINEERING-STATUS.md` and `COPY-MANIFEST.tsv`):

- new **DONE/UFS-RPMB-KERNEL**: ufs-mediatek-mod, ufs-mediatek-dbg, phy-mtk-ufs, rpmb, rpmb-mtk, blocktag
- new **DONE/MICROSD-KERNEL**: mtk-mmc, mtk-mmc-dbg, cqhci, mtk-wp
- `PARTIAL/UFS-STORAGE` and `PARTIAL/MICROSD` stay PARTIAL, re-scoped to runtime behaviour and device-firmware items
- `PARTIAL/OTA-AB-UPDATE` and `PARTIAL/PARTITION-OWNERSHIP` are unchanged

Totals: DONE 55 → 57, total 131 → 133.
