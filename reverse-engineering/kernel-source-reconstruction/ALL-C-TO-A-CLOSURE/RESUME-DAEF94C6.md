# Resume from daef94c6 — recovered evidence, additive DRM scope

Original18 immutable rows are preserved byte-for-byte in C-CLOSURE-ORIGINAL-MANIFEST.tsv.
C-CLOSURE-MANIFEST-AMENDMENT.tsv adds only two verified DRM identities from Codex staged
437ebd57 at maintained source425ffd72; no other checkout or ownership record was edited.

| Module | Recovered class | Actual source commit | Evidence / precise residual | Next executable experiment |
|---|---|---|---|---|
| charger_class.ko | C | b2a343a9d8664b77a63dc16835b5af0fd0e55cf1 | srcversion only (90/90 functions, data 20/21: __UNIQUE_ID_srcversion) | Recover authentic OEM token inputs; retain latest 709/709 TCPC source; no srcversion or counter override. |
| cmdq-platform-mt6878.ko | A | 0b4b07f38397ca6c0630b9edc5ccf2df9251da1d | Strict B1/B2 GNU20-only acceptance; 11 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| cmdq-sec-drv.ko | A | 0b4b07f38397ca6c0630b9edc5ccf2df9251da1d | Strict B1/B2 GNU20-only acceptance; 53 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| cmdq-test.ko | A | 0b4b07f38397ca6c0630b9edc5ccf2df9251da1d | Strict B1/B2 GNU20-only acceptance; 29 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| focaltech_touch_spi_ft3680.ko | C | a56d3d54167dd9e39a8734839fcd430fdfee8f76 | 40 functions size-different; opcode/call-boundary differences; recipe incomplete | Recover an authentic FT3680 SPI OEM driver revision; compare all 40 size-different functions and YFT dependencies. |
| mtk-cmdq-drv-ext.ko | A | 0b4b07f38397ca6c0630b9edc5ccf2df9251da1d | Strict B1/B2 GNU20-only acceptance; 289 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| mtk_chg_type_det.ko | C | b2a343a9d8664b77a63dc16835b5af0fd0e55cf1 | srcversion only (8/8 functions, data 20/21) | Recover authentic OEM token inputs; retain latest 709/709 TCPC source; no srcversion or counter override. |
| rt_pd_manager.ko | C | 758f9edc78c7a50d07b8629126438a3674845911 | srcversion only (11/11 functions, data 19/20) | Recover authentic OEM token inputs; retain latest 709/709 TCPC source; no srcversion or counter override. |
| st21nfc.ko | C | a56d3d54167dd9e39a8734839fcd430fdfee8f76 | 22/24 raw function matches; relocation/semantic acceptance not demonstrated; recipe incomplete | Find original OEM/ST revision beyond the scanned public blobs; close ioctl/ping and natural srcversion, then preserve a full clean recipe. |
| tcpc_class.ko | C | 758f9edc78c7a50d07b8629126438a3674845911 | srcversion only after closure (709/709 functions, 113/114 data, 54 timers exact) | Recover authentic OEM token inputs; retain latest 709/709 TCPC source; no srcversion or counter override. |
| tcpc_mt6375.ko | C | 758f9edc78c7a50d07b8629126438a3674845911 | srcversion + __COUNTER__-numbered .modinfo/addressable objects (66/66 functions, data 21/28) | Recover authentic OEM token inputs; retain latest 709/709 TCPC source; no srcversion or counter override. |
| thermal-generic-adc.ko | A | ff6e97b3bf1f29c1e1fba4ba0c0e28493cbd0698 | Strict B1/B2 GNU20-only acceptance; 4 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| tkcore.ko | C | a56d3d54167dd9e39a8734839fcd430fdfee8f76 | only 5/19 consumer CRC edges reproduced; 14 private-type CRC edges | Find the authentic newer 6:1.1-k6.6 source lineage carrying version/log/list-of-misc-device and extra context fields; use the recovered public headers as constraints, not a stock-compatible replacement. |
| yft_devinfo.ko | C | a56d3d54167dd9e39a8734839fcd430fdfee8f76 | 10 exported device_add CRCs + 11 KCFI IDs differ; provider enum/type graph; probe/sysfs codegen | Recover ODM enum tag/type declarations from authentic consumer/source release; retain CRC/KCFI and sysfs/probe blockers. |
| aw883xx_driver.ko | C | see AUDIO-BATCH-01 | 235/236 raw functions exact; aw883xx_dev_cfg_load 3560 B stock vs 3564 B best experimental build; complete ELF remains unaccepted | Test a helper-extracted insertion sort with independent j/k widths and stock dual bounds-check shape; current variants are unaccepted. |
| bluetooth.ko | A | 40bf42967a213af6faa45a6a579571973b8e5d15 | Strict B1/B2 GNU20-only acceptance; 1257 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| cfg80211.ko | A | 40bf42967a213af6faa45a6a579571973b8e5d15 | Strict B1/B2 GNU20-only acceptance; 1435 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| mac80211.ko | A | 40bf42967a213af6faa45a6a579571973b8e5d15 | Strict B1/B2 GNU20-only acceptance; 1420 functions | Owner-reviewed field-level integration; no runtime or flash claim. |
| drm_display_helper.ko | C (amendment) | 425ffd724462639899a71d3aa57da85b290037fe | Split-BTF type/name references only; all non-BTF/GNU20 bytes exact in Codex B1/B2 | Compile unchanged target source using source-generated MTK ACK OEM base cafe5987; strict GNU20-only whole ELF, then fresh B1/B2 |
| drm_dma_helper.ko | C (amendment) | 425ffd724462639899a71d3aa57da85b290037fe | Split-BTF type/name references only; all non-BTF/GNU20 bytes exact in Codex B1/B2 | Compile unchanged target source using source-generated MTK ACK OEM base cafe5987; strict GNU20-only whole ELF, then fresh B1/B2 |

