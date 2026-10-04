# FT3680 stock/rebuild parity report

## Compared artifacts

**A — stock**

`workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/focaltech_touch_spi_ft3680.ko`

- SHA-256: `6629ec6148ac361a5f0085b8b19efa9d591426679f58262c4998345f41931162`
- size: 400,936 bytes
- build ID: `35c87682241ccdef19a9b1b24c3240fac26caa5a`

**B — reconstruction**

Private build of `lieppos/disp/ft3680` against GKI `6.1.115-android14-11-g945dff7bc1bf`, clang r487747c, isolated `M=` build and stock-harvested provider CRCs. The proprietary firmware include is available only in that private harness.

## Exact ABI/module axes

| axis | result |
|---|---|
| functions | 166 stock, 166 rebuild; no one-sided functions |
| imports | **105/105 names and modversion CRCs exact** |
| exports | 0/0 |
| `.modinfo` | identity fields/dependency set match |
| `depends=` | `yft_tpd_gesture,mtk_disp_notify,yft_devinfo` |
| KCFI | absent in both |
| data objects | 85/85 total; 82 shared named objects, all shared section/size pairs exact |
| firmware placement | `fw_file` non-const in `.data`, 118,972 bytes |

The one shared data byte mismatch is `____versions`, caused by entry ordering while all 105 name/CRC pairs compare equal. Remaining one-sided data symbols are compiler-generated lock-class `__key.N` names.

## Function results

Raw ELF comparison:

- **126/166 size-identical**
- **67/166 byte-identical**

Address/string-normalised instruction classification (`parity/functions.tsv`):

| class | count | meaning |
|---|---:|---|
| `IDENTICAL` | 69 | normalized instruction+relocation sequence identical |
| `ORDER_ONLY` | 29 | identical instruction and relocation multisets; scheduling/order differs |
| `RELOCS_DIFFER` | 19 | code shape close, data/string/object references differ |
| `OPCODES_DIFFER` | 35 | real instruction-shape difference |
| `CALLS_DIFFER` | 14 | call-boundary or behavior difference remains |

Thus 98/166 functions are normalized-identical or order-only. This is a substantial improvement over the pass-opening 23 raw byte-identical / 105 size-identical result, but it is not full parity.

## Important closures achieved

- Exact 166-function set and exact import ABI/modversions.
- Exact stock-visible `fts_ts_data` offsets through the 0x508 structure end.
- Exact DT parser strings and behavior for `vddi-gpio`, optional `iovcc`, GPIOs and coordinates.
- Exact shared data-object section/size placement, including writable FHP file-operation tables.
- Removal of donor FOD/game/pocket behavior.
- Recovered MediaTek notifier label/callback flow, gesture wake, AOD gate and power sequencing.
- Recovered SPI NULL-command read semantics, firmware-reset detection, ex-mode locking, readiness polling and failure unwinding.

## Remaining size-different functions

Forty functions remain size-different. The complete list and sizes are machine-readable in `parity/functions.tsv`. Main clusters are:

- FHP/FWDBG queue, ioctl and read source shape;
- flash helpers (`fts_dpram_write`, ECC/download/resume/upgrade call boundaries);
- IRQ dispatcher and gesture-report compiler shape;
- SPI allocation/error-epilogue merging;
- probe cleanup/inlining;
- several ESD/mode/helper functions within a few instructions.

Some residuals are proven source-spelling/compiler-inlining differences; others still contain non-identical call or opcode structure. They are not all rigorously reducible to DWARF, relocation order or harmless scheduling.

## Data and relocation caveats

Text/rodata placement changes move many relocation offsets, so whole-section RELA byte comparison is not a behavioral metric here. Use the per-function normalized table. The rebuild also carries DWARF sections absent from stock.

## Status decision

**Remain PARTIAL.** The static hardware contract, ABI, function inventory and core behavior are reconstructed, but 68 functions are outside the normalized-identical/order-only classes. Moving to DONE would overstate evidence without the missing V4.2 source or further instruction-level reconstruction.

Raw reports:

- `parity/focaltech_touch_spi_ft3680.parity.txt`
- `parity/functions.tsv`
- `parity/data.tsv`
