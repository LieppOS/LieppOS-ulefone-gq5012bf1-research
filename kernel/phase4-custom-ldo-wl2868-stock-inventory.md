# Stock ELF inventory

Oracle: `workspace/phase4-custom-ldo-wl2868/stock-custom-ldo-wl2868.ko`

| Item | Count |
|---|---:|
| Functions | 15 |
| Objects/data symbols | 25 |
| Kernel imports | 27 |
| Exports | 2 |
| MODVERSIONS records | 27 |
| Relocations | 433 |
| Strings | 47 |

Required machine-readable inventories are in `kernel/phase4-custom-ldo-wl2868-{functions,objects,imports,exports,modversions,relocations,strings}.tsv`. Raw section dumps, disassembly, bytes, and the generator are retained under `workspace/phase4-custom-ldo-wl2868/`.

The two exported CRCs are `will_ldo_vout=0x23ec3223` and `will_ldo_en=0xdd9b9ea1`; both use KCFI ID `0x56e5b5a5`.
