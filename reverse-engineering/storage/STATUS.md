# Storage status (2026-10-06)

| scope | state | basis |
|---|---|---|
| UFS host + PHY + debug kernel modules | **CLOSED (exact)** | 3 modules byte-identical except build-id; DT contract and PM fully mapped |
| blocktag (UFS/MMC I/O tracer) | **CLOSED (exact)** | 88/88 |
| RPMB kernel transport (`rpmb`, `rpmb-mtk`, UFS RPMB provider) | **CLOSED (exact)** | GQ5012BF1 ioctl ABI reconstructed and cross-checked against stock `teed` |
| microSD / MSDC1 kernel + DT | **CLOSED (exact)** | 4 modules exact; DT contract proven; CD polarity and VMCH variant are the only board deltas |
| inline crypto / FBE (Linux side) | **MAPPED** | GKI built-in plus the exact MTK enable path; TEE/KeyMint are proprietary |
| UFS device identity + storage-layout record (workspace `UFS-STORAGE`) | **CLOSED (static)** | package/geometry/spec/FW/health decoded from PL/LK descriptor dumps; gear still UNKNOWN |
| microSD stock contract (workspace `MICROSD`) | **CLOSED (static)** | fstab/vold rule identical in device tree and untouched Slot-B fstab; exFAT mount proven in recovery |
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

## Workspace classification

Recorded in the organized workspace (`../../../Reverse Engineer - *`, indexed by `REVERSE-ENGINEERING-STATUS.md` and `COPY-MANIFEST.tsv`):

- 2026-10-04: new **DONE/UFS-RPMB-KERNEL**: ufs-mediatek-mod, ufs-mediatek-dbg, phy-mtk-ufs, rpmb, rpmb-mtk, blocktag
- 2026-10-04: new **DONE/MICROSD-KERNEL**: mtk-mmc, mtk-mmc-dbg, cqhci, mtk-wp
- 2026-10-04: `UFS-STORAGE` and `MICROSD` re-scoped to runtime behaviour and device-firmware items and recorded as staying PARTIAL. **Superseded 2026-10-06** on this workspace's own definition of DONE - "the named component/scope is sufficiently understood or reconstructed for its defined purpose; full-ROM integration may still remain" - which puts runtime validation on the integration side of that line, not the understanding side. Every item still open in either component is now either a runtime/integration item or a deliberately separate proprietary scope.
- 2026-10-06: **UFS-STORAGE** and `MICROSD` moved PARTIAL → DONE (named scope, static). Each pack carries a DONE README, a `CLASSIFICATION-CHANGE` entry with the promotion rationale (`UFS-STORAGE/notes/CLASSIFICATION-CHANGE.md` is new; MICROSD's gains the second entry) and a refreshed `evidence/EVIDENCE-INDEX.md` pointing at this domain tree and at the two kernel packs. This file is referenced by absolute path from both packs rather than copied, so no byte duplication enters the status trees; `UFS-STORAGE/notes/PROVENANCE.md` path prefixes were reprefixed PARTIAL → DONE and every copied-file SHA256 stayed unchanged. The per-module parity TSVs stay in the two kernel packs; the same bytes are deliberately not re-registered here.
- `PARTIAL/OTA-AB-UPDATE` and `PARTIAL/PARTITION-OWNERSHIP` are unchanged

Totals: 2026-10-04 DONE 55 → 57, total 131 → 133; 2026-10-06 DONE 69 → 71 and PARTIAL 61 → 59 at constant total 133, with BLOCKED 3 and TODO 0. The counts are re-derived from the status directories rather than carried forward (`ulefone-gq5012bf1-research/reverse-engineering/scripts/manifest-audit.py`), and every component appears in exactly one table of `REVERSE-ENGINEERING-STATUS.md`.
