# ST21 MIFARE Classic PICC/Card-Emulation Re-Audit

## 1. Executive conclusion

# LIKELY UNSUPPORTED

No usable arbitrary MIFARE Classic PICC/card-emulation path is established on the tested
Ulefone Armor 29 Pro Thermal stack.

The strongest evidence is controller-generated: otherwise-identical RF_DISCOVER_MAP tests
accept MIFARE protocol/interface `0x90` in POLL mode and reject it in LISTEN mode. The active
Android stack exposes ISO-DEP/T3T card emulation, contains reader-side MIFARE code, and has no
identified PICC-side Crypto1 or Classic sector-command state machine. Exhaustive host-side
command/config tracing found generic raw vendor transport, F/02 configuration, and F/04 loader
paths, but no Classic-PICC enable command.

The result is not upgraded to **UNSUPPORTED BY THIS FIRMWARE**. The firmware write payload is
opaque, unknown vendor commands were not brute-forced, and an inactive `/system_ext` ST stack
contains a real off-host/UICC “MIFARE route.” That route does not prove a MIFARE-capable secure
element, was not active in the observed process, and cannot provide arbitrary Android-hosted
memory/keys, but it prevents a categorical statement about every possible NFCEE path.

## 2. Known runtime facts

| Fact | Evidence | Level |
|---|---|---|
| ST21NFC AIDL HAL 140-20240525-24W21p0; HW 4/rev 4; FW `0x01209280`; loader `0x020201`; AuthKeyId 2 | startup logs / accepted baseline | **PROVEN RUNTIME** |
| Real MIFARE Classic-compatible card exposed `MifareClassic`, `NfcA`, protocol/type `0x90`; `RW_Mfc*` ran | device tag logs | **PROVEN RUNTIME** |
| CORE_INIT_RSP advertises vendor RF interface `90 00` | startup NCI trace | **CONTROLLER-ADVERTISED** |
| `21 00 07 02 04 03 02 90 01 90` → `41 00 01 00` | `analysis/mifare-090-poll-map-test.txt:396,399` | **PROVEN RUNTIME ACCEPTED** |
| `21 00 07 02 04 03 02 90 02 90` → `41 00 01 01` | `analysis/mifare-090-listen-map-test.txt:401,404` | **PROVEN RUNTIME REJECTED** |

This proves reader support and disproves the normal DH `0x90` Listen mapping. It does not by
itself disprove undocumented commands or independent off-host routing.

## 3. Previous Qwen report audit

The detailed audit is `QWEN-CLAIMS-AUDIT.md`. Major corrections:

- Generic Listen-A/T2T infrastructure does exist.
- Listen-A config IDs are `0x30-0x33`, not `0x22-0x27`.
- `NFA_PROPRIETARY_CFG` is positional, not identifier/mask/count.
- `0x90` is vendor MIFARE protocol/interface, not an NFC Forum Type-4 mapping.
- Type 3 Tag is not NFC-DEP.
- Standard compression signatures do not validate; encryption remains inference.
- AuthKeyId proves a loader profile selector, not that modified firmware is rejected.
- Vendor paths exist, although no dedicated Classic-PICC command was found.
- Low-level source can request custom UID/ATQA/SAK; controller acceptance of arbitrary values is
  not yet runtime-proven.
- Absolute “MIFARE Classic CE unsupported” was broader than the evidence. The corrected
  conclusion is **LIKELY UNSUPPORTED** for a usable arbitrary emulator.

## 4. Actual runtime ST/NFC binary inventory

Authoritative inventory: `runtime-binary-inventory.md`; metadata:
`evidence/runtime-blob-metadata.tsv`.

