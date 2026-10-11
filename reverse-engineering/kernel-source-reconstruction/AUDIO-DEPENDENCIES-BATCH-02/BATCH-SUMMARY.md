# Audio dependency source batch02 —20 A,2 retained C

## Scope and result

Frozen22 identities were processed, not just the first provider. All22 compile from maintained complete source. Twenty pass strict complete stock ELF acceptance with only the structural20-byte GNU build-ID descriptor normalized. The two native DRM helpers remainC: their executable/data/import/export/CRC/KCFI/relocation/modinfo/layout bytes all match, but their natural public-base split-BTF does not equal the private OEM-base representation. No BTF or CRC bytes were copied or rewritten.

The final six B1/B2 records cover44 raw/stripped file pairs and461 intermediate-object pairs, with actual source/config/core/provider/native ABI identity comparisons. This includes corrected compile-time host/assembler/compat-vDSO path mappings; the failed26-object comparison remains preserved. There are68 actual ELF mutation/control cases and14 unchanged audit mutation tests, all passing their positive/negative expectations. Four unchanged independent SLBC/modem records were rehashed rather than unnecessarily rebuilt after the shared source-only path fix; two fresh shared builds use the final source tip.

All continuing work uses four jobs, hard CPU affinity60–63 and nice10. Original development source/build paths were unavailable during the independent builds and were restored. No stock operand was stripped or edited in place.

## Complete target table

Commit abbreviations resolve to the full source tips below. Functions/data are measured named-object counts, not estimates. All listed CRC/KCFI and raw/semantic relocations match, including C rows; C does **not** mean full stock acceptance.

| Module (.ko) | Initial | Final | Functions | Data | CRC/KCFI | Relocations | Source commit | Residual |
|---|---|---|---:|---:|---|---|---|---|
| ccci_auxadc | G | A | 6 | 19 | exact | exact | 5a7980681a71 | none |
| ccci_ccif | G | A | 43 | 31 | exact | exact | 5a7980681a71 | none |
| ccci_dpmaif | G | A | 222 | 135 | exact | exact | 5a7980681a71 | none |
| ccci_fsm_scp | G | A | 17 | 30 | exact | exact | 5a7980681a71 | none |
| ccci_md_all | G | A | 370 | 173 | exact | exact | 5a7980681a71 | none |
| ccci_util_lib | G | A | 126 | 142 | exact | exact | 5a7980681a71 | none |
| ccmni | G | A | 27 | 22 | exact | exact | 5a7980681a71 | none |
| drm_display_helper | D | C | 199 | 46 | exact | exact | 425ffd724462 | private OEM BTF base |
| drm_dma_helper | D | C | 19 | 13 | exact | exact | 425ffd724462 | private OEM BTF base |
| leds-mtk | G | A | 25 | 27 | exact | exact | 425ffd724462 | none |
| mediatek-drm | G | A | 2446 | 2083 | exact | exact | 425ffd724462 | none |
| mmprofile | D | A | 37 | 50 | exact | exact | 425ffd724462 | none |
| mtk-mmdvfs-debug | D | A | 20 | 34 | exact | exact | 425ffd724462 | none |
| mtk-mmdvfs-ftrace | D | A | 30 | 61 | exact | exact | 425ffd724462 | none |
| mtk-mminfra-debug | D | A | 29 | 48 | exact | exact | 425ffd724462 | none |
| mtk_disp_notify | G | A | 6 | 12 | exact | exact | 425ffd724462 | none |
| mtk_mdpm | G | A | 17 | 111 | exact | exact | 5a7980681a71 | none |
| mtk_panel_ext | G | A | 12 | 14 | exact | exact | 425ffd724462 | none |
| mtk_slbc | D | A | 32 | 15 | exact | exact | 9e1c978ae4e6 | none |
| mtk_sync | D | A | 14 | 11 | exact | exact | 425ffd724462 | none |
| rps_perf | G | A | 1 | 9 | exact | exact | 5a7980681a71 | none |
| system_heap | D | A | 70 | 47 | exact | exact | 425ffd724462 | none |

Across22 targets:3768 functions/3133 data objects; the20 A targets account for3550/3074. Full per-function/data/export/relocation/section inventories and complete-file acceptance are in the referenced reports, not inferred from these counts.

## Foundation, graph and ownership

Existing AUDIO-BATCH-01 is genuinely preserved at research f00bd8af7e6bd4fde4355ae67e8392feab596a80 and source ec57573ca9f48c92b8485137064840025525f23f:21 targets/20 A/1 C. Its actual existing B1/B2 outputs and220 objects were rechecked without recompiling any audio target. AW883xx remains Claude-owned and unchanged. SCP-CONNECTIVITY-BATCH-01's entire frozen ownership was excluded. Both earlier branches remain unintegrated in the frozen canonical baseline.

The21 audio modules'1162 direct imports are resolved in AUDIO-DEPENDENCY-GRAPH.tsv. The eligible uncertified transitive ABI-provider set is19; three additional source/stock-supported registered modem-host endpoints bring the coherent frozen scope to22. No firmware file or unrelated modem module was added to reach a quota. Display/shared-buffer infrastructure is explicitly labeled transitive: CCCI really imports DRM MIPI/oscillator callbacks, so recovering this source was necessary to this closure rather than a claim that display is an audio engine.

