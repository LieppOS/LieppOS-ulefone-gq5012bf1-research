# Status: rear display + rear touch (2026-10-04)

## Parity proof axes (kept separate)

| axis | CO5300 | Hynitron |
|---|---|---|
| 1. stock semantic parity | closed; 13 earlier semantic claims corrected from bytes | closed; re-derived from exact source (gesture read and CST8XX ROM handshake corrected) |
| 2. shipped-module binary parity (A = stock, B = rebuild) | 24/25 functions byte-identical, 1 characterized CFG residual; data 63/64 bytes (srcversion); ABI exact | 65/65 functions byte-identical; data 40/40; strings 258/258; ABI exact; only `.note.gnu.build-id` differs |
| 3. clean rebuild reproducibility (B1 vs B2) | all loadable sections equal | B1==B2 file-identical |
| 4. function-surface equality | 25/25 names, sizes, KCFI | 65/65 names, sizes, KCFI (6 N/A both sides) |
| 5. runtime validation | none (offline only) | none (offline only) |

## Remaining

- **CO5300:** the `spidev_sync_write_multi_data` jump-threading/`csel` residual
  (source trigger unidentified, semantics identical); `srcversion` (needs the
  original source text); runtime validation.
- **Hynitron:** DONE (static). Residual: `.note.gnu.build-id` (original build-path DWARF); exact private YFT source checkout not found (reconstruction reproduces it byte-for-byte); runtime validation.
- **Userspace:** the app/framework internals are mapped only at the interface
  level (no decompilation).

## Next target

Backlight / display glue: audit the remaining display PARTIAL components and
close the easiest one statically. Then haptics/LEDs/flashlight.
