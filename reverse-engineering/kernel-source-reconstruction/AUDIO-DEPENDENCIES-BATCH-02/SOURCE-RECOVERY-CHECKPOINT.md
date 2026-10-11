# Source reconstruction checkpoint — ten development-exact modules, not final certification

The frozen22-module batch is still in progress. All21 original audio targets and pending SCP/connectivity scope remain excluded. No canonical classification was changed.

## SLBC recovered and source-built

Maintained source `android_kernel_modules_slbc_ulefone_gq5012bf1` at `9ce9df64536cb58dc3faacc1b84f302a4a36ed46`. Actual ALPS C/headers need no behavior patch. Owned Kbuild-only routes compile `mtk_slbc`:32 functions,15 data objects,34 exports,237 relocations; full stock ELF is identical except GNU20. Source commit and SHA-recorded recovery bundle are preserved. Independent B1/B2 and mutation certification is still pending.

## Nine modem modules recovered and source-built

Maintained source `android_kernel_modules_modem_audio_transport_ulefone_gq5012bf1` at `ed15c4697e4690e02153775453dcd7e31cbc43f5`.

The genuine historical fae67a CCCI source trees equal ALPS5e415e exactly; historical957dac CCMNI/RPS/MDPM component trees equal ALPS too. We recovered the existing C/header/Kbuild rather than rewriting equivalent code. Full component Git tree identities are recorded in the maintained README. Empty `evidence/modem-fae67a-to-alps5e41.patch` is an actual zero-difference result, not an empty report placeholder.

| Module | Functions | Data objects | Whole development stock parity |
|---|---:|---:|---|
| ccci_auxadc |6|19| GNU20 only |
| ccci_ccif |43|31| GNU20 only |
| ccci_dpmaif |222|135| GNU20 only |
| ccci_fsm_scp |17|30| GNU20 only |
| ccci_md_all |370|173| GNU20 only |
| ccci_util_lib |126|142| GNU20 only |
| ccmni |27|22| GNU20 only |
| mtk_mdpm |17|111| GNU20 only |
| rps_perf |1|9| GNU20 only |

Every target was processed individually by the unchanged whole-file verifier, with full function/data/section/import/export CRC/license/KCFI/modinfo/raw-semantic relocation ledgers. Twenty-two required external slots are emitted from genuine compiled provider C after matching CRC/license/namespace/symbol-type/KCFI-prefix evidence; zero witness errors. Provider-only objects are not certified targets.

D1 was a preserved failed routing experiment: the old audit candidate hint pointed to legacy `drivers/gpu/drm/mediatek`, but the actual callback provider is `mediatek_v2`. The corrected D2 builds all nine targets and naturally matches22/22 witnesses. No stock CRC, code or metadata was copied into compilation.

## Next source family

Twelve transitive shared-infrastructure targets remain: DRM/display helpers/panel/notify/sync, LEDs, profiling, DVFS/debug and system DMA heap. Recover the ten genuine historical DRM patches at `../Reverse Engineer - DONE/MEDIATEK-DRM/source/series/` over ALPS5e415e; inspect MTK-DISP-NOTIFY and backlight source before modifying public code. Preserve provenance and any residuals rather than assume historical DONE equals current independent A.

After all22 targets have been processed, independently clone committed source engines, mask only own development recipes/workspaces, perform B1/B2 all-object/raw/stripped/config/symvers proofs and real ELF/audit mutation tests. Until then **newly certified remains0**. Live stock-signature restoration and concurrent-owner completion are integration prerequisites; no phone, push or live audit edit.
