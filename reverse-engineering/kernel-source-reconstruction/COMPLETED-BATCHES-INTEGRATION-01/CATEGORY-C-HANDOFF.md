# Six retained C modules — Claude owner handoff, no reconstruction attempted

Exact identity/SHA/partition keys are in COMBINED-MANIFEST.tsv. Source/current parity/blocker statements below are independently rechecked in both original builds against authentic stock. No C→A claim is made. Original detailed experiments and all source commits remain unchanged.

| Module | Source commit | Functions | Data | Remaining obligation |
|---|---|---|---|---|
| aw883xx_driver |ec57573ca9f48c92b8485137064840025525f23f|235/236 exact|86 exact|aw883xx_dev_cfg_load inlined scene-parser codegen:3560 B stock vs3496 B rebuilt|
| cfg80211 |d0b9e10fbb3bb4810de79fda190a4216cec65b00|1435/1435 exact|1998 exact|private OEM split-BTF base|
| mac80211 |d0b9e10fbb3bb4810de79fda190a4216cec65b00|1420/1420 exact|1408 exact|private OEM split-BTF base|
| bluetooth (vendor2df021ea…) |d0b9e10fbb3bb4810de79fda190a4216cec65b00|1257/1257 exact|176 exact|private OEM split-BTF base|
| drm_display_helper |425ffd724462639899a71d3aa57da85b290037fe|199/199 exact|46 exact|private OEM split-BTF base|
| drm_dma_helper |425ffd724462639899a71d3aa57da85b290037fe|19/19 exact|13 exact|private OEM split-BTF base|

## AW883xx

Kernel amplifier interfaces/CRC/KCFI are exact:74 import CRCs and2 export CRCs; no BTF section. The single scene-parser residual is not solved by ABI identity, semantics, a matching srcversion or scene calibration. The preserved source recovers device behavior but doesn't recover stock block/instruction layout. Original AUDIO-BATCH-01/evidence/aw883xx-scene-parser includes18 falsified variants, stock disassembly and harness. Original BLOCKERS.tsv records248/892 normalized instruction differences and the exact pass-1 empty-list/j==32/(u32)j bounds evidence.

Next evidence-backed **owner** experiment: recover authentic private Awinic v1.7.1 lineage or test the existing insertion-sort/helper/int8/uint16 hypothesis under full stock acceptance. That is a handoff of prior evidence, not work performed here. No amplifier firmware, audio routing or calibration was touched.

## Shared native BTF blocker

All five native helpers match every non-BTF/GNU20 byte, including functions, data, imports/exports/CRCs/KCFI, relocation/modinfo/layout. Natural split-BTF strings/header/record structure agree; differing type/name references have bijective mappings. Module-local references demonstrate OEM base **15 additional types/389 string bytes** relative to public GKI12901745. Original base is g945dff7bc1bf OEM vmlinux; generic public base is not interchangeable.

Dependencies/experiments: exact common6b18f0, immutable compiler/config/pahole/public-vmlinux pins, connectivity BTF residual/base census/metadata experiments and shared helper independent/native reports are preserved in their original directories. The old census procedure was unsafe in-place objcopy; values remain evidence but never repeat that command on stock files. Source-only path mapping fixes affect reproducibility, not the unresolved original BTF base.

Next evidence-backed **owner** experiment: locate authentic original OEM vmlinux/BTF or sufficiently complete original source/config lineage, then regenerate split-BTF naturally and accept whole bytes with GNU20 only. Do not copy original BTF, renumber/rewrite type IDs/string offsets, waive BTF, transplant blobs or change fingerprints. Some existing C kernel targets may share this external base dependency; determine by their own evidence, not filename alone.

System bluetooth d2659fb3… is a distinct already-A signed identity and is untouched. Never replace it with the selected vendor binary.

## Concurrency and future successful deltas

Claude's active Category-C worktree/branch/source/build outputs are untouched. These six rows are handed off with full provenance, not independently re-reconstructed. Future owner CAS protects an already valid newer A/B entire identity. A new C proof/source-owner/commit that doesn't match expected fields stops for manual review. Thus this staging integration does not force older C evidence over a future genuine closure.