| Active/runtime-path artifact | Size | SHA-256 |
|---|---:|---|
| `android.hardware.nfc-service-st` | 37,904 | `f5c620cecf32962f31631219a28b5262f9a946b212f012d327aaf706728ac82d` |
| `nfc_nci.st21nfc.st.so` | 162,040 | `7dc795b36ac30139a631ace654cf13beacbfb74487b0b2166a886b3e62196eb0` |
| `android.hardware.nfc-V1-ndk.so` | 76,416 | `7ba4f4d3eec397583bef33524275a9bb168f31bb113cc2f15a4f67b63f03b3a3` |
| original APEX `libnfc_nci_jni.so` | 2,570,616 | `b11bdea0ac537778f437810d43133f1f5b9240383c639d308e551a71b921cd8e` |
| `st21nfc_fw7.bin` | 215,568 | `458b6b586a14d10e646ce6787c20a3b165fb586b526bb565484d898f5d889d34` |

Historical maps prove the APEX JNI path and HAL process. One pre-reboot capture used a temporary
T4T bind-mounted JNI (`1012cd...`); this audit analyzes the immutable/original `b11bde...`
build. HAL `DT_NEEDED` establishes the ST HAL and AIDL library dependencies.

Alternative `/system_ext` artifacts, not shown mapped in the active NFC process:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `libstnfc-nci.so` | 1,889,600 | `ff6be1dd81f12b8bd03e9a2b36d32070777b141448b7503aa25d6623af3f1f2e` |
| `libstnfc_nci_jni.so` | 2,370,288 | `85c5280e7bdd649667333c68b50f48fcb667dc05df64fa106d7bb169c8db08de` |
| `com.st.android.nfc_extensions.jar` | 89,286 | `7e99f4743477360ac53782cc74b5bea2b808b30c0c0c5ae558e51ea59c0e87be` |

Optional `libstnfc-auth.so` is referenced with `dlopen`, but runtime logs report it missing
(`mifare-090-listen-map-test.txt:329`): **PROVEN RUNTIME ABSENT/NOT LOADED**.

## 5. Correct AOSP/NCI Listen-A behavior

Reference source is evidence of host behavior, not automatic proof of controller acceptance.

- `nfa_dm_set_rf_listen_mode_config` includes `NFA_DM_DISC_MASK_LA_T2T`
  (`nfa_dm_discover.cc:347-373`).
- `nfa_dm_set_rf_listen_mode_raw_config` programs Listen-A and classifies neither T1T nor
  ISO-DEP/NFC-DEP as T2T (`:457-503`).
- `NFA_RequestExclusiveRfControl` accepts `tNFA_LISTEN_CFG`, reports activation, and uses
  `NFA_SendRawFrame` (`nfa_api.h:865-901`).
- Ordinary `NFA_CeConfigureLocalTag` rejects T1T/T2T and supplied UID with a normal protocol
  mask (`nfa_ce_api.cc:116-153`). NDEF CE adds only T3T and ISO-DEP
  (`nfa_ce_act.cc:422-495`).

Exact standard parameters:

| ID | Field | Meaning |
|---:|---|---|
| `0x30` | `LA_BIT_FRAME_SDD` | SENS_RES/ATQA byte 1 |
| `0x31` | `LA_PLATFORM_CONFIG` | SENS_RES/ATQA byte 2 |
| `0x32` | `LA_SEL_INFO` | SEL_RES/SAK |
| `0x33` | `LA_NFCID1` | UID, length 0/4/7/10 |

Thus generic NFC-A/T2T listen is real, but it is not Classic and does not supply Crypto1.

## 6. Correct NFA_PROPRIETARY_CFG decoding

Configured bytes: `05 FF FF 06 8A 90 77 FF FF`
(`blobs/libnfc-hal-st.conf:44-55`). Struct/parser evidence:
`vendor_cfg.h:27-40`; `NfcAdaptation.cc:616-636`.