## Already rejected hypotheses

- CMDQ-OPAQUE-GRAPH: Stock CRC hit for six opaque type nodes; diagnostic only, not installed (SUPPORTED_DIAGNOSTIC).
- CMDQ-TEE-BOTH-OFF: GenieZone provider cannot compile without GP header include path (REJECTED).
- CMDQ-MICROTRUST-OFF: 35/35 joint strict B1/B2, four selected modules A (ACCEPTED).
- BTF-GKI: 130351 types; +15/+389 reference residual (REJECTED).
- BTF-MTK-GKI-CONFIG: 130348 types; not stock base (REJECTED).
- BTF-MTK-VENDOR-RELEASE: Exact base .BTF hash; four selected modules strict B1/B2 accepted (ACCEPTED).
- SRCV-NOTHING: 1100 combinations across four modules; no stock srcversion hit (REJECTED_CANDIDATES).
- SRCV-MICODE: 4443 combinations across four modules; no stock srcversion hit (REJECTED_CANDIDATES).
- AW-GRID-1: 15 builds; no accepted ELF (REJECTED_CANDIDATES).
- AW-GRID-2: 30 builds; best heuristic diff 255 lines (REJECTED_CANDIDATES).
- AW-GRID-3: 45 builds; no improvement on best diagnostic candidate (REJECTED_CANDIDATES).
- AW-BEST-CORROBORATION: 235/236 bodies exact; cfg_load 3564 vs stock3560; C retained (REJECTED).
- ST21-VENDOR-ENV: 6/24 bodies exact, 25 functions; configuration mismatch, not useful baseline (REJECTED_ENVIRONMENT).
- ST21-HISTORICAL-ENV: 24/24 bodies exact vs preserved object; 22/24 vs stock (BASELINE_REPRODUCED).
- ST21-PUBLIC-BLOBS: 28 pairs;4 compile;24 incompatible I2C probe API;no ioctl/ping matches (REJECTED_CANDIDATES).
- ST21-SRCV: Nothing20+MiCode28 tests;no stock fingerprint hit (REJECTED_CANDIDATES).
- TKCORE-ZTE-3.2P3: 52 verified blobs;tee size0x158/context0xc8 versus stock0x138/0xd0;not compatible newer6:1.1-k6.6 lineage (REJECTED_DROP_IN_HISTORICAL_CONSTRAINTS_RECOVERED).
- TKCORE-VIVO-3.2P8: Two pinned trees;57 recovered blobs;10 core struct definitions byte-identical to ZTE3.2p3;version3.2p8.4.14p2, not stock6:1.1-k6.6 (REJECTED_DROP_IN).
- TKCORE-UMIDIGI-SCOPES: Two >50k-path kernel trees have zero target paths;linked145500-path GitLab vendor tree has no matching normal-world private header (NO_MATCH_IN_PINNED_TREE_SCOPES).
- TKCORE-STOCK-TYPE-INFO: Eight frozen stock occurrences have no BTF or debug sections;no private field-name recovery from those sections (UNAVAILABLE_IN_INSPECTED_STOCK_FILES).

## Canonical vs staged accounting

- canonical f61ebf03275ba2d3f6aa4f9d5aebe18e12922263: {'A': 244, 'D': 91, 'G': 108, 'C': 14, 'B': 1}; existing closure-A overlap=0.
- codex57 55dab18ac0470d4145f05fba48076b75d9e75ebb: {'A': 301, 'D': 82, 'G': 54, 'C': 20, 'B': 1}; existing closure-A overlap=0.
- codex22 437ebd5762afa2512fe1ba10102e6b4f4d6beba9: {'A': 323, 'D': 60, 'G': 54, 'C': 20, 'B': 1}; existing closure-A overlap=0.

No projected totals are forced. Original8 A are preserved; scope is20 with12 open before new experiments.
Full identities, source HEADs/status, worktree ownership, B1/B2 axes, checkpoint hashes
and exact per-target next actions are in evidence/resume-context.json.
