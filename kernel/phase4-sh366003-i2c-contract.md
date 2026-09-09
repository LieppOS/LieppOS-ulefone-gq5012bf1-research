# SH366003 I2C transaction contract

## Ordinary transport

- Adapter/client: I2C bus 9, 7-bit address 0x55.
- Public telemetry uses `i2c_smbus_read_word_data`; data is SMBus little-endian.
- `fg_read_sbs_word` command descriptors:
  - bit 27: write low 16 bits to SMBus command 0x3e, sleep 3 ms, read word at 0x40;
  - bit 26: write low 16 bits to command 0x00, busy-delay exactly 10 ms, read word at 0x00;
  - otherwise: read direct command low byte.
- `fg_read_block` writes the low 16-bit MAC selector to 0x3e, sleeps 3 ms, then performs raw two-message transfer: one-byte register 0x40 followed by a requested read (normally 2 or 32 bytes).
- All ordinary helper transactions are serialized by the state I/O mutex. Error returns are propagated and caches are preserved.

## AFI interpreter transport

Embedded records carry 8-bit address 0xaa, shifted right to 7-bit 0x55.

- type 2 WRITE: raw one-message transfer of `len` bytes beginning at the embedded register byte; retry once after 50 ms.
- type 3 COMPARE: raw two-message transfer, write one embedded register byte then read `len`; retry once after 50 ms; byte-compare with embedded expected payload.
- type 4 WAIT: `msleep(delay_ms)` where delay is little-endian u16.
- type 1 legacy branch is implemented by stock but absent from this image; it uses a raw write transaction and stock index semantics.

The image fills the full 2,142-byte object with 209 records: 104 writes, 1 compare, 104 waits and 0 legacy reads. There is no separate END record; the interpreter stops at byte offset 0x85e. Maximum embedded write-data length is 34 bytes. Checksums and commit lengths are precomputed in the stream; the driver performs no CRC calculation.

## Retry and delay behavior

- Raw write/compare records: initial attempt plus one retry, 50 ms between.
- MAC word reads/writes: errors are returned; callers commonly retry version reads up to five times.
- Unseal words: 3 ms after each key word.
- MAC selector reads: 3 ms selector-to-read.
- AFI stream: exactly 51 waits of 2 ms, 51 waits of 5 ms, and two waits of 1,500 ms (3,357 ms encoded total).

## High-risk writes

All writes to 0x00, 0x3e or 0x60—including unseal keys, 0x0041 reset, 0x0030 seal, 0x004d manufacture date, and every AFI record—are marked:

`DO_NOT_RUNTIME_TEST`

The development-safe reconstruction compiles the recovered algorithm but rejects programming entry unless `SH366003_ALLOW_AFI_PROGRAMMING=1` is explicitly selected.