| Offset | Field | Byte | Meaning |
|---:|---|---:|---|
| 0 | `pro_protocol_18092_active` | `05` | 18092 active protocol value |
| 1 | `pro_protocol_b_prime` | `FF` | unsupported B-prime |
| 2 | `pro_protocol_dual` | `FF` | unsupported dual |
| 3 | `pro_protocol_15693` | `06` | ISO15693 value |
| 4 | `pro_protocol_kovio` | `8A` | Kovio protocol |
| 5 | `pro_protocol_mfc` | `90` | MIFARE protocol |
| 6 | `pro_discovery_kovio_poll` | `77` | Kovio poll discovery type |
| 7 | `pro_discovery_b_prime_poll` | `FF` | unsupported |
| 8 | `pro_discovery_b_prime_listen` | `FF` | unsupported |
| 9 | `pro_protocol_chinese_id` | omitted | compiled default retained |

A MIFARE-listen mode, alternate MIFARE-listen protocol, and PICC/Crypto1 enable field are
**NOT FOUND in this structure**.

## 7. Meaning and code paths of protocol/interface 0x90

`vendor_cfg.h:33-34` places `0x90` in `pro_protocol_mfc`; `nfc_brcm_defs.h:49` aliases the
vendor MIFARE interface to the configured protocol; `nfc_api.h:384,420` exports the NFC aliases.

Reader flow:

```text
remote target activated as protocol 0x90
 -> NativeNfcTag::doConnect
 -> choose NFA_INTERFACE_MIFARE (0x90)
 -> reSelect
 -> RW_Mfc authentication/read/write commands
```

The default map contains only `04 03 02` (ISO-DEP) and `05 03 03` (NFC-DEP)
(`nfc_main.cc:63-85`). Runtime proves the additional `90 01 90` poll map works and
`90 02 90` listen map does not. Interface advertisement is therefore evidence of reader
capability, not symmetric listen capability.

## 8. Function containing “non ISO_DEP and non Mifare”

Full reconstruction: `non-isodep-non-mifare-function.md`.

- Binary/string VA: active `libnfc_nci_jni.so`, `0x7dc16`.
- Function: `nativeNfcTag_doConnect`, inferred extent `0x13a4f4-0x13b008`.
- Matched source: `NativeNfcTag.cpp:542-625`.
- At `0x13a970` it compares ISO-DEP `0x04`; at `0x13aa50-0x13aa5c` it loads positional
  `pro_protocol_mfc` and compares the active target protocol.
- MIFARE Classic chooses interface `0x90`; ISO14443-3 A/B generally chooses FRAME; other
  targets choose ISO-DEP or avoid unnecessary reselection.

Classification: **STATIC IMPLEMENTATION — reader-side remote-tag connection handling**. It has
no Listen-A, CE, PICC authentication, or card-side Crypto1 role.

## 9. ST proprietary/vendor NCI commands

The complete evidence table is `vendor-command-table.md`; exact bytes/disassembly are under
`evidence/st-hal-*` and `evidence/alternative-st-jni-vendor-commands.disasm.txt`.

