# ST/proprietary NCI command emitters

## Scope and caveats

This table separates the active mainline APEX + ST HAL path from the alternative `/system_ext` ST stack. Exact HAL bytes are preserved in:

- `evidence/st-hal-static-command-bytes.txt`
- `evidence/st-hal-command-emitters.disasm.txt`
- `blobs/st21nfc_conf.txt`
- `evidence/alternative-st-jni-vendor-commands.disasm.txt`

`0x2F` is an NCI command header with proprietary GID `0x0F`; responses use `0x4F` and notifications `0x6F`.

## 1. Active ST HAL emitters

| Binary/function | VA / file offset | GID/OID | Exact request or format | When/purpose | Proof | MIFARE-CE relevance |
|---|---|---|---|---|---|---|
| `nfc_nci.st21nfc.st.so`, `hal_wrapper_open` | call VAs `0x1f7d4`, `0x1fb3c`; bytes at `0x8b52` | F/04 | `2F 04 05 80 8A 00 00 04` | Query loader/controller information during startup/update decision | **STATIC IMPLEMENTATION** | Firmware-loader access only |
| same, config reads | data VA/file offsets `0x27ea4/0x26ea4`, `0x27eac/0x26eac`, `0x27eb4/0x26eb4`, `0x27e9c/0x26e9c`, `0x27ebc/0x26ebc` | F/02 | `2F 02 05 03 00 ID 01 00`, IDs `01` NFCC, `02` HW, `08` IOT/interop, `11` test, `14` custom | Read ST configuration blocks | **STATIC IMPLEMENTATION** | No MIFARE CE field identified |
| same, mode set | call VA `0x22ccc`; bytes `0x8b9b` | F/02 | `2F 02 05 06 00 01 02 03` | ST NFC mode/power transition | **STATIC IMPLEMENTATION** | No demonstrated relation |
| same, config-script executor | `hal_wrapper_send_config`; script lines 8-36 | F/02 | `04 00 block_id 01 sub length data...` after F/02 | Writes customer CRC, HW, RF A/B, DPC, UICC, SE, IOT, antenna and NFCC blocks | **CONFIGURED + STATIC IMPLEMENTATION** | Type-A analog tuning only; no PICC/Crypto1 enable field identified |
| same, loader state commands | call VAs `0x23098`, `0x23178`, `0x2325c`, `0x23540`; bytes `0x8ba8..0x8bc3` | F/04 | `2F 04 06 80 0C 00 00 01 {03,04,01,02}` | Loader/update state transitions | **STATIC IMPLEMENTATION** | Patch transport only |
| same, erase/loader management | call VA around `0x236ac`; bytes `0x8bcc`, `0x8bd6` | F/04 | `2F 04 07 80 A6 00 00 02 AF A0` or `... A1 A0` | Selected by loader state; adjacent logs identify flash-loader/area operations | **STATIC IMPLEMENTATION** | Destructive; not a CE command |
| same, exit loader | `SendExitLoadMode` `0x23740`; calls `0x2379c`; bytes `0x8be0` | F/04 | `2F 04 06 80 A0 00 00 01 01` | Exit loader mode/reboot transition | **STATIC IMPLEMENTATION** | No direct relation |
| embedded RA7/RA9 loader patch | RA7 bytes `0x8c18`, size 24,610; size table `0xec3c` | F/04 | first `2F 04 15 80 32 00 00 10 ...`; data packets use `80 34`; terminator `2F 04 06 80 A8 00 00 01 10` | Upload/activate loader patch | **STATIC IMPLEMENTATION** | Enables firmware update, not MIFARE CE by itself |
| same, CORE vendor TLVs | `hal_wrapper_send_core_config_prop` `0x20c80`; config `libnfc-hal-st.conf:154-162` | CORE/02, not GID F | `20 02 13 06 A1 01 1E A2 01 19 80 01 01 08 01 01 11 01 01 19 01 01` | Startup CORE_SET_CONFIG with vendor/standard TLVs | **CONFIGURED + STATIC IMPLEMENTATION** | No MIFARE listen setting established |

### Config block list

`blobs/st21nfc_conf.txt` emits these F/02 write blocks:

