# Firmware image and loader analysis

## Scope

Reconstruct the on-disk firmware format (`st21nfc_fw7.bin`, `st21nfc_fw.bin`), the
embedded loader-patch tables, the `ft_cmd_HwReset` update flow, and assess whether a
modified firmware could be built and accepted — specifically whether any path enables
MIFARE Classic PICC/Crypto1 behaviour.

Raw evidence:

- `evidence/firmware-structure.txt` — full record/framing dump.
- `evidence/fw7.head1024.hex`, `evidence/fw7.tail1024.hex` — byte samples.
- HAL disassembly in `evidence/st-hal-command-emitters.disasm.txt`.

## 1. Container format: a pre-serialized NCI loader stream

Both firmware files are **not** MCU images. They are a byte-for-byte capture of the
proprietary NCI loader command stream that the HAL replays to the controller.

- File size: 215,568 bytes each.
- 4-byte version header `01 20 92 80`, then a contiguous sequence of 877 NCI packets.
- Every packet is `2F 04 <len> 80 <sub> ...` (GID `0x0F` proprietary, OID `0x04` =
  `NCI_PROP_NFC_FW_UPDATE`, then an `80`-prefixed loader subcommand).

Subcommand census (identical in both files):

| Sub | Count | Role |
|---|---:|---|
| `80 88` | 1 | Header/开 metadata record (16-byte opaque field) |
| `80 32` | 1 | Zeroed init record |
| `80 A8` | 4 | Region/area select (`...01 1X`, X = 0..3) |
| `80 34` | 870 | Flash write: `80 34 <addr_hi addr_lo> <n> <n data bytes>` |
| `80 36` | 1 | Trailer/commit record (16-byte opaque field) |

The 870 `80 34` writes carry addresses that are **perfectly contiguous within each of the
four `80 A8` regions** (only one intentional gap in region 3), confirming the address/length
fields parse correctly and the format is fully understood:

| Region (`80 A8 ...01 1X`) | write recs | data bytes | addr span |
|---|---:|---:|---|
| 0x0 | 136 | 32,640 | 0x8100–0xff90 |
| 0x1 | 273 | 65,520 | 0x0080–0xff80 |
| 0x2 | 273 | 65,520 | 0x0070–0xff70 |
| 0x3 | 188 | 44,816 | 0x0060–0xddb0 |

Total payload written = 208,496 bytes.

## 2. Payload is high-entropy/opaque, not plaintext code

- Shannon entropy of the concatenated write payload = **7.9992 bits/byte** (ceiling 8.0).
  Required 256/4096-byte statistics are in `evidence/firmware-entropy-windows.txt`.
- `zlib`/`bzip2`/`xz` all *expand* the payload (ratio > 1.0) — it is incompressible by those
  codecs.
- `binwalk3` finds **no** embedded signatures; no gzip/xz/zip/ELF/PEM containers validate
  (the stray `1f 8b` bytes fail as gzip: "Unknown compression method"). See
  `evidence/binwalk3-firmware.txt` and `evidence/firmware-signature-validation.txt`.
- No plaintext MIFARE/Crypto1/UID/SAK/ATQA byte patterns (`90 01 90`, `04 03 02`, etc.) occur.

**Conclusion (STRONG INFERENCE, not proof):** the flash payload is encrypted, whitened, or
otherwise controller-encoded. High entropy alone does not distinguish encryption from an
unknown compression/packing transform. It is not directly disassemblable or meaningfully
editable from these host artifacts; the HAL performs no decode before transmission.

## 3. The two images differ only in payload + header/trailer tags

Comparing `fw7` vs `fw` (both 215,568 B):

- Identical 4-byte version header, identical packet framing, identical `80 34` addr/len
  metadata for all 870 writes.
- **0 of 870** write-data records are equal; only ~3.6% of total bytes coincide (noise).
- The `80 88` header record and `80 36` trailer record differ **only** in their 16-byte
  opaque fields (5/21 bytes equal = the fixed `2F 04 15 80 88/36 00 00 10` prefix).

This is consistent with two revision-specific transformed builds sharing one write layout.
The differing 16-byte header/trailer fields are plausible integrity/authentication metadata,
MACs, nonces, or transform metadata, but their exact semantics are **UNKNOWN**. There is no
identified plaintext code region to modify.

