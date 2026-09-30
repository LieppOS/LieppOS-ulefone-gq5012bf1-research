# `st21nfc_fw7.bin` firmware format

## Metadata

| File | Size | SHA-256 | Header |
|---|---:|---|---|
| `st21nfc_fw7.bin` | 215,568 | `458b6b586a14d10e646ce6787c20a3b165fb586b526bb565484d898f5d889d34` | `01 20 92 80` |
| `st21nfc_fw.bin` | 215,568 | `35572928584a9fb090179bd66b528d26cb9cde326be34fe91bd902c1c3aeeb64` | `01 20 92 80` |

`file` reports generic `data`. Head/tail and hash evidence is under `evidence/`.

## Reconstructed grammar

```text
file := firmware_version_be32 record[877]
record := 2F 04 length_u8 payload[length_u8]
payload := 80 subcommand subcommand_fields
```

The parser consumes the entire file exactly with no padding/trailing bytes.

| Subcommand | Count | Layout / interpretation |
|---|---:|---|
| `80 88` | 1 | `80 88 00 00 10 opaque[16]` (opening metadata/auth field) |
| `80 32` | 1 | `80 32 00 00 10 zero[16]` (initialization) |
| `80 A8` | 4 | `80 A8 00 00 01 {10,11,12,13}` (select four regions) |
| `80 34` | 870 | `80 34 addr_be16 data_len_u8 data[data_len]` |
| `80 36` | 1 | `80 36 00 00 10 opaque[16]` (closing commit/auth field) |

Full offsets and records: `evidence/firmware-structure.txt`.

### Write regions (`fw7`; `fw` has identical metadata)

| Region | Records | Data bytes | Addressing |
|---|---:|---:|---|
| 0 (`...10`) | 136 | 32,640 | contiguous 0x8100 through 0xff90+0xf0 |
| 1 (`...11`) | 273 | 65,520 | contiguous 0x0080 through 0xff80+0xf0 |
| 2 (`...12`) | 273 | 65,520 | contiguous 0x0070 through 0xff70+0xf0 |
| 3 (`...13`) | 188 | 44,816 | one gap 0x9b50→0xca00; ends 0xddb0+0x70 |

Total written data: 208,496 bytes. Most NCI records are 248 bytes total: 3-byte header +
245-byte body, whose `80 34` body carries 240 data bytes.

## Comparison of hardware variants

- Record count, NCI headers, subcommands, addresses and data lengths are identical.
- Zero of 870 write-data records are identical.
- `80 88` and `80 36` retain fixed prefixes but their 16-byte fields differ.
- Total byte equality is 7,859/215,568 (3.6457%), mostly deterministic framing plus random
  coincidences.

This is consistent with two transformed, revision-specific builds sharing one flash layout.

## Entropy and compression/signature validation

`evidence/firmware-entropy-windows.txt` records both full-file and extracted write-data values:

- write-data global entropy: 7.999192 (`fw7`), 7.999207 (`fw`);
- 256-byte window mean: ~7.1767 / ~7.1758 bits/byte (finite-sample ceiling effect);
- 4096-byte window mean: 7.9542 / 7.9558 bits/byte.

`binwalk3` reports no signatures (`evidence/binwalk3-firmware.txt`). Manual validation
(`evidence/firmware-signature-validation.txt`):

- stray gzip magics: `fw7@0x276b9`, `fw@0x1dbc6,0x2e1ec`; all fail immediately with unknown
  compression method;
- no bzip2/xz/zip/ELF/PEM magic;
- 166/208 chance-valid zlib headers, zero valid end-of-stream.

Classification:

- “standard compressed container”: **DISPROVEN** for tested formats;
- “opaque/high-entropy controller encoding”: **STATIC IMPLEMENTATION**;
- “encrypted”: **STRONG INFERENCE**, not proven solely by entropy;
- exact encryption/compression/authentication algorithm: **UNKNOWN**.

## Search for RF mapping table

Neither image contains exact `90 01 90`, `90 02 90`, `90 03 90`, default `04 03 02`, or
`05 03 03`. Because write data is opaque, absence is non-probative. No decoded capability table
of `(protocol, allowed modes, interface)` was recovered, and no patch candidate exists.
