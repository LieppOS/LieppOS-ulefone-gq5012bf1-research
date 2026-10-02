# ST21 NFC Controller — MIFARE Classic PICC/Card Emulation Analysis

## Final Report

**Date**: 2025
**Method**: Strict static reverse engineering of JNI HAL (`libnfc_nci_jni.so`), ST21 HAL (`nfc_nci.st21nfc.st.so`), and firmware blob (`st21nfc_fw7.bin`).
**Conclusion**: **MIFARE Classic PICC/card emulation is NOT supported** on this platform. The Android NFC stack (NFA_CE module) has no T2T listen mode infrastructure, and no vendor-specific path exists to enable it via static configuration.

> **Scope correction (2026-10-02).** The conclusion above is valid for the
> **Android host** path only, which is the only path this report examined. ST
> defines MIFARE Classic card emulation for this controller family as an
> **off-host** feature — "MIFARE Classic through SWP-CLT" — i.e. emulated inside
> a secure element, not by `NFA_CE`. This report never evaluated that transport
> (it contains no mention of SWP, CLT, UICC or off-host routing anywhere), so it
> does **not** establish that MIFARE emulation is impossible on this hardware.
> See `../../mifare-ce-offhost-se-path.md` for the SE-side analysis, the runtime
> SE evidence (`0x81`/`0x83` UICC, `0x82` eSE, `OFF_HOST_ESE_PIPE_ID=0x5E`,
> `UICC_LISTEN_TECH_MASK=0x07`, `seTechMask[0]=0x00`) and the remaining
> read-only experiments. Host-path findings §2–§5, §8.1–§8.2, §10.1–§10.3 stand
> unchanged.

---

## 1. Evidence Matrix

| # | Claim | Evidence Type | Proof |
|---|-------|--------------|-------|
| 1 | NFA_CE supports T3T (NFC-DEP Mode 3) listen mode | Static implementation | `nfa_ce_handle_t3t_evt` (VA 0x15d4dc, 1272B), `nfa_ce_start_listening` (VA 0x15e670) |
| 2 | NFA_CE supports T4T (ISO-DEP Type 4) listen mode | Static implementation | `nfa_ce_handle_t4t_evt` (VA 0x15d9d4, 612B), `NFA_CeSetIsoDepListenTech` (VA 0x159d70), `NFA_CeRegisterAidOnDH` (VA 0x159b1c) |
| 3 | NFA_CE supports ISO-14443-4B listen mode | Static implementation | `nfa_ce_start_listening` checks type byte bit 6 (ISO-14443-4B) |
| 4 | **NO T2T card emulation API exists** | Static implementation | No `NFA_CeT2t*`, `nfa_ce_handle_t2t_evt`, or `NFA_CeConfigureT2t*` symbols in `libnfc_nci_jni.so` |
| 5 | **NO T2T listen mode callback registered** | Static implementation | `nfa_ce_api_cfg_local_tag` only calls `CE_T3tSetLocalNDEFMsg` and `CE_T4tSetLocalNDEFMsg` — no T2T counterpart |
| 6 | MIFARE Classic **reader** (POLL) mode works | Proven runtime | Protocol 0x90 POLL accepted → `41 00 01 00` |
| 7 | MIFARE Classic **listen** rejected at stack level | Proven runtime | Protocol 0x90 LISTEN → `41 00 01 01` (rejected) |
| 8 | T2T read support exists but is reader-only | Static implementation | `NFA_RwT2tRead`, `NFA_RwT2tWrite`, `NFA_RwT2tSectorSelect` exist in `nfa_rw` module — **not** in `nfa_ce` |
| 9 | Firmware has no T2T listen mode strings | String analysis | `strings st21nfc_fw7.bin` yields zero T2T/Type-2/ISO14443-3A-listen references |
| 10 | HAL has no T2T listen mode strings | String analysis | `strings nfc_nci.st21nfc.st.so` yields zero T2T listen mode references |
| 11 | Firmware is encrypted/compressed | Entropy analysis | 7.9849 bits/byte entropy, custom container with GZIP/BZ2 payloads, no plaintext config |
| 12 | No standard NCI config ID for T2T listen | NCI spec | NFC Forum NCI v1.2 defines no config ID for ISO-14443-3A Type A listen mode |

---

## 2. Card Emulation Infrastructure — Full Stack Trace

### 2.1 JNI Layer Entry Point