## 4. Firmware selection (`ft_cmd_HwReset`) and the AuthKeyId

`nfc_nci.st21nfc.st.so :: ft_cmd_HwReset` (`_Z14ft_cmd_HwResetPhS_b`, VA 0x212a0):

1. Sends loader-info query `2F 04 05 80 8A 00 00 04`.
2. Parses the response: offset `0x19` → `pAuthKeyId` (4-byte BE, byte-swapped at 0x215d8),
   offset `0x0a` → firmware version, offset `0x0e` → loader version.
3. Selects the firmware file by chip family:
   - `pAuthKeyId == 1` → `st54j_fw.bin`
   - `pAuthKeyId == 2` → `st21nfc_fw7.bin` (this device) / falls through to `st21nfc_fw.bin`
   - default name string `st21nfc_fw.bin` at rodata 0x6010.
   Config key `STNFC_FW_BIN_NAME` can override the name.

The embedded loader-patch tables corroborate the key mapping directly:

| Symbol | Value |
|---|---|
| `loader_RA7_patch_AuthKeyId` | `0x02` |
| `loader_RA9_patch_AuthKeyId` | `0x01` |
| `loader_RA7_patch_version` | `01 02 02 00` |
| `loader_RA9_patch_version` | `01 03 02 00` |
| `loader_RA7/RA9_patch_cmd_nb` | `0x6C` = 108 (matches decoded record count) |
| `loader_RA7/RA9_patch` size | 24,610 B, 108 NCI packets, all length-consistent |

`pAuthKeyId` is therefore a **key/profile selector reported by the controller**, not a
host-side signature. See `auth-key-id.md`.

## 5. Update flow and likely authentication boundary

`FwUpdateHandler` / `LdUpdateHandler` stream the file's `2F 04` packets downstream verbatim
(`fread`/`__fread_chk` of the 3-byte NCI header then the length-prefixed body via
`HalSendDownstreamTimer`). The host performs:

- **No identified** signature verification, hashing, RSA/ECDSA, or `libcrypto` calls.
- Only structural checks (record length, response status `0x00`, retry/timeout, EOF).

If integrity/authentication is enforced, it must be enforced by the controller/loader, because
the host does not inspect the opaque data. The names `AuthKeyId`, revision-specific key/profile
selection, high-entropy payload and opaque 16-byte framing fields are **strong inference** of
controller-side cryptographic processing, but no modified-record rejection experiment or
algorithm recovery proves it. A checksum-only or unauthenticated controller cannot be excluded
from static host evidence alone.

The optional `libstnfc-auth.so` (hooks `AuthCheckCoreResetNtfImpl`, `AuthHandlerImpl`,
`AuthCheckConfigCommandImpl`) is **absent on this device** (dlopen fails at runtime — see
`runtime-binary-inventory.md`), so even the optional host-side auth layer is not present.

## 6. Patchability verdict

| Question | Finding | Evidence level |
|---|---|---|
| Is the FW a disassemblable MCU image? | No — pre-serialized opaque NCI loader stream | STATIC IMPLEMENTATION |
| Is the flash payload plaintext/editable? | No identified plaintext — entropy 7.999, incompressible, opaque | STATIC IMPLEMENTATION |
| Does the host verify signatures? | No host-side cryptographic verifier identified | STATIC IMPLEMENTATION |
| Does the controller cryptographically authenticate/decode it? | Likely, but not proven by host static analysis | STRONG INFERENCE |
| Can the host inject arbitrary modified FW? | HAL would transport it; controller acceptance is unknown | UNKNOWN |
| Any visible MIFARE/Crypto1/PICC bytes in the image? | None found; opaque encoding makes absence non-probative | NOT FOUND |

**Bottom line:** A modified firmware enabling MIFARE Classic card emulation cannot currently
be crafted from these artifacts: the payload encoding and executable representation are
unknown and no signing/encryption keys or builder are available. Controller-side authentication
is likely but not proven. Nothing about MIFARE PICC/Crypto1 is observable in the image; this is
negative evidence about *feasibility from the host*, not proof that the silicon lacks the
capability internally.
