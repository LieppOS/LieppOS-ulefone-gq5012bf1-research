# AOSP/NCI Listen-A and protocol 0x90 fact check

## Scope and reference revisions

- `aosp-reference/system-nfc`: `da3a76b98152d26f44050731be039b629cb9e806` (24Q3 snapshot).
- `aosp-reference/packages-modules-Nfc`: `b01e3991865799e55d095a30a0b86b5f4030b929`.
- Installed mainline JNI: `libnfc_nci_jni.so`, SHA-256 `b11bdea0ac537778f437810d43133f1f5b9240383c639d308e551a71b921cd8e`.

Exact source excerpts are preserved in `evidence/aosp-listen-proprietary-source-excerpts.txt`; installed exported symbols are in `evidence/libnfc-target-symbols.txt`.

## 1. Listen-A infrastructure

**STATIC IMPLEMENTATION:** AOSP has NFC-A listen infrastructure, including a T2T listen discovery mask.

- `libnfc-nci/src/nfa/include/nfa_dm_int.h:341`: `NFA_DM_DISC_MASK_LA_T2T = 0x00020000`.
- `nfa/dm/nfa_dm_discover.cc:252-261`: T1T, T2T, and ISO-DEP masks all produce `NFC_DISCOVERY_TYPE_LISTEN_A`.
- `nfa/dm/nfa_dm_discover.cc:350-400`: `nfa_dm_set_rf_listen_mode_config()` explicitly describes and configures T1T, T2T, ISO-DEP and NFC-DEP Listen-A behavior.
- `nfa/dm/nfa_dm_discover.cc:460-510`: exclusive-RF raw listen configuration accepts Listen-A SENS_RES fields, SEL_RES and NFCID1; a zero platform/SEL configuration is classified as T2T.

This disproves “no T2T/listen-A infrastructure.” It does **not** establish MIFARE Classic emulation: T2T and MIFARE Classic are different protocols.

## 2. Normal NFA card-emulation API

**STATIC IMPLEMENTATION / negative evidence:** the normal `NFA_CeConfigureLocalTag()` path rejects Type 1 and Type 2 local-tag emulation and only starts normal host listening for T3T and ISO-DEP.

- `nfa/ce/nfa_ce_api.cc:116-153`: rejects `NFA_PROTOCOL_MASK_T1T` and `NFA_PROTOCOL_MASK_T2T`; when a protocol mask is present it also rejects a supplied UID.
- `nfa/ce/nfa_ce_act.cc:422-495`: active NDEF card emulation adds only T3T and ISO-DEP discovery masks.

This shows the normal Android/NFA CE API does not expose T1T/T2T or MIFARE Classic local-tag emulation. It does not remove the lower-level DM exclusive Listen-A facility and does not prove controller incapability.

## 3. Standard NCI Listen-A parameter IDs

The prior `0x22-0x27` table is false for these parameters. `src/include/nci_defs.h:508-577` defines:

| Parameter | ID | Length/shape | Standard status |
|---|---:|---|---|
| `LA_BIT_FRAME_SDD` | `0x30` | 1 byte; Byte 1 of SENS_RES | Standard NCI RF configuration |
| `LA_PLATFORM_CONFIG` | `0x31` | 1 byte; Byte 2 of SENS_RES | Standard NCI RF configuration |
| `LA_SEL_INFO` | `0x32` | 1 byte; SEL_RES capability byte | Standard NCI RF configuration |
| `LA_NFCID1` | `0x33` | 0, 4, 7 or 10 bytes, max 10 | Standard NCI RF configuration |
| `LB_SENSB_INFO` | `0x38` | 1 byte | Standard NCI RF configuration |
| `LB_NFCID0` | `0x39` | 4 bytes in generic parameter definition | Standard NCI RF configuration |
| `LB_APPDATA` | `0x3A` | 4 bytes | Standard NCI RF configuration |
| `LB_SFGI` | `0x3B` | 1 byte in the listen config structure | Standard NCI RF configuration |
| `LB_ADC_FO` | `0x3C` | 1 byte | Standard NCI RF configuration |
| `LF_T3T_ID1..16` | `0x40..0x4F` | 10 or 18 bytes depending on NCI version | Standard NCI RF configuration |
| `LF_PROTOCOL` | `0x50` | 1 byte | Standard NCI RF configuration |
| `LF_T3T_PMM` | `0x51` | 8 bytes | Standard NCI RF configuration |
| `LF_T3T_MAX` | `0x52` | controller capability value | Standard NCI RF configuration |
| `LF_T3T_FLAGS2` | `0x53` | 2 bytes | Standard NCI RF configuration |
| `LF_CON_BITR_F` | `0x54` | 1 byte | Standard NCI RF configuration |
| `LF_CON_ADV_FEAT` / `LF_T3T_RD_ALLOWED` | `0x55` | 1 byte | Standard NCI RF configuration |