| Line | Block | Payload prefix |
|---:|---|---|
| 8, 36 | customer/config CRC | `04 00 06 01 00 08 ... A5A5/4646` |
| 11 | hardware | `04 00 02 01 00 24 ...` |
| 14 | Custom A RF | `04 00 10 01 00 DC ...` |
| 16 | Custom B RF | `04 00 10 01 01 54 ...` |
| 18 | DPC | `04 00 03 01 00 4A ...` |
| 21 | UICC | `04 00 0A 01 00 1A ...` |
| 24 | SE | `04 00 0B 01 00 1A ...` |
| 27 | IOT | `04 00 08 01 00 0C ...` |
| 30 | antenna | `04 00 09 01 00 20 ...` |
| 33 | NFCC | `04 00 01 01 00 05 ...` |

No decoded block field was found that names MIFARE, MFC, PICC, Crypto1, UID, SENS_RES, SEL_RES, or Listen-A emulation. This is **NOT FOUND in the decoded host configuration**, not proof that no undocumented bit exists.

## 2. Active mainline raw vendor-command path

The installed original APEX JNI contains the same machinery represented by local source `NativeNfcManager.cpp:2720-2775`:

```text
NfcAdapter.sendVendorNciMessage(mt,gid,oid,payload)
 -> NfcService
 -> DeviceHost.sendRawVendorCmd
 -> native NFA_SendRawVsCommand
```

The framework API is privileged/flagged and requires `WRITE_SECURE_SETTINGS` (`framework/api/system-current.txt:18`; `NfcAdapter.java:2826-2832`). It constructs any supplied NCI header and payload and waits for the raw response.

Classification: **STATIC IMPLEMENTATION, privilege-gated arbitrary NCI transport**. This is a reachable way for a system/root component to send a *known* safe vendor command; it is not evidence that a MIFARE CE command exists. Unknown commands were not probed.

## 3. Alternative `/system_ext` ST JNI

These functions are statically present in `libstnfc_nci_jni.so` but the library is not proven loaded by the observed active NFC process.

| Function/source label | VA | Exact behavior | Corrected assessment |
|---|---:|---|---|
| Java/native raw vendor command (`nfcManager_nativeSendRawVendorCmd`) | send call `0x13f234` | Builds `[MT|GID, OID, length, payload]`, calls `NFA_SendRawVsCommand`, waits up to 2 s, returns raw GID/OID/payload | **STATIC IMPLEMENTATION**; arbitrary passthrough, not MIFARE-specific |
| `nfcManager_setForceSAK` | start `0x13d750`, send `0x13d7c0` | Sends `2F 0C 02 01 enabled`; the Java signature is `(boolean enabled, int sak)`, but native code stores only `w2 & 1` and never uses the integer SAK argument | **STATIC IMPLEMENTATION**, purpose/name unresolved; does not prove arbitrary SAK control |
| previously called `getForceSAK` | start `0x13f650`, send `0x13f6b8` | Sends `2F 0C 01 00`; logs `NCI_ANDROID_GET_CAPS`/“Failed to get caps” | Prior identification was **FALSE**. This is Android proprietary GET_CAPS, not a Force-SAK query |

OID F/0C is the Android proprietary command family in the matched AOSP (`nci_defs.h:231-251`). Subcommand `0x00` is GET_CAPS and subcommand `0x01` is POWER_SAVING in that reference. The alternative ST method name `setForceSAK` conflicts with that interpretation, so controller semantics of `2F 0C 02 01 x` on this build remain **UNKNOWN**. Since the SAK integer is discarded, the earlier claim that this API can select a MIFARE-like `0x08` SAK is disproven.

## 4. Search result relevant to the core question

- Dedicated ST command enabling MIFARE Classic PICC/Crypto1 listen state: **NOT FOUND**.
- Command configuring arbitrary UID/ATQA/SAK through an ST-specific OID: **NOT FOUND**.
- Privileged arbitrary raw command transport: **STATIC IMPLEMENTATION**.
- Standard lower-level NCI Listen-A config path: documented separately in `aosp-nci-listen-analysis.md`.
- Firmware loader/update commands: **STATIC IMPLEMENTATION**, but their existence alone says nothing about whether a modified image would be accepted.

The result is negative evidence against an exposed hidden HAL feature, not a proof that firmware contains no undocumented capability.
