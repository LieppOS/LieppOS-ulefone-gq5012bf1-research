# Hynitron V2.1: RED → reconstruction → exact closure

## 1. Old false DONE

The original DONE (Phase 4) rested on semantic contracts (DT, I2C, report,
gesture, firmware boundary) plus ABI exactness. The frozen source was a
single-file semantic reconstruction (`hynitron.c`).

## 2. Remeasurement RED (2026-10-04)

A = shipped `hynitron.ko` (`860f2840…51fb6`, "V2.1 20201222"), B = old rebuild,
same toolchain (`parity/before-2026-10-04-semantic-recon/`):

| axis | old |
|---|---|
| functions byte-identical | **8/65** |
| functions size-identical | **9/65** |
| `.text` | **8364 vs 22044 B** |
| `.rodata.str1.1` | 750 vs 10134 B |
| strings reproduced | ~a handful; donors 228/258 by anchor |
| data objects | 40 vs 45, 32 section+size equal |

DONE → PARTIAL. `non-exact-function-classification.tsv` classifies all 57
non-exact old functions: **A source missing 31, B newer/reduced donor
behavior 19, E helper/inline mismatch 7**. C/D/F/G/H: 0 after restoration.
No residual remained a struct or codegen problem once the full source was
restored.

## 3. Reconstruction

Lineage is in `lineage.md`. A multi-file V2.1/V2.2 donor body was restored
(core, i2c, esd, tool_debug, update_firmware, gesture, proximity). The binary
then proved these GQ5012BF1 deltas:

- CST820 config, 340×340, 1 point, protocol A, falling IRQ
- `tiny_tp_power_contorl`/`tiny_tp_gesture_contorl` exports, with
  suspend/resume gated by `tiny_tpgesture_status`
- `yft_set_touch_device_used`, plus `second_touch_fw_version` sprintf in
  `cst8xx_firmware_info`
- `hynitron_fw_grp` with three CST816D/CST816T/CST820 entries
- `hyn_gesture_readdata` brace structure: the MUT_CAP block closes before the
  SEL_CAP block (that last ORDER_ONLY residual was a scope difference)
- a single `MODULE_LICENSE("GPL v2")`, plus `pm_runtime.h` for the `__COUNTER__`
  offset
- 41 `#line` anchors for `HYN_FUNC_EXIT` `__LINE__`
- global `-faddrsig`

Iteration record: it2…it9 in the workspace (`parity.sh`). The final tables are
in `parity/`.

## 4. Final parity (A = stock, B = `source/` rebuilt, debug stripped)

| axis | result |
|---|---|
| functions | **65/65 byte-identical**, 65/65 size, KCFI 65/65 (59 typed, 6 N/A on both), relocations 65/65 |
| data objects | **40/40** section+size+bytes (firmware arrays hash-equal) |
| non-DWARF relocations | 2080/2080 semantic-equal |
| strings | **258/258** at identical offsets (`parity/string-parity.tsv`) |
| imports/CRCs | 54/54, `__versions` order equal |
| exports/CRCs | 2/2 (`0xfcc94fc7`, `0x4e4b7919`) |
| modinfo/vermagic/depends | 9/9 positional-equal |
| sections | 41/42 byte-equal. Only `.note.gnu.build-id` differs (`parity/section-parity.tsv`) |
| reproducibility | B1 == B2 file-identical (two clean builds) |

**Sole residual:** `.note.gnu.build-id` is the SHA-1 of the pre-strip
linked object, including DWARF (absolute source paths, comp_dir). It is build
provenance and cannot be reproduced without the original build path. Every
loadable byte is equal.

## 5. Decision

All DONE criteria are met: complete source, complete function surface, exact
ABI, all strings and data accounted for, protocol/firmware/coupling mapped,
and the residual fully explained. **PARTIAL → DONE.**