| Binary/function | VA/offset | GID/OID | Request/layout | Purpose | MIFARE-CE result |
|---|---:|---|---|---|---|
| active HAL `hal_wrapper_open` | calls `0x1f7d4`,`0x1fb3c`; bytes `0x8b52` | F/04 | `2F 04 05 80 8A 00 00 04` | loader/controller info | unrelated |
| active HAL config reads | data `0x27e9c-0x27ebc` | F/02 | `2F 02 05 03 00 ID 01 00`, IDs `01,02,08,11,14` | read NFCC/HW/IOT/test/custom blocks | no CE field found |
| active HAL mode set | call `0x22ccc` | F/02 | `2F 02 05 06 00 01 02 03` | power/mode transition | no relation shown |
| active config executor | `hal_wrapper_send_config` | F/02 | `04 00 block 01 sub len data...` | write HW, RF-A/B, DPC, UICC, SE, IOT, antenna, NFCC | no decoded MFC-PICC field |
| active loader states | calls `0x23098`,`0x23178`,`0x2325c`,`0x23540` | F/04 | `2F 04 06 80 0C 00 00 01 {03,04,01,02}` | loader transitions | update only |
| active erase/management | around `0x236ac` | F/04 | `2F 04 07 80 A6 00 00 02 AF {A0,A1} A0` | flash-loader management | destructive; not probed |
| active exit loader | `SendExitLoadMode 0x23740` | F/04 | `2F 04 06 80 A0 00 00 01 01` | exit/reboot | unrelated |
| embedded RA7/RA9 patch | RA7 `0x8c18`, 24,610 B | F/04 | `80 32`, `80 34`, `80 36`, `80 A8` framed records | upload loader patch | no CE implication |
| active core config | `hal_wrapper_send_core_config_prop 0x20c80` | CORE/02 | `20 02 13 06 A1...A2...80...08...11...19...` | startup TLVs | no MFC listen established |
| active APEX raw transport | source `NativeNfcManager.cpp:2720-2775` | caller-selected | arbitrary `[MT/GID,OID,len,payload]` | privileged vendor message | transport, not capability |
| alternative `nativeSendRawVendorCmd` | send `0x13f234` | caller-selected | arbitrary header/payload, 2 s wait | raw vendor transport | inactive |
| alternative `setForceSAK` | `0x13d750-0x13d7c0` | F/0C | `2F 0C 02 01 enabled` | name/semantics conflict with Android OID | ignores supplied SAK integer |
| alternative GET_CAPS | `0x13f650-0x13f6b8` | F/0C | `2F 0C 01 00` | Android proprietary GET_CAPS | not Force-SAK query |

Dedicated ST MIFARE Classic PICC/Crypto1 enable command: **NOT FOUND**. Arbitrary raw transport
is reachable to privileged/root code but does not prove any undocumented command exists.

## 10. Firmware loader protocol

Reconstruction: `firmware-loader.md` and `firmware-loader-analysis.md`.

- `ft_cmd_HwReset` (`nfc_nci.st21nfc.st.so:0x212a0`) queries `2F 04 05 80 8A 00 00 04`,
  parses controller versions/key profile, selects firmware, and compares versions.
- `LdUpdateHandler` (`0x22ef0`) replays one of two embedded 108-packet RA7/RA9 loader patches.
- `FwUpdateHandler` (`0x23900`) saves file position, reads a three-byte NCI header, reads exactly
  `header[2]` body bytes, and sends `length+3` with a 3000 ms timer
  (`0x23e14-0x23e74`, repeated through `0x244ac`).
- `SendExitLoadMode` (`0x23740`) sends the exit command.
- Host code checks read lengths, response status, timeout/retry, and version. It does not decode,
  decompress, hash, or cryptographically verify record payloads.

## 11. pAuthKeyId analysis

`ft_cmd_HwReset` reads four big-endian bytes at loader-info response offset `0x19`
(`0x215cc-0x215dc`). It does not come from the firmware header.

At `0x21ab0-0x21b6c`:

- key 1 selects RA9; exported `loader_RA9_patch_AuthKeyId=01`;
- key 2 selects RA7; exported `loader_RA7_patch_AuthKeyId=02` and this device's
  `st21nfc_fw7.bin`.

Both embedded patches contain 108 valid NCI packets. Final classification:
**loader key/profile selector reported by the controller**. A cryptographic signature role is
not proven; it is not merely unrelated metadata either.

## 12. st21nfc_fw7.bin format

Full grammar and offsets: `firmware-format.md`; parser evidence:
`evidence/firmware-structure.txt`.

```text
file = firmware_version_be32 + 877 NCI records
record = 2F 04 length_u8 payload[length]
```

| Payload subcommand | Count | Meaning/layout |
|---|---:|---|
| `80 88` | 1 | opening 16-byte opaque field |
| `80 32` | 1 | initialization with 16 zero bytes |
| `80 A8` | 4 | select regions `10,11,12,13` |
| `80 34` | 870 | address, data length, opaque write data |
| `80 36` | 1 | closing 16-byte opaque field |

