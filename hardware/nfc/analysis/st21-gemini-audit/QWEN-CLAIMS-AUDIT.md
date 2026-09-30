# Previous Qwen Claims Audit

This document evaluates only the claims named by the re-audit specification. “Not found” is
scoped to the searched artifacts and is not promoted to proof of silicon incapability.

## 1. “MIFARE Classic PICC/card emulation is NOT supported”

**VERDICT:** **OVERCLAIM**

**EVIDENCE:** The controller rejects the standard DH mapping `90 02 90` with
`41 00 01 01`, while accepting poll mapping `90 01 90` with `41 00 01 00`
(`analysis/mifare-090-{listen,poll}-map-test.txt`). Active AOSP CE exposes ISO-DEP/T3T, not
Classic (`nfa_ce_api.cc:116-153`; `nfa_ce_act.cc:422-495`). No active PICC Crypto1 path was
found. However, the inactive ST JNI implements an off-host `default_mifare_route` to an NFCEE
(`libstnfc_nci_jni.so:0x160044-0x160138`), and opaque controller firmware cannot be exhaustively
excluded.

**CORRECTED STATEMENT:** No usable arbitrary host MIFARE Classic emulator is established, and
the standard `0x90` Listen map is unsupported by this firmware. A separate off-host/UICC path
remains unproven rather than disproven. Overall result: **LIKELY UNSUPPORTED**.

**PROOF LEVEL:** **PROVEN RUNTIME** for standard-map rejection; **NOT FOUND** for active-host
PICC code; **STATIC IMPLEMENTATION/UNKNOWN runtime** for alternative off-host routing.

## 2. “No T2T listen infrastructure exists”

**VERDICT:** **FALSE**

**EVIDENCE:** `NFA_DM_DISC_MASK_LA_T2T` is consumed in
`nfa_dm_set_rf_listen_mode_config` (`nfa_dm_discover.cc:347-373`); raw listen configuration
classifies neither T1T nor ISO-DEP/NFC-DEP as `LA_T2T` (`:457-503`).

**CORRECTED STATEMENT:** Generic NFC-A/T2T listen infrastructure exists. It does not implement
MIFARE Classic or Crypto1.

**PROOF LEVEL:** **STATIC IMPLEMENTATION**.

## 3. “No standard NCI config exists for Type-A/T2T listen”

**VERDICT:** **FALSE**

**EVIDENCE:** Standard NCI parameters `LA_BIT_FRAME_SDD=0x30`,
`LA_PLATFORM_CONFIG=0x31`, `LA_SEL_INFO=0x32`, and `LA_NFCID1=0x33` are defined in
`nci_defs.h:508-511` and serialized by `nfa_dm_discover.cc:473-502` through CORE_SET_CONFIG.

**CORRECTED STATEMENT:** Standard Listen-A configuration exists and can request ATQA, SAK and
NFCID1 through the low-level exclusive-RF path. Ordinary Android HCE does not expose it as a
Classic emulator.

**PROOF LEVEL:** **STATIC IMPLEMENTATION**.

## 4. “0x22-0x27 are the listen config IDs”

**VERDICT:** **FALSE**

**EVIDENCE:** Exact Listen-A IDs are `0x30-0x33` (`nci_defs.h:508-511`); Listen-B begins at
`0x38`, and Listen-F at `0x50`. The source writers agree (`nfa_dm_discover.cc:473-500`).

**CORRECTED STATEMENT:** The relevant standard Listen-A IDs are `30`, `31`, `32`, and `33`.

**PROOF LEVEL:** **DISPROVEN**.

## 5. “NFA_PROPRIETARY_CFG is identifier + protocol mask + entry count”

**VERDICT:** **FALSE**

**EVIDENCE:** `vendor_cfg.h:27-40` defines a positional structure and
`NfcAdaptation.cc:616-636` copies each indexed byte into it. Device bytes are
`05 FF FF 06 8A 90 77 FF FF` (`libnfc-hal-st.conf:44-55`).

**CORRECTED STATEMENT:** Offsets 0-8 are, respectively, 18092-active protocol, B-prime
protocol, dual protocol, ISO15693 protocol, Kovio protocol, MIFARE protocol, poll-Kovio
discovery type, poll-B-prime type, and listen-B-prime type. No MIFARE-listen field exists in
this structure.

**PROOF LEVEL:** **DISPROVEN**; correct layout **CONFIGURED + STATIC IMPLEMENTATION**.

## 6. “0x90 maps to MIFARE Classic in NFC Forum Type 4 mapping”

**VERDICT:** **FALSE**

**EVIDENCE:** Device config sets positional `pro_protocol_mfc=0x90`; reference aliases
`NCI_INTERFACE_VS_MIFARE` to that value (`vendor_cfg.h:33-34`; `nfc_brcm_defs.h:49`). Type 4
uses ISO-DEP protocol `0x04` and ISO-DEP interface `0x02`, visible in default map `04 03 02`
(`nfc_main.cc:63-85`).

