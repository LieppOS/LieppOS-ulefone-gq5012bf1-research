# ST21 NFC Controller - MIFARE Classic PICC Emulation Research
## Current Findings - Turn Context

### Project Overview
- **Goal**: Determine if ST21 NFC controller/firmware can do MIFARE Classic PICC/card emulation via static reverse engineering
- **Work directory**: `$HOME/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/hardware/nfc/`
- **Output directory**: `analysis/st21-mifare-ce/`

---

### Phase 1: Inventory & Hashing ✅ COMPLETE

**File Inventory:**

| File | Type | Size | SHA256 |
|------|------|------|--------|
| `blobs/libnfc_nci_jni.so` | ELF 64-bit ARM aarch64 executable | 2,536,608 bytes | `b11bdea0ac537778f437810d43133f1f5b9240383c639d308e551a71b921cd8e` |
| `blobs/nfc_nci.st21nfc.st.so` | ELF 64-bit ARM aarch64 shared lib | 159,144 bytes | `7dc795b36ac30139a631ace654cf13beacbfb74487b0b2166a886b3e62196eb0` |
| `blobs/st21nfc_fw7.bin` | data (high entropy) | 211,584 bytes | `458b6b586a14d10e646ce6787c20a3b165fb586b526bb565484d898f5d889d34` |

**Firmware Binary Header (first 80 bytes):**
```
0000: 01 20 92 80  00 00 00 00  2f 04 15 80  4f e8 22 00  (FwVersion=0x01209280)
0020: 4f e8 22 00  00 00 00 00  00 00 00 00  00 00 00 00
0040: 00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00
0060: 00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00
```
- `01 20 92 80` = `FwVersion=0x01209280`
- Pointer fields: `2f 04 15 80`, `4f e8 22 00` (x2)
- Large zeroed region from 0x28-0x7f
- File offset 0x80 is where the payload begins

---

### Phase 2: Firmware Characterization (in progress)

**Entropy Analysis:**
- `st21nfc_fw7.bin`: ~7.98 bits/byte (VERY HIGH, suggests encryption)
- Chunked analysis shows high entropy throughout
- No recognizable signatures, no ASCII strings
- `binwalk` not yet run due to PATH issues

**Strings found in HAL (`nfc_nci.st21nfc.st.so`):**
```
NFC_ST_NCI
HwVersion=0x04
HwRevision=0x04
FwVersion=0x01209280
LoaderVersion=0x020201
CustomerVersion=0x4646
pAuthKeyId=0x00000002
NFA_PROPRIETARY_CFG=05FFFF068A9077FFFF
NFC_ST_NCI_CONFIG=01
```

**Config String Decoding:**
`NFA_PROPRIETARY_CFG=05FFFF068A9077FFFF`
- `05` = NFA_PROPRIETARY_CFG identifier
- `FFFF` = protocol mask for 0x90
- `06` = 6 entries follow
- `8A 90 77 FF FF` = MIFARE Classic listen/poll config for protocol 0x90

---

### Loader/Auth Functions in HAL (`nfc_nci.st21nfc.st.so`)

**Key Function Addresses (in HAL .text, base 0x20000):**

| Function | VA | Description |
|----------|----|-------------|
| `AuthHandler` | 0x252d0 | Main auth handler - checks `mBinData[0x273]`, calls `mBinData[0x290]` or aborts |
| `AuthCheckConfigCommand` | 0x25460 | Checks `mBinData[0x272]`, handles APDU commands |
| `AuthCheckCoreResetNtf` | 0x250d0 | Core reset notification handler |
| `BackToFactoryLoaderIfPossible` | 0x237f0 | Factory loader transition |
| `FwUpdateHandler` | 0x23900 | Firmware update handler |

**AuthHandler Flow:**
```
AuthHandler(void* pCBData, unsigned char* pData, unsigned int* pRetLen):
  1. Check mBinData[0x273] (byte at offset 0x273 from mBinData base)
     - If set (non-zero): call function pointer at mBinData[0x290], return
     - If clear: log error, abort
```

**AuthCheckConfigCommand:**
- Checks `mBinData[0x272]` (byte at offset 0x272)
- If set: skip to next state
- Otherwise: enter APDU command parsing
- Handles: `APDU_EXIT_LOADER_CMD` (0xFF 0xE0 0x00 0x00 0x00)
- On exit: calls `BackToFactoryLoaderIfPossible`

