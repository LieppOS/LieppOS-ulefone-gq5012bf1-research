# ST21 firmware loader reconstruction

## Inputs and functions

Active HAL: `runtime-blobs/nfc_nci.st21nfc.st.so`, SHA-256 `7dc795...`.

| Function/symbol | VA | Role |
|---|---:|---|
| `ft_cmd_HwReset` | `0x212a0` | Query controller info, select loader profile/file, compare versions |
| `LdUpdateHandler` | `0x22ef0` | Replay embedded RA7/RA9 loader-patch packets |
| `SendExitLoadMode` | `0x23740` | Exit loader |
| `FwUpdateHandler` | `0x23900` | Read and replay external firmware records |
| `loader_RA7_patch` | `0x8c18`, 24,610 B | 108-packet key/profile-2 loader patch |
| `loader_RA9_patch` | `0xecb4`, 24,610 B | 108-packet key/profile-1 loader patch |

Detailed joint analysis: `firmware-loader-analysis.md`.

## Controller query and parsed fields

Startup sends:

```text
2F 04 05 80 8A 00 00 04
```

`ft_cmd_HwReset` parses the `4F 04` response into device information:

- response offset `0x19`, 4-byte big-endian → `pAuthKeyId` (`ldur`/`rev` at
  `0x215cc-0x215dc`);
- offset `0x0a`, 4-byte big-endian → firmware version;
- offset `0x0e`, 3-byte big-endian → loader version;
- hardware version/revision and loader mode are used in adjacent branch logic.

Observed runtime: AuthKeyId 2, FW `0x01209280`, loader `0x020201`, HW 4/rev 4.

## Profile and file selection

At `0x21ab0-0x21b6c`, AuthKeyId selects embedded loader tables:

- 1 → RA9 (`loader_RA9_patch_AuthKeyId = 01`);
- 2 → RA7 (`loader_RA7_patch_AuthKeyId = 02`).

At `0x21dd0-0x21e24`, default firmware names are selected:

- key 1 → `st54j_fw.bin` (rodata `0x7c30`);
- key 2 → `st21nfc_fw7.bin` (rodata `0x7024`);
- other family defaults include `st21nfc_fw.bin`, `st54l_fw.bin`.

`STNFC_FW_BIN_NAME` may override the filename; default directory is
`/vendor/firmware/`. The first four bytes of the selected file are read as its firmware version.
Version comparison decides whether “FW patch needs to be applied”; loader mode can force
recovery/update paths.

## Record reader / transport

`FwUpdateHandler` records exact file position, then:

```text
fread(buffer, 1, 3, file)              # NCI header
length = buffer[2]
__fread_chk(buffer+3, 1, length, file) # body
HalSendDownstreamTimer(ctx, buffer, length+3, 3000 ms)
```

Disassembly: `0x23e14-0x23e74`, repeated at `0x23fd8-0x24038` and
`0x2444c-0x244ac`. It validates read lengths and controller response status, retries on
failure/timeouts, and stops at EOF. It does **not** decrypt, decompress, hash or verify the
record body.

`LdUpdateHandler` does the same transport from embedded arrays using their 108-byte size
tables. Both RA7/RA9 arrays decode into 108 length-correct `2F 04` packets.

## Loader command families

| Bytes | Function |
|---|---|
| `2F 04 05 80 8A 00 00 04` | controller/loader information query |
| `2F 04 06 80 0C 00 00 01 {01..04}` | loader state transitions |
| `2F 04 07 80 A6 00 00 02 AF {A0,A1}` | erase/loader-area management |
| embedded `80 32`, `80 34`, `80 36`, `80 A8` | loader patch upload |
| `2F 04 06 80 A0 00 00 01 01` | exit loader mode |

See `vendor-command-table.md` for exact call VAs.

## Integrity/authentication and downgrade status

- No host crypto verifier or public-key operation was identified.
- `pAuthKeyId` is **loader key selector** metadata, not proof of host signature verification.
- Opaque payload, `AuthKeyId` names, and 16-byte framing fields strongly suggest controller-side
  transform/authentication, but enforcement and algorithm are **UNKNOWN** without a safe
  mutation test or controller code.
- Version comparison exists; exact anti-rollback/downgrade enforcement inside the controller is
  **UNKNOWN**. Host filename override/readability does not imply controller acceptance.

No destructive loader command was sent during this audit.
