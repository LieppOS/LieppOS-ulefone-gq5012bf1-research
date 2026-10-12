# DISPLAY-BACKLIGHT-G-BATCH-01 — summary

**Result:** all 8 frozen Category G display/backlight identities are independently certified as **Category A**.
The only difference from stock is the 20-byte GNU build ID.

| | |
|---|---|
| Baseline | canonical `1e87ca06` (after G-CANONICAL-INTEGRATION-01: A412 B1 C11 D3 G31 = 413/458) |
| Inventory | all 31 remaining G rows in `G-REMAINING-INVENTORY.tsv` |
| Manifest | 8 identities, sha256 `9b8199c6d7dffac13ced1e9fca3f0ec28de8cdfdd42ff66ff33ec2cdae3cb89c`, committed `a54e1939` before source work |
| Source | `android_kernel_modules_display_backlight_ulefone_gq5012bf1` @ `c0b39b61`; bundle `4b98dbd2…`, verified and cloned fresh twice |
| Proposed totals | **A420 B1 C11 D3 E0 F0 G23 = 421 certified / 37 remaining (91.9%)** |

| Module | Original | Final | Functions | Data | Imports/Exports | KCFI IDs | Relocs | Source | Residual |
|---|---|---|---|---|---|---|---|---|---|
| mtk-pwm | G | A | 87/87 | 30/30 | 27/5 | 0 | 1145 | ALPS 5e415e05 | none |
| pwm-mtk-disp | G | A | 10/10 | 44/44 | 21/0 | 0 | 148 | ALPS + reconstructed GQ5012BF1 delta | none |
| rt4831a_drv | G | A | 14/14 | 19/19 | 16/6 | 0 | 441 | ALPS 5e415e05 | none |
| mediatek-drm-gateic | G | A | 39/39 | 50/50 | 29/12 | 0 | 1326 | ALPS 5e415e05 | none |
| mediatek-drm-panel-drv | G | A | 123/123 | 52/52 | 71/53 | 0 | 7010 | ALPS + shared DRM series | none |
| leds-mtk-disp | G | A | 9/9 | 23/23 | 19/0 | 0 | 90 | ALPS 5e415e05 | none |
| mtk_disp_sec | G | A | 11/11 | 19/19 | 21/0 | 0 | 356 | ALPS + shared DRM series | none |
| met_backlight_api | G | A | 2/2 | 12/12 | 8/0 | 3 | 28 | NothingOSS kernel_modules 5f75a3b1 | none |

All CRCs, licences, namespaces, KCFI type IDs, raw and semantic relocations, section headers, symbol and string
tables and modinfo (vermagic, srcversion, depends) match. No stock module has `.BTF`. No bytes were transplanted,
forced or patched in a binary.

## Findings

- **OEM delta:** `pwm-mtk-disp` is the only module with an OEM delta: the `mediatek,mt6878-disp-pwm0/1` of_match
  entries and probe start/end logs. It was reconstructed from historical LieppOS work, rebased onto ALPS 5e415e05,
  and corroborated by the stock strings and stock DT nodes.
- **New configuration finding:** the GQ5012BF1 vendor config must disable Microtrust (the device ships
  TrustKernel). Otherwise the cmdq-sec provider CRCs imported by `mtk_disp_sec` differ, failing 3/31 boundaries
  without the TEE fragment. Kept as a failed experiment.
- **Hardware (HARDWARE-CONTRACT.md):**
  - The backlight is `lcd-backlight` in CUST_LCM mode (`led-mode = 4`, 0x7ff range, gate-enable).
  - Two display PWMs sit at 0x1100e000/0x1100f000.
  - The general PWM is at 0x11008000.
  - The `lcd_ocp2131@3e` bias node exists, but the production AMOLED panel has `gate-ic = 0`.
  - No DT node binds rt4831a or the generic panel driver.
  - `disp-sec` uses `mediatek,disp-sec-aidctl`.
  - Nothing was operated on hardware.
- **Dependencies:** 212 edges (161 GKI, 7 intra-batch, 44 external). All 8 external providers are already
  canonical A and were witnessed from pinned source (31/31 exact); no ownership changed.

## Reproducibility

- **B1/B2:** fresh clones run sequentially, offline, at four jobs: 8/8 acceptance and 106/106 ELF mutations each.
- **Identity:** 16/16 outputs, 155/155 intermediates, config, symvers and trees identical.
- **Development:** D1–D3 are quarantined with their failures recorded (EXPERIMENTS.tsv).

## Safety

- Canonical was not modified in this stage, and no other agent's work was touched.
- No phone or display/backlight hardware operation, no push.
- Stock operands were read-only private copies, with hashes verified.

Reports: G-REMAINING-INVENTORY.tsv, BASELINE-AND-SELECTION.md, BATCH-MANIFEST.tsv, BATCH-PARITY.tsv,
SOURCE-LINEAGE.md, SOURCE-REPOSITORIES.tsv, DEPENDENCY-GRAPH.tsv, ABI-PROVIDERS.tsv, HARDWARE-CONTRACT.md,
EXPERIMENTS.tsv, BLOCKERS.tsv, BUILD-REPRODUCTION.md, AUDIT-DELTA.tsv, PROPOSED-AUDIT.patch, MERGE-INSTRUCTIONS.md,
NEXT-BATCH.md, BATCH-STATE.json.