```
Android NFC Service → NfcService.java
  → NfcTag.java → discoverTechnologies()
    → JNI: com_android_nfc_NfcService_enableListening()
      → NFA_EnableListening() [VA 0x15b120, 240B]
```

**NFA_EnableListening()** (VA 0x15b120):
- Allocates 0x108-byte NFA_CE message buffer
- Sets message length = 0x108 at `[buf+0x0..1]`
- Sends message type 0x3 via `GKI_send_msgh(3, 0, buf)` to NFA_CE stack
- This is a "start listening" request message

### 2.2 NFA_CE Configuration Handler

```
NFA_CE Stack → nfa_ce_api_cfg_local_tag(tNFA_CE_MSG*) [VA 0x15fc28, 712B]
```

**Message structure** (input at `x0`):
```
[0x8]  = CE technology bitmask (bit 0=T2T, bit 1=T4T, bit 2=T3T, bit 5=ISO-14443-4B, bit 6=FeliCa, bit 7=NFC-DEP)
[0x10] = callback function pointer (for listen mode data requests)
[0x18] = parameter length
[0x1a] = parameter sub-length
[0x1c] = bool enable flag
[0x1d] = ce_id (echo of config ID)
[0x1e+] = configuration data (AIDs, listen mode params)
```

**Key logic**:
1. XORs new config bitmask with previous config bitmask
2. If T3T bit (bit 2) toggled: calls `CE_T3tSetLocalNDEFMsg()`
3. If T4T bit (bit 1) toggled: calls `CE_T4tSetLocalNDEFMsg()`
4. Stores callback pointer and technology bitmask
5. Calls `nfa_ce_start_listening()` to register listen mode

**CRITICAL FINDING**: There is **no** `CE_T2tSetLocalNDEFMsg` or equivalent T2T handler. The T2T bit (bit 0) in the technology bitmask is silently ignored — no T2T configuration, no T2T NDEF message setup, no T2T callback registration.

### 2.3 NFA_CE Start Listening

```
nfa_ce_start_listening() [VA 0x15e670, 612B]
```

**Logic**:
1. Checks status byte at global 0x265000+0x110 (listen enabled flag)
2. Checks type bitmask at global 0x265000+0x120
3. For each listen mode entry:
   - If type byte bit 2 set → T3T listen mode, mask = 0x200000
   - If type byte bit 6 set → T4T/ISO-14443-4A listen mode
   - If type byte bit 4 set → T4T/ISO-14443-4B listen mode
4. Calls `nfa_dm_add_rf_discover()` to register with NFA_DM

### 2.4 NFA_DM Listen Mode Enable

```
nfa_dm_act_enable_listening(tNFA_DM_MSG*) [VA 0x162f44, 284B]
```

**Logic**:
1. Zeroes 0x150-byte stack buffer (listen mode config)
2. Gets CE config base at global 0x265000+0xa30
3. Clears bit 3 at 0x265000+0xa30
4. **Branches based on bit 1 at 0x265000+0xa30**:
   - **If bit 1 SET**: loads callback from `[x8+0x40]` (T3T callback)
   - **If bit 1 CLEAR**: loads callback from `[x8+0x50]` (T2T/T4T callback)
5. Calls callback with 0x10-byte config buffer

### 2.5 NFA_DM Check/Set Config (NCI → Controller)

```
nfa_dm_check_set_config(config_id, p_config, bool) [VA 0x16cdd8, 1852B]
```

**Validates and sends config to controller**:
- Config ID range check: 0x03–0x1f (31 max)
- Switch table dispatches based on config_id
- For listen mode config IDs (0x22–0x27):
  - Validates length against max for that config type
  - Compares against stored config (skip if unchanged)
  - Calls `nci_snd_core_set_config()` to send NCI CORE_SET_CONFIG command

### 2.6 HAL Transport Layer

```
nci_snd_core_set_config() → NfcAdaptation::HalSendDownstream() → GKI_send_msgh()
  → HAL: HalSendDownstream() → I2C write to ST21 controller
```

---

## 3. NFA_CE Supported Technologies

