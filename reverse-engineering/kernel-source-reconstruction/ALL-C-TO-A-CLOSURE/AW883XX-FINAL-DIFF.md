# AW883XX checkpoint — C, not complete

The latest maintained AUDIO-BATCH-01 reconstruction is the baseline. No speaker,
amplifier, protection, tuning or calibration hardware was operated. Experiments use an
isolated KDM source copy, not the audio owner's active workspace.

The baseline private harness first reproduced the preserved development build exactly.
A dispatch restructuring reduced its diagnostic assembly diff from 420 to 286 lines.
Targeted empty-list/insertion-loop variants and three bounded type grids followed:
15 + 30 + 45 candidates. All grid logs are preserved in `evidence/aw883xx/`.

The best diagnostic candidate combines the empty-list path with `int8_t j,k` and
`uint8_t num`. Its stripped ELF size equals stock (331808 bytes), but this is **not parity**.
A fresh corroborating report (`best-full-parity.txt`) gives:

- 236/236 functions present; 235/236 raw bodies exact.
- `aw883xx_dev_cfg_load`: stock 3560 bytes, candidate 3564 bytes, different instructions.
- 74/74 import names and CRCs equal; export name/license set equal.
- The harness assembly normalization reports 255 differing lines; it removes branch target
  offsets and some relocation labels, so this is a search heuristic, not an acceptance rule.
- Whole-file differences remain far outside GNU20. No promotion, B classification, or
  behavioral-equivalence conclusion is made from file size or the smaller diff.

The residual is in the inlined scene parser, including index-width/sign extension,
dual array-bounds traps, insertion/shift-loop block shape and bool-test code generation.
The grids did not establish that any one declaration type is the real OEM source type.
Explicit empty-list, append/bubble, strict-comparison and count-first variants are not
accepted. Avoid repeating these grids without a new hypothesis.

The diagnostic best source is preserved as `f1-int8_t-uint8_t.c`; it is not substituted
into the accepted maintained audio recipe. `try.sh` documents the exact private build
and normalization method. The full original audio blocker remains relevant.

Next bounded experiment: extract the insertion sort into a helper so the loop's independent
index widths and duplicate bounds-check sites can be tested without changing profile
ordering. Alternatively recover original Awinic v1.7.1 OEM source from an authentic release.
Accept only the full module, including metadata/relocations, under the existing rule.

## Continuation: helper-extracted insertion sort (evidence/aw883xx/helper-probe/)

The recorded next experiment was executed. The inline `j`/`k` loops were moved into
`aw_scene_index_insert()` taking `uint32_t (*)[AW_SCENE_INDEX_MAX]`, which keeps both
array-bound checks and the `<=` stable-before-equal ordering; no profile/protection logic changed.

| Variant | Raw exact functions | `aw883xx_dev_cfg_load` bytes (stock 3560) | Stripped size | Non-GNU20 differing bytes |
|---|---:|---:|---:|---:|
| control (preserved best) | 235/236 | 3564 | 331808 | 114932 |
| helper j:int8 k:int8 | 235/236 | 3564 | 331808 | 115168 |
| helper j:int k:int8 | 235/236 | 3524 | 331744 | 192786 |
| helper j:uint8 k:int8 | 235/236 | 3564 | 331808 | 115158 |
| helper j:int8 k:int | 235/236 | 3544 | 331744 | 193200 |

Data 81/81, import CRCs equal in every case. The helper is always inlined back and does not
change the mismatching function in the stock direction. Hypothesis rejected; AW883XX remains C.
Do not repeat helper/type permutations; the remaining route is an authentic Awinic v1.7.1 source.