The parser consumes all 215,568 bytes exactly. Write data totals 208,496 bytes across four
regions: 32,640; 65,520; 65,520; and 44,816 bytes. `st21nfc_fw.bin` has identical framing,
addresses and lengths, but zero identical write-data records and only 3.6457% equal bytes.

No decoded `(protocol, allowed modes, interface)` table was recovered; raw map patterns are
absent but non-probative because the payload is opaque.

## 13. Firmware signing/compression/encryption assessment

- `binwalk3`: no recognized signatures (`evidence/binwalk3-firmware.txt`).
- Gzip-looking offsets fail immediately; no valid gzip, zlib, bzip2, XZ, ZIP, ELF or PEM stream
  reaches end-of-stream (`evidence/firmware-signature-validation.txt`).
- Concatenated write-data entropy is 7.999192/7.999207 bits/byte; 4096-byte window means are
  7.9542/7.9558 (`evidence/firmware-entropy-windows.txt`).
- Generic compressors expand the payload.

Classification:

| Property | Result |
|---|---|
| tested standard compression container | **DISPROVEN** |
| opaque/high-entropy controller encoding | **STATIC IMPLEMENTATION** |
| encryption/whitening | **STRONG INFERENCE**, not proof |
| host signature verification | **NOT FOUND** |
| controller-side authentication | **UNKNOWN** |
| exact algorithm/key/signature format | **UNKNOWN** |

The opening/closing 16-byte fields and “AuthKeyId” nomenclature are compatible with
controller authentication but do not prove enforcement.

## 14. NFC-A UID / ATQA / SAK configurability

Detailed results: `nfca-listen-params.md`.

`tNFA_LISTEN_CFG` exposes ATQA's two bytes, one SAK byte, and fixed 4/7/10-byte NFCID1
(`nfa_api.h:582-591`). The raw listen path serializes them to IDs `30-33`
(`nfa_dm_discover.cc:473-502`). Length-zero UID delegates choice to the NFCC; source does not
force random UID when fixed bytes are supplied.

Therefore the host can **request** custom UID/ATQA/SAK (**STATIC IMPLEMENTATION**). This
controller's acceptance/sanitization of arbitrary values, including `SAK=0x08`, is **UNKNOWN**.
The `90 02 90` rejection tests protocol/interface mapping, not `LA_SEL_INFO=08`.

The inactive ST `setForceSAK(boolean,int)` method is not arbitrary SAK control: native code
uses only the boolean and discards the integer.

## 15. Crypto1 reader-side vs PICC-side evidence

`crypto1-analysis.md` classifies every relevant hit.

Reader-side support is concrete. `rw_mfc_authenticate` (`rw_mfc.cc:916-972`) constructs:

```text
AUTH A/B command + block + remote UID[4] + selected six-byte key
```

and sends it through the lower MIFARE interface before remote-sector read/write/format. The
`NativeNfcTag` path and `performHaltPICC` are likewise remote-tag operations.

A Classic PICC would need listen-side AUTH A/B, nonce/PRNG, Crypto1 keystream/parity,
encrypted READ/WRITE/value commands, ACK/NAK short frames, and sector storage. These were
**NOT FOUND** in active host binaries. Generic raw Listen-A proves no encrypted parity,
sub-byte framing, or timing capability. Firmware-internal implementation remains **UNKNOWN**
because payload bytes are opaque and no enable path was found.

## 16. Hidden MIFARE CE path evidence

### Positive evidence

