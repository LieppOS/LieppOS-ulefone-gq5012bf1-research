# Build reproduction

## Development (quarantined, not deleted)

`/home/armol/kernel-work/display-backlight-g-batch-01/dev` was renamed `quarantined-development` before the proof.

| Run | Inputs | Result |
|---|---|---|
| D1 | audio-only config b826d842 | objects/modules exit 0, but the KDM targets were not linked (the inherited MET engine skipped the KDM modpost when an NKM pin was present). Provider witnesses: 28/31, with 3 cmdq-sec CRC mismatches |
| D2 | + `gq5012bf1-tee.config` (config 67f85473) | 31/31 witnesses exact; KDM link still skipped (engine bug) |
| D3 | engine fix: KDM modpost always runs and its Module.symvers feeds the MET build; manifest NKM path corrected | **8/8 whole-file acceptance, 106/106 ELF mutations** |

Recipe committed as `c0b39b61` with pinned trees: KDM `9e4571fd…`, NKM `6e1e6623…`.

## Independent proof

Bundle `bundles/display-backlight.bundle` (sha256 `4b98dbd229e8ea9b7d8931174cdb8901434378287c0ed0dd9cee46a6c7e5905d`)
was verified. B1 and B2 ran **sequentially**, each:

1. fresh `--no-hardlinks` clone, exact commit, no alternates, `fsck --full`;
2. offline bootstrap from the immutable mirrors;
3. build at JOBS=4, CPUs 0-3, `nice 10`.

| Check | B1 | B2 | B1 vs B2 |
|---|---|---|---|
| object / KDM module / MET core / MET api exits | 0/0/0/0 | 0/0/0/0 | — |
| provider witnesses | 31/31 | 31/31 | identical natural symvers |
| whole-file stock acceptance | 8/8 | 8/8 | same normalized hashes |
| ELF mutation controls | 106/106 | 106/106 | — |
| `.ko` + stripped outputs | 16 | 16 | **16/16 byte-identical** |
| intermediate objects | 155 | 155 | **155/155 byte-identical** |
| vendor `.config` | 67f85473 | 67f85473 | identical |
| joint-extra / MET-api / batch Module.symvers | — | — | identical (path-mapped) |
| assembled KDM / NKM trees | 9e4571fd / 6e1e6623 | same | equal to `reference/` |

Proof metadata is in `evidence/independent-proof/{B1,B2}`. The stock operands were a private read-only copy of the
8 stock files with sha256 verified; canonical stock was never written.
