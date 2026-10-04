# Rear display + rear touch (GQ5012BF1)

Coupled subsystem: a 340×340 rear AMOLED driven over SPI by
`spi_tiny_co5300_lcd.ko`, and a Hynitron CST820 I2C touch controller driven by
`hynitron.ko`. The display module owns touch power and wake.

| component | status | headline |
|---|---|---|
| CO5300 rear display (`co5300/`) | **DONE (static)** | A = stock vs B = rebuild: 25/25 size-equal, **24/25 byte-identical**, 25/25 KCFI, 64/64 data section+size (63/64 bytes, `srcversion` only), 58/58 import CRCs, all section sizes equal, B1==B2 reproducible |
| Hynitron rear touch (`hynitron/`) | **DONE (static)** | V2.1 reconstruction: **65/65 byte-identical**, 40/40 data, 258/258 strings, 54/54 import CRCs, 2/2 exports; 41/42 sections equal (build-id only); B1==B2. Old rebuild was 8/65 (RED record kept) |
| integration (`integration.md`) | closed | 2 Hynitron exports consumed by 6 CO5300 call sites; CO5300 owns sequencing |
| userspace (`userspace/`) | boundary mapped | MiniScreen app → services.jar VirtualDisplay → ITinylcd HIDL → `tinylcd.default.so` → ioctl |

- `kernel/module-inventory.tsv`: Phase-1 module inventory
- `hardware/topology.md`: buses, GPIOs, IRQs, rails, geometry
- `yft-rear-display-input-deltas.md`: vendor-specific behavior and stock defects
- `scripts/ko-parity-tsv.py`: explicit-operand parity writer (functions/data/ABI/relocs)
- `scripts/symdis.py`, `scripts/squash.py`: symbolized per-function disassembly and diff helpers

Safety: offline static analysis only. Nothing was loaded and no SPI, I2C, GPIO
or firmware operation was performed.