- NFCC advertises vendor interface `0x90` (**CONTROLLER-ADVERTISED**).
- Reader-mode `0x90` works (**PROVEN RUNTIME**).
- Privileged arbitrary vendor-command transport exists (**STATIC IMPLEMENTATION**).
- Firmware/loader paths and opaque proprietary configuration blocks exist.
- Inactive ST `NfcService` exposes `default_mifare_route`; alternative
  `StRoutingManager::updateEeTechRouteSetting` compares that route to NFCEE handles and calls
  `NFA_EeSetDefaultTechRouting` (`libstnfc_nci_jni.so:0x160044-0x160138`); string says
  “Mifare route is UICC” (`evidence/alternative-mifare-offhost-route.txt`).

### Negative evidence

- Controller rejects standard `0x90` LISTEN map while accepting POLL.
- Ordinary CE supports ISO-DEP/T3T, not Classic.
- Active routing programs ISO-DEP/T3T; optional NFCEE feature is T4T and
  `NDEF_NFCEE_ENABLE=0` (`libnfc-hal-st.conf:145-166`).
- No active PICC Crypto1/state machine, dedicated enable command, or decoded config flag was
  found.
- Alternative ST binaries containing extra controls were not runtime-loaded.

### Unresolved evidence

- Off-host technology routing is independent enough that DH RF_DISCOVER_MAP rejection does not
  categorically disprove a UICC/eSE applet path.
- NFCEE IDs `0x81`, `0x82`, `0x10` prove endpoints, not a MIFARE applet.
- No compatible UICC/eSE applet, keys, memory, activation trace, or card-side Crypto1 execution
  was observed.
- Opaque firmware and unknown vendor OIDs cannot be exhaustively ruled out without unsafe
  brute force or controller code.

## 17. Firmware patchability

**Classification: UNKNOWN.**

The host selects a filename (`STNFC_FW_BIN_NAME` can override), parses the four-byte version,
and streams records without a host crypto check. That makes host transport modifiable, but not
necessarily controller acceptance. High-entropy variant-specific payloads, key/profile IDs,
and 16-byte boundary fields suggest a protected controller format. No mutation or downgrade
test was run because loader writes are destructive.

It is therefore not justified to call the image unsigned/raw-patchable, checksum-only,
cryptographically authenticated, or definitely encrypted. Even if authenticity were bypassed,
the encoded payload and absent ISA image currently prevent a credible MIFARE feature patch.

## 18. Proof matrix

| Proposition | Result | Evidence |
|---|---|---|
| MIFARE Classic reader operation | **PROVEN RUNTIME** | real tag/type `0x90`, `RW_Mfc*` |
| Interface `0x90` advertised | **CONTROLLER-ADVERTISED** | CORE_INIT_RSP |
| `0x90` POLL mapping | **PROVEN RUNTIME** | status `00` |
| `0x90` LISTEN mapping | **DISPROVEN** as accepted path | status `01` |
| Generic Listen-A/T2T host infrastructure | **STATIC IMPLEMENTATION** | `nfa_dm_discover.cc:347-503` |
| Normal Android Classic CE API | **NOT FOUND** | CE API/routing audit |
| Fixed UID/ATQA/SAK request path | **STATIC IMPLEMENTATION** | `tNFA_LISTEN_CFG`, IDs `30-33` |
| Arbitrary `SAK=08` accepted by this NFCC | **UNKNOWN** | not tested |
| Active-host PICC Crypto1 | **NOT FOUND** | binary/source classification |
| Dedicated ST Classic-PICC command | **NOT FOUND** | emitter/config audit |
| Raw privileged vendor transport | **STATIC IMPLEMENTATION** | JNI/framework path |
| Alternative off-host MIFARE route | **STATIC IMPLEMENTATION** | alt JNI `0x160044-0x160138` |
| MIFARE-capable UICC/eSE on this phone | **UNKNOWN** | endpoint existence only |
| Standard compressed firmware | **DISPROVEN** | decompressor validation |
| Encrypted/whitened firmware | **STRONG INFERENCE** | entropy/variant comparison |
| Host firmware signature verifier | **NOT FOUND** | loader disassembly |
| Controller rejects modified image | **UNKNOWN** | no mutation test |
| Usable arbitrary Classic emulator | **LIKELY UNSUPPORTED** | combined evidence |

