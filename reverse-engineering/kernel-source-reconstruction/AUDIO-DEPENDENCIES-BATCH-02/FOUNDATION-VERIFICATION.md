# Audio foundation verification — preserved, not integrated

Canonical master is `f61ebf03275ba2d3f6aa4f9d5aebe18e12922263`:458 identities/471 occurrences,245 certified/213 remaining. It does **not** contain AUDIO-BATCH-01 or SCP-CONNECTIVITY-BATCH-01. Their genuine committed evidence is available on independent branches; absence from canonical is an integration discrepancy, not missing reconstruction.

## Verified audio foundation

- Research branch `codex/audio-batch-01`, commit `f00bd8af7e6bd4fde4355ae67e8392feab596a80`.
- Maintained audio source `ec57573ca9f48c92b8485137064840025525f23f`; clean source checkout, authentic recovery bundle SHA checked and `git bundle verify` succeeds.
- Existing validator passes against its frozen baseline;21 manifest identities,20 A and one C (`aw883xx_driver`).
- Reran the complete whole-file20-module verifier against actual stock and both existing clean B1/B2 outputs. Both PASS; reports saved here. No audio module was recompiled.
- Independently hashed all21 raw and stripped files from each existing build:42 file pairs byte-identical.
- Independently hashed all220 actual intermediate objects against their manifests and compared B1/B2 identities. Configuration and GKI symvers match byte-for-byte.
- AW883xx C evidence is retained for coverage only. Its implementation/experiments/repository were not modified; Claude owns its closure.
- Copied manifest, parity, dependency, source repository and audit delta records under `evidence/foundation/`. These are provenance snapshots, not newly applied audit rows.

## SCP/connectivity ownership

Research commit `40bfedda097cc33d05eba145fa0c51d6ceb0a07e` records20 targets:17 A,3 C. Source tips: SCP/sensorhub `26507aa653a09f907329795b6c31c6ec1bd694dd`; connectivity `d0b9e10fbb3bb4810de79fda190a4216cec65b00`. Its entire frozen scope is excluded from the new batch, even while canonical still calls those identities G. Bluetooth/BTCVSD is not a reason to duplicate that ownership.

## Stock operand integrity

Inventory research commit `143a6db22434216e815e4a16c5da41a255efed2b` establishes that60 shared canonical system_dlkm copies have lost their721-byte signatures during an earlier in-place dump-section operation. Authentic originals were separately extracted from the SHA-pinned system_dlkm image. The canonical owner has not restored the shared copies.

This task will never repair or normalize the shared inputs. Its private stock set must match every expected identity SHA, obtaining signed originals from the authentic isolated extraction when necessary. Analysis uses read-only Python ELF parsing; no in-place objcopy/strip/dump-section command is permitted on stock. Isolated audit validation and live canonical validation are distinct gates.

Pending audio/SCP results add37 certifications only after separately reviewed integration; current committed total remains245. No new result is credited by this verification.

Safety: strict offline, no phone/firmware/hardware operation, no Claude checkout write, no canonical audit edit, no push.