**BackToFactoryLoaderIfPossible:**
- Checks if state is LOADER (state & 0xf == 3)
- If yes: send timer command (param=9, timeout=3000ms)
- If success: send param=8 command, return
- If fail: set HAL state to 1, call I2C recovery

---

### Loader Patch Data in HAL

**RA7 Patch:**
- File offset: 0x0000c1d0
- Size: 72 bytes
- APDU: `FF 00 80 00 44` + 68 bytes binary
- Size tab entry: 0x42201185 (NOT a size - likely CRC/checksum)

**RA9 Patch:**
- File offset: 0x0000c220
- Size: 248 bytes
- APDU: `FF 00 82 00 F4` + 244 bytes binary
- Size tab entry: 0x42201187
- References files: `stnfc_fw7.bin`, `stnfc_fw7.bin`

**Loader Structures:**
```c
loader_patch mLoaderPatches[] = {
    {RA7_PATCH, ..., 0x42201185, RA7_DATA, 72},
    {RA9_PATCH, ..., 0x42201187, RA9_DATA, 248},
};
```

---

### JNI Layer Functions (`libnfc_nci_jni.so`)

**Key Function Addresses:**

| Function | VA | Size | Description |
|----------|----|------|-------------|
| `NfcAdaptation::DownloadFirmware()` | 0x1e0838 | 968B | Firmware download entry point |
| `NfcAdaptation::HalDownloadFirmwareCallback()` | 0x1e0c08 | 828B | Callback for download status |
| `NfcAdaptation::HalDownloadFirmwareDataCallback()` | 0x1e0f44 | 644B | Callback for download data |
| `NfcTag::discoverTechnologies(tNFA_ACTIVATED&)` | 0x14a84 | 3016B | **KEY: Tag discovery** |
| `NfcTag::fillNativeNfcTagMembers5()` | 0x14a488 | 1980B | Tag activation data |
| `nfa_rw_check_mifare_data()` | 0x18c478 | 60B | MIFARE data check |
| `nfa_rw_set_mifare_deactivated()` | 0x18c4b4 | 20B | MIFARE deactivation |
| `crcChecksumCompute()` | 0x18c6f8 | 92B | CRC computation |
| `crcChecksumVerifyIntegrity()` | 0x1e8754 | 1000B | CRC verification |

---

### MIFARE String Found in JNI

**Location:** File offset `0x7dc1a`
**String:** `"%s: Nfc type = 0x%x, do nothing for non ISO_DEP and non Mifare"`

This string appears in a context that checks `Nfc type` and filters out non-ISO_DEP and non-MIFARE tags. This is likely in the discovery/tag handling path.

---

### Proven Runtime Behavior

| Command | Meaning | Response | Status |
|---------|---------|----------|--------|
| `21 00 07 02 04 03 02 90 01 90` | POLL on proto 0x90 | `41 00 01 00` | ✅ SUCCESS |
| `21 00 07 02 04 03 02 90 02 90` | LISTEN on proto 0x90 | `41 00 01 01` | ❌ FAILED |

- Protocol `0x90` = MIFARE Classic (NFC Forum Type 4 mapped)
- POLL works = reader mode works
- LISTEN fails = card emulation NOT enabled by default

---

## Pending Analysis

### Phase 2
- [ ] Run `binwalk blobs/st21nfc_fw7.bin`
- [ ] Complete entropy analysis
- [ ] Determine firmware format (encrypted/compressed/container)

### Phase 3
- [ ] Disassemble `DownloadFirmware()` (0x1e0838) - trace firmware download flow
- [ ] Disassemble `HalDownloadFirmwareCallback()` (0x1e0c08) - check CRC/auth
- [ ] Disassemble `HalDownloadFirmwareDataCallback()` (0x1e0f44) - data delivery path
- [ ] Map auth key usage (pAuthKeyId=0x00000002)

### Phase 4+
- [ ] Vendor NCI enumeration analysis
- [ ] Card emulation path tracing
- [ ] UID/ATQA/SAK configurability
- [ ] Crypto1 capability assessment
- [ ] Patchability assessment

---

## Key Findings So Far

1. **Firmware is encrypted**: st21nfc_fw7.bin has ~7.98 bits/byte entropy, no strings, no signatures
2. **Auth system present**: HAL has multi-stage auth with mBinData state tracking
3. **Loader patches exist**: RA7 (72 bytes) and RA9 (248 bytes) patches for firmware
4. **MIFARE strings in JNI**: Discovery code checks for "Mifare" type tags
5. **Vendor config string**: `05FFFF068A9077FFFF` maps protocol 0x90 to MIFARE
6. **Auth key ID 2**: Firmware download expects auth with key 0x00000002