**CORRECTED STATEMENT:** `0x90` is the vendor MIFARE reader protocol/interface on this stack.
It is not an NFC Forum Type 4 mapping.

**PROOF LEVEL:** **DISPROVEN**; reader mapping **PROVEN RUNTIME + STATIC IMPLEMENTATION**.

## 7. “T3T is NFC-DEP Mode 3”

**VERDICT:** **FALSE**

**EVIDENCE:** The default RF map independently maps NFC-DEP protocol `0x05` to interface
`0x03`; T3T is the FeliCa/Type-3 card-emulation protocol handled by T3T CE registration.
`RoutingManager::updateDefaultProtocolRoute()` also routes ISO-DEP and T3T as separate protocol
masks.

**CORRECTED STATEMENT:** T3T and NFC-DEP are separate protocols. “Type 3 Tag” does not mean
“NFC-DEP mode 3.”

**PROOF LEVEL:** **DISPROVEN**.

## 8. “Firmware is encrypted/compressed”

**VERDICT:** **OVERCLAIM**

**EVIDENCE:** Both images are complete 877-packet proprietary NCI streams after a four-byte
version. Their 208,496-byte write payloads have global entropy ~7.9992 bits/byte. `binwalk3`
finds no signatures; candidate gzip/zlib offsets fail valid end-of-stream checks; gzip, zlib,
bzip2, XZ, ZIP, ELF and PEM were not validated (`firmware-format.md` and evidence files).

**CORRECTED STATEMENT:** Tested standard compressed-container claims are **DISPROVEN**. The
payload is opaque and high-entropy; encryption/whitening/controller encoding is a **STRONG
INFERENCE**, but the exact transform is **UNKNOWN**.

**PROOF LEVEL:** structure **STATIC IMPLEMENTATION**; standard compression **DISPROVEN**;
encryption **STRONG INFERENCE**.

## 9. “The authentication system blocks firmware modification”

**VERDICT:** **UNPROVEN**

**EVIDENCE:** `ft_cmd_HwReset` parses controller-reported AuthKeyId at response offset `0x19`
(`nfc_nci.st21nfc.st.so:0x215cc-0x215dc`) and selects RA7/key 2 versus RA9/key 1 loader
profiles (`:0x21ab0-0x21b6c`). The HAL replays records without host cryptographic verification
(`FwUpdateHandler:0x23e14-0x244ac`). Opaque 16-byte opening/closing fields could be
controller-authentication data, but acceptance enforcement was not tested.

**CORRECTED STATEMENT:** AuthKeyId is a loader key/profile selector. Controller-side integrity,
authenticity, downgrade policy, and acceptance of modified records are **UNKNOWN**.

**PROOF LEVEL:** selector **STATIC IMPLEMENTATION**; modification blocking **UNKNOWN**.

## 10. “No vendor-specific path exists”

**VERDICT:** **FALSE** as written; **UNPROVEN** if narrowed to a dedicated Classic-PICC command.

**EVIDENCE:** The active HAL emits proprietary F/02 configuration and F/04 loader commands
(`vendor-command-table.md`). The active framework/JNI has privileged arbitrary vendor-NCI
transport (`NativeNfcManager.cpp:2720-2775`). The alternative ST JNI sends F/0C and implements
off-host MIFARE routing. No command specifically enabling Classic PICC/Crypto1 was identified.

**CORRECTED STATEMENT:** Multiple vendor-specific paths exist, but a reachable command that
enables MIFARE Classic PICC emulation was **NOT FOUND**.

**PROOF LEVEL:** vendor paths **STATIC IMPLEMENTATION/CONFIGURED**; dedicated MIFARE-CE command
**NOT FOUND**.

## 11. “Custom UID/ATQA/SAK is impossible”

**VERDICT:** **FALSE** as an absolute claim.

**EVIDENCE:** `tNFA_LISTEN_CFG` exposes the two SENS_RES bytes, SEL_RES, and fixed 4/7/10-byte
NFCID1 (`nfa_api.h:582-591`); `nfa_dm_set_rf_listen_mode_raw_config` serializes them
(`nfa_dm_discover.cc:473-502`). The alternative `setForceSAK` is not proof: its native code
ignores the integer SAK argument and sends only `2F 0C 02 01 <enabled>`
(`libstnfc_nci_jni.so:0x13d750-0x13d7c0`).

**CORRECTED STATEMENT:** A low-level host path can request fixed UID, ATQA and SAK. This
firmware's acceptance of arbitrary values, especially `SAK=0x08`, remains **UNKNOWN**, and
those anticollision values alone do not implement Crypto1.

**PROOF LEVEL:** host request path **STATIC IMPLEMENTATION**; arbitrary controller acceptance
**UNKNOWN**; impossibility **DISPROVEN**.