AOSP calls the two ATQA/SENS_RES bytes `LA_BIT_FRAME_SDD` and `LA_PLATFORM_CONFIG`; there is no single `LA_SENS_RES` TLV in this tree.

## 4. UID, ATQA and SAK implications

**STATIC IMPLEMENTATION:** `tNFA_LISTEN_CFG` (`nfa/include/nfa_api.h:579-600`) exposes:

- `la_bit_frame_sdd` and `la_platform_config`: the two SENS_RES/ATQA bytes;
- `la_sel_info`: the SEL_RES byte used by this NCI configuration model;
- `la_nfcid1_len` and `la_nfcid1[10]`: fixed 4/7/10-byte NFCID1 or length 0 for NFCC choice.

`nfa_dm_set_rf_listen_mode_raw_config()` serializes all four into CORE_SET_CONFIG (`nfa_dm_discover.cc:460-510`). Thus the host stack has a low-level path to request fixed NFCID1 and chosen Listen-A discovery bytes. Controller acceptance of arbitrary values, especially a MIFARE-like `0x08` SEL_RES, is **not proven**.

The ordinary `NFA_CeConfigureLocalTag` API does not expose this path and rejects a UID when a normal local-tag protocol is configured.

## 5. Protocol/interface 0x90

- `vendor_cfg.h:33-34,63-64`: `NCI_PROTOCOL_MIFARE` is the positional `pro_protocol_mfc` byte.
- Device config `blobs/libnfc-hal-st.conf:44-55` sets that byte to `0x90`.
- `nfc_brcm_defs.h:49`: `NCI_INTERFACE_VS_MIFARE` equals `NCI_PROTOCOL_MIFARE`; therefore the configured interface is also `0x90`.
- `nfc_api.h:384,420` aliases these to `NFC_PROTOCOL_MIFARE` and `NFC_INTERFACE_MIFARE`.
- Reader paths use it in `rw_mfc.cc`, `rw_main.cc`, and `NativeNfcTag.cpp`.

The normal default RF interface map is only ISO-DEP and NFC-DEP (`nfc/nfc/nfc_main.cc:63-85`):

```text
04 03 02   protocol ISO-DEP, poll+listen, interface ISO-DEP
05 03 03   protocol NFC-DEP, poll+listen, interface NFC-DEP
```

The MIFARE `0x90` mapping is not part of that default table. The known runtime tests separately prove `90 01 90` is accepted and `90 02 90` is rejected.

## 6. Installed-vs-reference assessment

The installed APEX JNI exports the expected CE, discovery-map and reader-side MIFARE symbols, including `nfa_ce_start_listening`, `NFA_CeConfigureLocalTag`, `NFA_CeSetIsoDepListenTech`, `NFC_DiscoveryMap`, `nci_snd_discover_map_cmd`, `nfa_rw_check_mifare_data` and `RW_Mfc*`. The critical `NativeNfcTag.cpp` string and control flow match the local source. No installed `ce_t2t` symbol was found.

This is strong source-to-binary correspondence for the audited paths, not proof that every installed function is byte-identical to the reference revision.