## 19. Single best next runtime experiment

### Reversible exclusive Listen-A test with Classic-like anticollision values

**Do not execute without explicit approval.** Instrument the active AOSP JNI to call
`NFA_RequestExclusiveRfControl` after stopping RF discovery, with polling disabled and:

```c
tNFA_LISTEN_CFG cfg = {};
cfg.la_enable = true;
cfg.la_bit_frame_sdd = 0x04;      // SENS_RES byte 1
cfg.la_platform_config = 0x00;    // SENS_RES byte 2
cfg.la_sel_info = 0x08;           // Classic-like SEL_RES/SAK
cfg.la_nfcid1_len = 4;
cfg.la_nfcid1 = {0xDE,0xAD,0xBE,0xEF};
```

The justified CORE_SET_CONFIG payload generated by the audited serializer should be:

```text
20 02 10 04 30 01 04 31 01 00 32 01 08 33 04 DE AD BE EF
```

Use a second NFC reader/Proxmark to perform REQA/select, record ATQA/UID/SAK, then send one
AUTH-A request (`60 <block> CRC_A`) and record whether the phone receives a raw frame callback.
Do not attempt keys, writes, value operations, vendor commands, or firmware changes.

**Expected interpretations:**

- CORE_SET_CONFIG status nonzero: firmware rejects at least one requested Listen-A value;
  narrow parameters individually only in a separately approved follow-up.
- status zero but reader sees sanitized/default ATQA, UID, or SAK: controller accepts the config
  command but overrides Classic-like values.
- reader sees `04 00`, fixed UID, and `08`, but AUTH is not delivered: custom anticollision is
  possible, but the generic interface does not expose the Classic authentication phase.
- AUTH reaches the host as raw data: a lower-level software-emulation investigation becomes
  justified, but PICC Crypto1, parity/short-frame control, and timing are still unproven.
- Controller autonomously responds to AUTH: unexpectedly strong evidence of hidden PICC-side
  logic; capture the complete exchange without proceeding to writes.

**Rollback/recovery:** call `NFA_ReleaseExclusiveRfControl`; if callbacks stall, disable/re-enable
NFC or restart `com.android.nfc`. CORE listen parameters are runtime configuration and should be
restored by normal NFC initialization. No F/02 persistent block or F/04 loader command is used.

## 20. Final answer to the core question

1. **Does normal Android/AOSP expose MIFARE Classic CE?** No. Normal CE exposes ISO-DEP/T3T;
   Classic reader support is separate.
2. **Does normal RF_DISCOVER_MAP allow `0x90` LISTEN?** No on this controller/firmware; it is
   **PROVEN RUNTIME REJECTED**.
3. **Is there evidence of another ST vendor path?** Yes: generic vendor transport, loader/config
   paths, and an inactive off-host/UICC MIFARE route. No dedicated, active Classic-PICC enable
   path is proven.
4. **Is PICC-side Crypto1 present?** Not in identified active host code. Firmware/NFCEE presence
   is **UNKNOWN**; only reader-side Crypto1 operation is proven.
5. **Can firmware plausibly be patched?** Host transport can be altered, but payload encoding,
   controller authentication, and modification acceptance are unknown. No practical patch is
   currently established.
6. **Is custom-kernel-only implementation realistic?** No. The kernel transports NCI; it cannot
   add a controller RF protocol, Crypto1 timing, encrypted parity, or short-frame support.
   Success would require demonstrated raw-listen primitives plus substantial userspace/NFCC or
   secure-element support, not a kernel change alone.

Final core assessment: **LIKELY UNSUPPORTED for usable arbitrary MIFARE Classic PICC/card
emulation on the present active stack, with a narrow unresolved off-host secure-element path.**
