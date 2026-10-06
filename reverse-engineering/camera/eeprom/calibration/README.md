# Calibration formats (no per-unit values)

* `layouts/imx989.tsv`, `layouts/s5kjn1.tsv`, `layouts/s5kjn1main2.tsv`, `layouts/ov64b.tsv`: every EEPROM region stock software reads, from both the kernel parser and imgsensor, with offset, length, encoding, checksum, parser, consumer and whether it is mandatory
* `parser-map.tsv`: which config and parser each fitted sensor (and the camera-0 alternates) uses
* `checksum-map.tsv`: **no checksum of any kind** in the stock kernel. The only validation is the header magic `0x77006901` at offset 0, nonzero AWB values, and AF ordering (S2aAf[0] ≤ S2aAf[1])
* `af-boundary.md`: EEPROM 0x76d/0x76b → `S2aAf[0]`/`S2aAf[1]` → HAL `AFInf`/`AFMacro` → lens 0..1023
* `ois-boundary.md`: no OIS calibration read or consumed anywhere

Common ODM format (all fitted modules, header `0x77006901`):

| offset | len | content |
|---|---|---|
| 0x0000 | 4 | header magic |
| 0x000b | 8 | AWB unit gain, u16 LE ×4 (R, B, Gr, Gb) |
| 0x0013 | 8 | AWB golden gain |
| 0x001d | 0x74c | LSC |
| 0x076b / 0x076d | 2 / 2 | AF DACs (macro slot / infinity slot) |
| 0x0771 | 0x5dc | PDAF |
| 0x0d4f… | | imgsensor-owned: imx989 QSC (0xc00); JN1 family 4-cell blocks up to 0x300e |

Per module, the stock kernel enables only these items:

| module | items enabled |
|---|---|
| imx989 | LSC, AWB+AF, PDAF |
| s5kjn1main2 | LSC, AWB+AF, PDAF |
| s5kjn1 | LSC, AWB |
| ov64b (at 0x53) | AF |