---

### NEW FINDINGS - Turn 2

#### nfa_rw_check_mifare_data(NFC_HDR*) - 60 bytes (VA 0x18c478)

```asm
  18c478: ldrh w8, [x0, #0x4]     ; Read 16-bit length from NFC_HDR+4
  18c47c: add x8, x0, x8          ; Compute pointer
  18c480: ldrb w9, [x8, #0x8]!    ; Read byte at [ptr+8]
  18c484: and w9, w9, #0xfe       ; Clear LSB (bit 0)
  18c488: cmp w9, #0x60             ; Compare with 0x60
  18c48c: b.ne 18c4b0               ; If not 0x60, return
  ; IF MATCH (byte == 0x60):
  18c490: adrp x9, 0x265000
  18c494: mov w10, #1
  18c498: ldr x9, [x9, #0xb10]    ; Load global ptr from 0x265000+b10
  18c49c: str w10, [x9, #0x44]    ; Set global[0x44] = 1 (MIFARE ACTIVATED?)
  18c4a0: ldr w10, [x8, #0x8]     ; Read data byte
  18c4a4: ldr x8, [x8]            ; Read pointer from data
  18c4a8: str w10, [x9, #0x50]    ; Set global[0x50] = data byte
  18c4ac: str x8, [x9, #0x48]     ; Set global[0x48] = data pointer
```

**Analysis:**
- Checks if `NFC_HDR[4] + pointer[8] & 0xfe == 0x60`
- If `0x60` detected: sets global state at offset 0x44 = 1
- Also stores data byte at global[0x50] and data pointer at global[0x48]
- **0x60 in NFC context = MIFARE Classic SELECT/READ response**
- This function ACTIVATES MIFARE support in the global state

#### nfa_rw_set_mifare_deactivated() - 20 bytes (VA 0x18c4b4)

```asm
  18c4b4: adrp x8, 0x265000
  18c4b8: ldr x8, [x8, #0xb10]    ; Load global ptr
  18c4bc: stur xzr, [x8, #0x4c]   ; Clear global[0x4c]
  18c4c0: stur xzr, [x8, #0x44]   ; Clear global[0x44]
```

**Analysis:**
- Clears global[0x44] = 0 and global[0x4c] = 0
- This is the deactivation counterpart to check_mifare_data
- 0x44 is the "MIFARE activated" flag (set to 1 by check function)
- 0x4c is likely "MIFARE type" or "MIFARE variant" field

#### fillNativeNfcTagMembers5() - 1980 bytes (VA 0x14a488)

Key logic at 0x14a4d4:
```asm
  14a4d4: ldrb w8, [x0, #0xe1]    ; Read byte at JNI object offset 0xe1
  14a4d8: ldrb w10, [x9, #0x6]    ; Read byte from global 0x265000+6
  14a4dc: cmp w10, w8              ; Compare
  14a4e0: b.ne 14a534              ; If different, skip some processing
  14a4e4: log("Should not happen") ; Warning if same
  14a4f8: ldrb w24, [x0, #0xe2]  ; Read byte at JNI object offset 0xe2
  ...
  14a508: blr x8                   ; Call virtual function via vtable
  ...
  14a534: cmp w8, #0x80            ; Check if byte == 0x80 (ISO-DEP?)
  14a538: b.eq 14a548              ; If yes, branch
  14a53c: cmp w8, #0x1             ; Check if byte == 0x1 (NFC-DEP?)
  14a540: b.eq 14a680              ; If yes, branch to different handler
  14a544: cbnz w8, 14a660          ; If non-zero, branch
```

**Analysis:**
- Global 0x265000+0x6 appears to be the last activation state
- JNI object offset 0xe1 contains the current activation state byte
- Function branches based on technology type (0x80=ISO-DEP/T4T, 0x1=NFC-DEP)
- Virtual function calls at 0x14a508 (vtable offset 0x580) and 0x14a524 (vtable offset 0x680)
- These likely handle different tag type processing

#### Critical Global Structure at 0x265000+0xb10

Fields identified:
- `[0x44]` = MIFARE activated flag (0/1)
- `[0x48]` = MIFARE data pointer
- `[0x50]` = MIFARE data byte
- `[0x4c]` = MIFARE variant/type field
- Accessed via: `adrp x8, 0x265000` + `ldr x8, [x8, #0xb10]`

This is likely the NFA (NFC Firmware Abstraction) runtime state structure.

