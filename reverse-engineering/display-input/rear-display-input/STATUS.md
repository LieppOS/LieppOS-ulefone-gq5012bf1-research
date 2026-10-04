# Status: rear display + rear touch (2026-10-04)

## Parity proof axes (kept separate)

| axis | CO5300 | Hynitron |
|---|---|---|
| 1. stock semantic parity | closed; 13 earlier semantic claims corrected from bytes | closed for the fitted CST820 path (earlier contracts) |
| 2. shipped-module binary parity (A = stock, B = rebuild) | 24/25 functions byte-identical, 1 characterized CFG residual; data 63/64 bytes (srcversion); ABI exact | 8/65 functions byte-identical; ABI exact; not closed |
| 3. clean rebuild reproducibility (B1 vs B2) | all loadable sections equal | not re-measured |
| 4. function-surface equality | 25/25 names, sizes, KCFI | 65/65 names, KCFI 63/65 |
| 5. runtime validation | none (offline only) | none (offline only) |

## Remaining

- **CO5300:** the `spidev_sync_write_multi_data` jump-threading/`csel` residual
  (source trigger unidentified, semantics identical); `srcversion` (needs the
  original source text); runtime validation.
- **Hynitron:** full V2.1 source reconstruction from the identified donor
  family to binary parity; runtime validation.
- **Userspace:** the app/framework internals are mapped only at the interface
  level (no decompilation).

## Next target

Hynitron V2.1 binary-parity reconstruction (donor family identified, method
proven on CO5300). After that: backlight/display glue, then haptics/LEDs/
flashlight.