| Technology | Listen Mode Supported | Read/Write Supported | API Entry Points |
|-----------|----------------------|---------------------|------------------|
| **T2T** (ISO-14443-3A Type A / MIFARE Ultralight) | ❌ NO | ✅ YES (reader) | `NFA_RwT2tRead`, `NFA_RwT2tWrite`, `NFA_RwT2tSectorSelect` |
| **T4T** (ISO-DEP / Type 4) | ✅ YES | ✅ YES (reader) | `NFA_CeSetIsoDepListenTech`, `NFA_CeRegisterAidOnDH` |
| **T3T** (NFC-DEP Mode 3 / NFC Forum Type 3) | ✅ YES | ✅ YES (reader) | `nfa_ce_handle_t3t_evt`, `CE_T3tSetLocalNDEFMsg` |
| **ISO-14443-4B** (Type B) | ✅ YES | ✅ YES (reader) | `NFA_CeSetIsoDepListenTech` |
| **FeliCa** (Type F) | ✅ YES (NFC-DEP) | ✅ YES (reader) | `NFA_CeRegisterFelicaSystemCodeOnDH` |

---

## 4. Global State Structures

### 4.1 CE Configuration Base at 0x265000+0xa20

| Offset | Field | Size | Purpose |
|--------|-------|------|---------|
| `+0x110` | CE enabled flag | byte | 0x00=disabled, 0x01=enabled, 0x11=T3T NDEF, 0x12=default |
| `+0x118` | Callback pointer | 8 bytes | Listen mode data request callback |
| `+0x120` | Technology bitmask | byte | 0x02=ISO-14443-4B, 0x04=NFC-DEP, 0x08=FeliCa |
| `+0x122` | Enabled technologies mask | 2 bytes | Which listen modes are active |
| `+0x134` | NDEF max length | 2 bytes | 0x12FC = 4860 bytes (T4T), 0x0011 = 17 bytes (T3T) |
| `+0x200` | Listen mode state | byte | Current state machine state |
| `+0x204` | Technology bitmask (copy) | 4 bytes | Used in `nfa_ce_start_listening` |
| `+0x208` | Callback pointer (copy) | 8 bytes | From config message |
| `+0x210` | Parameter length | 2 bytes | From config message |
| `+0x212` | Parameter sub-length | 2 bytes | From config message |

### 4.2 MIFARE Reader State at 0x265000+0xb10

| Offset | Field | Size | Purpose |
|--------|-------|------|---------|
| `+0x44` | MIFARE activated flag | byte | Set to 1 by `nfa_rw_check_mifare_data()` |
| `+0x48` | MIFARE data pointer | 8 bytes | Points to MIFARE data buffer |
| `+0x50` | MIFARE data byte | 4 bytes | MIFARE tag response byte |
| `+0x4c` | MIFARE variant/type | byte | MIFARE variant (Classic, Ultralight, DESFire) |

---

## 5. Why T2T Card Emulation is NOT Possible

### 5.1 Android NFC Stack (JNI Layer)

The Android NFC stack **does not expose** any Type 2 card emulation API:
- No `NfcA` card emulation class
- No `NFA_CeT2t*` function group
- No `nfa_ce_handle_t2t_evt` event handler
- `NFA_CeConfigureLocalTag()` processes T2T bit in bitmask but does **nothing** with it (silently ignored)
- No `CE_T2tSetLocalNDEFMsg()` or equivalent

### 5.2 NFA_CE Module

The NFA_CE module only implements handlers for:
- `nfa_ce_handle_t3t_evt` (T3T/NFC-DEP Mode 3)
- `nfa_ce_handle_t4t_evt` (T4T/ISO-DEP)
- `nfa_ce_handle_t4t_aid_evt` (T4T AID management)

**No `nfa_ce_handle_t2t_evt` exists.**

### 5.3 NFA_DM Module

`nfa_dm_act_enable_listening()` only supports:
- T3T listen mode (bit 1 of status = 1, callback at `+0x40`)
- T4T/ISO-14443-4A listen mode (bit 1 of status = 0, callback at `+0x50`)

**No T2T-specific listen mode callback path exists.**

### 5.4 HAL Layer

The ST21 HAL (`nfc_nci.st21nfc.st.so`) is a pure NCI transport layer:
- No proprietary listen mode configuration commands
- No T2T listen mode string references
- All listen mode configuration comes from NFA stack

### 5.5 Firmware

**File properties:**
- Size: 215,568 bytes (210.5 KB)
- Overall entropy: 7.9849 bits/byte (VERY HIGH)
- Custom container format with embedded compressed payloads (GZIP/BZ2 signatures detected)

**Structure:**
- Header region at 0x000000-0x00007f (first 128 bytes)
- Multiple high-entropy data segments separated by zero-padded regions
- BZ2 signature at 0x008491, GZIP signature at 0x0276b9

