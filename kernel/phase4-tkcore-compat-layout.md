# GQ5012BF1 tkcore 32-bit compat layout

Stock uses **same-size in-place overlays**, not compact alternate ioctl structures. Every compat pointer/`size_t` occupies a low 32-bit value followed by a dedicated high 32-bit word. The converters zero those high words and native code then consumes the result.

## Primary native/compat pairs

### Command ioctl — 48 / 48 bytes

| Semantic field | Native offset/width | Compat offset/width | Conversion |
|---|---:|---:|---|
| `err` | 0x00 / 4 unsigned | same | none |
| `origin` | 0x04 / 4 unsigned | same | none |
| command id | 0x08 / 4 unsigned | same | none |
| session fd | 0x0c / 4 signed | same | none |
| UUID pointer | 0x10 / 8 | low pointer 0x10 / 4 + high 0x14 / 4 | zero high |
| data pointer | 0x18 / 8 | low 0x18 / 4 + high 0x1c / 4 | zero high |
| operation pointer | 0x20 / 8 | low 0x20 / 4 + high 0x24 / 4 | zero high, then copy 8-byte widened pointer |
| data size | 0x28 / 4 unsigned | same | none |
| reserved | 0x2c / 4 signed | same | none |

### SHM ioctl — 24 / 24 bytes

| Field | Native | Compat | Conversion |
|---|---:|---:|---|
| buffer pointer | 0x00 / 8 | low 0 / 4 + high 4 / 4 | zero high |
| size | 0x08 / 4 | same | none |
| flags | 0x0c / 4 | same | none |
| fd | 0x10 / 4 signed | same | none |
| registered | 0x14 / 4 | same | none |

### SPTA compat-only overlay — 24 / 24 bytes

Stock proves only the conversion-relevant shape because native dispatch rejects the command: pointer slots at offsets 0 and 0x10, each with upper word at +4; the eight bytes at 0x08 are opaque and untouched. No field meaning is invented. Conversion zeros offsets 0x04 and 0x14.

## Nested TEEC operation graph

### `TEEC_Operation` — 0x118 / 0x118

| Field | Offset | Native / compat |
|---|---:|---|
| started | 0x00 | u32 / u32 |
| `paramTypes` | 0x04 | u32 / u32 |
| 4 parameters | 0x08 | 4 × 0x18 in both |
| session pointer | 0x68 | native 8; compat low 4 + high at 0x6c |
| 4 embedded shared-memory records | 0x70 | 4 × 0x28 in both |
| flags | 0x110 | u64 / u64 |

The converter zeros the session high word at 0x6c.

### Parameter union — 0x18 / 0x18

| Variant | Native fields | Compat fields / conversion |
|---|---|---|
| value | `a` 0x00 u32, `b` 0x04 u32 | identical; no conversion |
| temporary memref | buffer 0x00/8, size 0x08/8 | low32+high32 for each; zero relative +0x04 and +0x0c |
| registered memref | parent 0x00/8, size 0x08/8, offset 0x10/8 | low32+high32 for each; zero +0x04, +0x0c, +0x14 |

### Compat shared memory reached through a registered memref — 0x28 / 0x28

| Field | Native | Compat | Conversion |
|---|---:|---:|---|
| buffer | 0x00 / 8 | low32 + high at 0x04 | zero high |
| size | 0x08 / 8 | low32 + high at 0x0c | zero high |
| flags | 0x10 / 4 unsigned | same | none |
| reserved | 0x14 / 4 unsigned | same | none |
| fd/pointer union | 0x18 / 8 | low32 + high at 0x1c | zero high |
| registered | 0x20 / 8 unsigned | same | none |

## Parameter-type authority

- types 0–3 (`NONE`, VALUE input/output/inout): no pointer conversion;
- types 5–7 (temporary memrefs): convert temporary buffer+size;
- types 12–15 (whole/partial registered memrefs): convert parent+size+offset, then if parent non-NULL convert that shared-memory object's buffer+size+handle;
- every other nibble logs `bad param <index>` and fails with `-EFAULT`.

## Compiler enforcement

Phase 3C adds assertions for all three primary overlays and the nested compat operation/parameter/shared-memory graph, plus every pointer-high offset the stock converters write. Existing 83 assertions are preserved; no padding is guessed — explicitly unnamed bytes in the rejected SPTA record are recorded as opaque stock bytes.
