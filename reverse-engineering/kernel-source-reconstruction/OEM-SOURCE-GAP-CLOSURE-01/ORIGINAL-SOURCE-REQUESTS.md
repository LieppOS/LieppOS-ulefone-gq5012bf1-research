# Original-source request package: index

All documents are drafts. **None has been sent, filed or published.** Sending requires the user's explicit
approval.

| Document | Addressee | Scope |
|---|---|---|
| `ULEFONE-SOURCE-REQUEST.md` | Ulefone (distributor; primary) | complete vendor module tree as built for GQ5012BF1_EEA_V15, plus the 24 named GPL modules |
| `TRUSTKERNEL-SOURCE-REQUEST.md` | TrustKernel, or via Ulefone | TKCore normal-world driver 6:1.1-k6.6 (`tkcore`, `tkcore_drv`) |
| `COMPONENT-SOURCE-REQUESTS.md` | MediaTek, Richtek, Awinic, FocalTech, ST, SouthChip, Sinowealth, Hynitron, ODM | secondary or courtesy routes |
| `SOURCE-RELEASE-EVIDENCE.md` | (supporting) | per-module licence, author and hash evidence, plus public sources checked |
| `MISSING-SOURCE-MATRIX.tsv` | (supporting) | all 37 currently uncertified identities, with gap type and next experiment |

## Priorities by expected certification gain

1. **Ulefone full tree:** up to 24 modules, the D rows included.
2. **Richtek/MediaTek exact charging and Type-C files:** 5 C rows that need only srcversion/line metadata.
3. **TrustKernel 6:1.1:** `tkcore` C→A. Declarations were already closed this session; `tkcore_drv` is Codex's.
4. **MediaTek flashlight-core.c:** `flashlight` D→A. It also stabilizes the Codex AW365xx consumers.