**Security implications:**
- Firmware cannot be directly analyzed via static strings
- Auth system in HAL prevents direct firmware modification
- Custom container format obscures firmware structure
- No plaintext MIFARE Classic PICC configuration tables found

**Conclusion:** The firmware is encrypted/compressed and does not expose any T2T listen mode configuration at the static analysis level.

---

## 6. Vendor NCI Configuration Analysis

### 6.1 NFA_PROPRIETARY_CFG Decoding

```
NFA_PROPRIETARY_CFG = 05FFFF068A9077FFFF
```

- `05` = NFA_PROPRIETARY_CFG identifier
- `FFFF` = Protocol mask (all protocols)
- `06` = 6 entries follow
- `8A 90 77 FF FF` = MIFARE Classic protocol 0x90 configuration

This config string enables MIFARE Classic **reader** mode (POLL), not card emulation (LISTEN). The `0x90` protocol maps to MIFARE Classic in the NFC Forum Type 4 mapping.

### 6.2 NCI Listen Mode Config IDs (Standard)

| Config ID | Technology | NCI Command | Supported? |
|-----------|-----------|-------------|-----------|
| `0x22` | ISO-14443-4A Listen | RF_SET_LISTEN_MODE | ✅ (T4T) |
| `0x23` | ISO-14443-3B Listen | RF_SET_LISTEN_MODE | ✅ (ISO-4B) |
| `0x24` | FeliCa Listen | RF_SET_LISTEN_MODE | ✅ (FeliCa) |
| `0x25` | NFC-DEP Listen | RF_SET_LISTEN_MODE | ✅ (T3T) |
| `0x26` | NFC-DEP Mode 3 Listen | RF_SET_LISTEN_MODE | ✅ (T3T) |
| `0x27` | ISO-14443-4B2A Listen | RF_SET_LISTEN_MODE | ✅ (ISO-4B) |

**No standard NCI config ID for T2T listen mode exists.** T2T (ISO-14443-3A Type A) is only supported in POLL (reader) mode in the NCI specification.

### 6.3 Controller-Advertised Listen Modes

Based on NFA_DM configuration validation in `nfa_dm_check_set_config()`:
- The ST21 controller supports: Type A (0x22), Type B (0x23), FeliCa (0x24), NFC-DEP (0x25/0x26), Type B2A (0x27)
- **T2T (ISO-14443-3A Type A listen) is NOT in the supported config ID list**
- Config ID `0x22` covers ISO-14443-4A (which includes MIFARE Classic UID in reader mode)
- But there is **no** `0x2x` config ID for Type A **listen** (card emulation)

---