SLBC is the source-matched common-ops facade. Missing backend callbacks return -ENODEV; generic other-SoC cache/SCMI code is PUBLIC_SOURCE_ONLY, not proof of an MT6878 backend. system_heap is a genuine transitive buffer provider, not a presumed speech sample allocator.

## Modem, DSP and board boundaries

get_md_resv_mem_info is provided by ccci_util_lib; get_smem_phy_start_addr by ccci_md_all. `/dev/ccci_aud` AUDIO RX7/TX6 uses CCIF control/character transport; RAW_AUDIO and USIP expose shared mappings. DPMAIF/CCMNI/RPS are cellular packet transport, not speech PCM sample transport. CCCI core and its SCP FSM bridge implement host dispatch, readiness/exception/shared-memory/IPI coordination. Existing audio IPI/ADSP/SCP targets were not re-reconstructed.

VOICE-PATH-KERNEL-INTERFACES.md reuses the phone's saved MT6878 AFE, MT6369 codec/receiver/microphone, AW88394 I2S and clock/power/DT evidence, explicitly distinguishing prior PROVEN_RUNTIME, ENABLED_IN_STOCK_DT, STOCK_BINARY_IMPLEMENTATION, PUBLIC_SOURCE_ONLY and UNKNOWN. Proprietary DSP/modem algorithms, Audio HAL/policy and successful calls/physical routing/timing remain outside kernel source parity. Nothing ran on the phone; no DSP firmware, microphone recording or voice call was triggered.

## Maintained source tips and recovery

- android_kernel_modules_slbc_ulefone_gq5012bf1: `9e1c978ae4e687367e1d154f07553fa86547b3f3`.
- android_kernel_modules_modem_audio_transport_ulefone_gq5012bf1: `5a7980681a71388fc50379699e041e8a071f344f`.
- android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1: `425ffd724462639899a71d3aa57da85b290037fe`.

Source pins include ALPS5e415e, Nothing957dac, common6b18f0, Clang7775eb and the independently pinned public GKI/pahole native environment. Historical complete CCCI source equals the pinned ALPS lineage; ten actual historical DRM patches were recovered instead of rewritten. SOURCE-LINEAGE.md and per-engine pins/patches contain full provenance. Authentic source-only ABI witnesses are explicitly ABI evidence, not replacement target implementations or certifications of their provider modules.

Every current tip has a verified Git bundle and fresh recovery clones with fsck/no alternates. SOURCE-REPOSITORIES.tsv records exact bundle hashes. BUILD-REPRODUCTION.md points to actual B1/B2 outputs,922 object instances, configs/ABI manifests, successes and failed experiments.

Research checkpoints include `ebe89dbd` (foundation), `ef7d0ade` (frozen22 scope), `58b98592` (complete SLBC/nine modem source recovery), and `e32f2d0250d5d740a2d560465f6e2459e8a263c6` (shared-source proof artifacts and low-CPU failures/path fixes). Final local research commit is identified by the branch HEAD after committing this report; no push.

## Audit delta and exact totals

The unchanged validator passes the isolated proposed audit with explicit retained unresolved source classes, zero errors. All14 existing audit mutation tests pass. Actual private immutable stock bytes match every one of458 identities/471 occurrences. Missing git-ignored original research/saved capture inputs were aliased only after matching their already-frozen hashes; prior missing-input validation failures remain preserved. No expected hash, assertion or verifier was weakened.

AUDIT-DELTA.tsv contains364 per-field compare-and-swap entries for22 selected identities; AUDIT-JSON-DELTA.json carries associated original/proposed JSON evidence. All436 unselected audit rows and component/runtime owners are unchanged. No live canonical audit or earlier branch result was applied.

- Frozen committed canonical:245 certified/213 remaining.
- This independently validated proposal:20 additional A;2 retained C.
- Projected if **only this batch** is integrated:265 certified/193 remaining.
- Separate pending audio20/SCP17 are not included or double-counted.

Canonical live validation still requires the inventory owner to restore60 shared signature-stripped operands. The private-input PASS is not a claim those shared files were restored. Integration must wait for concurrent Claude assignments and exact CAS/revalidation; see MERGE-INSTRUCTIONS.md.

## Remaining actual blockers and next work

The two C helpers need the genuine OEM g945dff7bc1bf split-BTF base, whose module-local references demonstrate15 additional types and389 string bytes versus public GKI12901745. Their implementations are complete; a public-base BTF reference rewrite would be prohibited false closure. No other eligible provider implementation is left unfinished inside the frozen22 scope.

Next priority is authentic OEM BTF base recovery and reviewed branch/inventory integration, not repeating audio/modem reconstruction or starting OS deployment. For a later independent source batch, the frozen audit still records `CANDIDATE:device_modules:drivers/clocksource`/timer-mediatek.ko as a one-module D group; verify its live/pending ownership after concurrent assignments before selecting it. NEXT-BATCH.md records the broader source-family selection guard.

STRICT OFFLINE: no phone, ADB, flash, reboot, slots, experimental module loads, firmware/calibration/image edits, Claude checkout edits or push.