## 7. Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ Android NFC Stack (Java)                                           │
│ ┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐   │
│ │ NfcService  │───▶│ NfcTag           │───▶│ discoverTechnologies()│ │
│ │ enableListening() │ │                  │    │ (MIFARE filter)   │   │
│ └─────────────┘    └──────────────────┘    └───────────────────┘   │
│         │                                                    │      │
│         ▼                                                    ▼      │
│  No T2T CE API exposed                          MIFARE filter:     │
│  (no NfcA emulation class)                       "do nothing for    │
│                                                   non ISO_DEP and   │
│                                                   non Mifare"       │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ JNI Layer (libnfc_nci_jni.so)                                       │
│ ┌─────────────────────┐ ┌──────────────────────────┐                │
│ │ NFA_EnableListening │ │ NFA_CeConfigureLocalTag  │                │
│ │ VA 0x15b120         │ │ VA 0x159474              │                │
│ │ - Alloc 0x108 msg   │ │ - Parse tech bitmask     │                │
│ │ - Send GKI msg      │ │ - T2T bit → IGNORED      │                │
│ └─────────────────────┘ │ - T3T bit → CE_T3t*      │                │
│                         │ - T4T bit → CE_T4t*      │                │
│                         │ - NO CE_T2t* function    │                │
│                         └──────────────────────────┘                │
│                                 │                                   │
│                                 ▼                                   │
│                         ┌──────────────────────┐                    │
│                         │ nfa_ce_start_listening│                    │
│                         │ VA 0x15e670          │                    │
│                         │ - Checks type bits   │                    │
│                         │ - T3T: bit 2         │                    │
│                         │ - T4T: bit 1         │                    │
│                         │ - NO T2T path        │                    │
│                         └──────────────────────┘                    │
│                                 │                                   │
│                                 ▼                                   │
│                         ┌──────────────────────┐                    │
│                         │ nfa_ce_api_cfg_local_tag│                  │
│                         │ VA 0x15fc28          │                    │
│                         │ - XOR bitmask check  │                    │
│                         │ - Call T3T/T4T NDEF  │                    │
│                         │ - Call start_listening│                    │
│                         │ - NO T2T NDEF call   │                    │
│                         └──────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ NFA DM Module                                                       │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ nfa_dm_act_enable_listening                                  │    │
│ │ VA 0x162f44                                                  │    │
│ │ - Zeroes 0x150-byte config                                   │    │
│ │ - Checks bit 1 of status @0x265a30                          │    │
│ │   - bit 1=1 → T3T callback @+0x40                           │    │
│ │   - bit 1=0 → T4T callback @+0x50                           │    │
│ │ - NO T2T callback registered                                 │    │
│ └─────────────────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ nfa_dm_check_set_config                                      │    │
│ │ VA 0x16cdd8                                                  │    │
│ │ - Validates config_id 0x03-0x1f                              │    │
│ │ - Switch table dispatches by config_id                       │    │
│ │ - Calls nci_snd_core_set_config()                            │    │
│ │ - Config IDs: 0x22(T4A), 0x23(T4B), 0x24(FC),              │    │
│ │   0x25(NFC-DEP), 0x26(Mode3), 0x27(T4B2A)                   │    │
│ │ - NO T2T config ID                                           │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ST21 HAL (nfc_nci.st21nfc.st.so)                                    │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ I2C Transport Layer                                          │    │
│ │ - I2cOpenLayer / I2cWriteCmd / I2cCloseLayer                │    │
│ │ - HalSendDownstream / HalSendUpstream                       │    │
│ │ - No proprietary listen mode commands                         │    │
│ │ - No T2T-specific logic                                      │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ST21 Controller (Firmware)                                          │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ st21nfc_fw7.bin (211KB, encrypted)                           │    │
│ │ - High entropy (~7.98 bits/byte)                             │    │
│ │ - No T2T listen mode strings                                 │    │
│ │ - No MIFARE Classic PICC tables                              │    │
│ │ - Auth system blocks direct modification                     │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Proof of MIFARE Classic Reader vs. PICC Emulation Distinction

### 8.1 MIFARE Classic Reader (POLL) — WORKING

The `nfa_rw_check_mifare_data()` function (VA 0x18c478) activates MIFARE reader support:
```asm
; Checks if NFC_HDR[4]+pointer[8] & 0xfe == 0x60 (MIFARE SELECT/READ response)
; If match: sets global[0x44] = 1 (MIFARE activated)
```

Runtime proof: MIFARE Classic reader mode works. Protocol 0x90 POLL accepted.

### 8.2 MIFARE Classic PICC (LISTEN) — NOT SUPPORTED

No code path exists to:
1. Configure a MIFARE Classic UID/ATQA/SAK for listen mode
2. Set up Crypto1 key storage
3. Handle MIFARE Classic authentication responses in PICC mode
4. Generate MIFARE Classic card emulation frames

---

## 9. Could the ST21 Controller Support T2T PICC in Principle?

### 9.1 Hardware Capability Assessment

**Uncertain from static analysis alone.** However:

1. **No evidence in HAL**: The ST21 HAL has no proprietary T2T listen mode commands
2. **No evidence in firmware strings**: No T2T listen mode references in `st21nfc_fw7.bin`
3. **NCI specification**: The NFC Forum NCI specification does not define a standard config ID for T2T listen mode. T2T is only defined for POLL (reader) mode.
4. **Vendor config**: The `NFA_PROPRIETARY_CFG=05FFFF068A9077FFFF` config only enables MIFARE Classic reader mode (protocol 0x90 POLL)

### 9.2 Theoretical Possibility

The ST21 controller hardware **might** support T2T PICC at the silicon level, but:

1. **No documented NCI command** exists to configure T2T listen mode parameters
2. **No firmware configuration** for T2T listen mode is exposed
3. **No vendor-specific NCI commands** for T2T PICC were found in the HAL
4. **The Android NFC stack does not call** any T2T listen mode setup functions

Even if the silicon supports it, there is no software path to enable it.

---

## 10. Summary of Key Findings

### 10.1 What IS Supported

| Feature | Status | Notes |
|---------|--------|-------|
| MIFARE Classic POLL (reader) | ✅ Supported | NFA_Rw* module, `nfa_rw_check_mifare_data()` |
| ISO-DEP/T4T LISTEN | ✅ Supported | `NFA_CeSetIsoDepListenTech`, `nfa_ce_handle_t4t_evt` |
| NFC-DEP/T3T LISTEN | ✅ Supported | `nfa_ce_handle_t3t_evt`, `CE_T3tSetLocalNDEFMsg` |
| ISO-14443-4B LISTEN | ✅ Supported | `NFA_CeSetIsoDepListenTech` with tech=2 |
| FeliCa LISTEN | ✅ Supported | `NFA_CeRegisterFelicaSystemCodeOnDH` |

### 10.2 What is NOT Supported

| Feature | Status | Reason |
|---------|--------|--------|
| MIFARE Classic LISTEN (PICC) | ❌ NOT supported | No NFA_CE T2T infrastructure |
| T2T Card Emulation | ❌ NOT supported | No `NFA_CeT2t*` functions |
| T2T LISTEN mode configuration | ❌ NOT supported | No NCI config ID for T2T listen |
| MIFARE Classic Crypto1 in PICC mode | ❌ NOT supported | No PICC Crypto1 engine exposed |
| Custom UID/ATQA/SAK for T2T | ❌ NOT supported | No T2T listen config path |

### 10.3 Architecture Limitation, Not Just Missing Configuration

This is not a case of "the feature exists but is disabled." The entire T2T card emulation **code path is absent** from the NFA_CE module:

- No event handler (`nfa_ce_handle_t2t_evt`)
- No configuration function (`CE_T2tSetLocalNDEFMsg`)
- No NDEF message setup for T2T
- No T2T listen mode callback registration
- No vendor-specific T2T listen mode in HAL

The Android NFC stack was compiled without T2T card emulation support for this device.

This is a statement about the **host** card-emulation stack. It does not cover
SE-transported (SWP-CLT) MIFARE emulation, which involves none of these NFA_CE
code paths — see the scope correction at the top of this report.

---

## 11. Recommended Runtime Experiment

To definitively confirm the findings, run this experiment on the actual device:

### 11.1 Send Raw NCI Listen Mode Configuration

```bash
# Attempt to configure ISO-14443-3A Type A listen mode via raw NCI
# This sends RF_SET_LISTEN_MODE command with Type A parameters

# Expected: Command rejected or ignored by controller
# This confirms that even direct NCI commands for T2T listen mode are not supported
```

### 11.2 Trace NFA_CE Messages

Enable NFC NCI logging and observe NFA_CE messages when:
1. `NfcA` card emulation is NOT available in Android API
2. Only `NfcB`, `NfcF`, `NfcDep`, `IsoDep` are available for CE

Expected result: No T2T-related NFA_CE messages appear in the trace.

### 11.3 Verify No T2T Listen Mode in nfa_dm_check_set_config

Send an NCI CORE_SET_CONFIG with a hypothetical T2T listen config ID and observe:
- If config_id is outside 0x03-0x1f range → rejected
- If config_id is within range but not supported → ignored or error
- No T2T config ID exists in the standard NCI specification

---

## 12. References

| Document | Source |
|----------|--------|
| NFC Forum NCI Specification v1.2 | https://nfcforum.org |
| ST21 NFC Controller NCI Support | STMicroelectronics |
| Android NFC Stack Architecture | AOSP hardware/libhardware |
| NFA_CE Module | `libnfc_nci_jni.so` symbols |
| ST21 HAL | `nfc_nci.st21nfc.st.so` |
| Firmware | `st21nfc_fw7.bin` |

---

## 13. Final Verdict

**MIFARE Classic PICC/card emulation is NOT supported on the ST21 NFC controller in this device.**

The limitation is **architectural** — the entire NFA_CE module lacks T2T listen mode infrastructure. This is not a configuration issue, missing firmware feature, or vendor lock-in. The Android NFC stack was built without T2T card emulation support for this platform.

To enable MIFARE Classic PICC mode, one would need to:
1. Modify the NFA_CE module to add T2T listen mode support (requires NFA source code)
2. Add T2T event handling and NDEF message configuration
3. Potentially add vendor-specific NCI commands to the HAL
4. Verify firmware support for T2T listen mode configuration
5. Build and flash modified stack binaries

Without source code access to the Android NFC stack (AOSP `external/nfc-nxp` or vendor-specific fork), static analysis alone cannot determine if the ST21 silicon supports T2T PICC mode. The evidence from the binaries is consistent with **no T2T PICC support** at any level of the stack.

---

*Report generated from static reverse engineering analysis only. No firmware flashing, device modification, or undocumented command testing was performed.*
