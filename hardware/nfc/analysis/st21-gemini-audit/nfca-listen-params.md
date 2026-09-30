# NFC-A listen parameter capabilities

## Standard parameter map

Source: `nci_defs.h:508-577`, `nfa_api.h:582-591`, and
`nfa_dm_discover.cc:347-503`.

| Value | Name | Length | Meaning |
|---:|---|---:|---|
| `0x30` | `LA_BIT_FRAME_SDD` | 1 | Byte 1 of SENS_RES/ATQA |
| `0x31` | `LA_PLATFORM_CONFIG` | 1 | Byte 2 of SENS_RES/ATQA |
| `0x32` | `LA_SEL_INFO` | 1 | SEL_RES/SAK byte |
| `0x33` | `LA_NFCID1` | 0/4/7/10 | NFCID1/UID; length 0 delegates choice to NFCC |

The earlier `0x22-0x27` identification is false. These are standard NCI RF-config
parameters, not ST-proprietary fields.

## Code paths

### Ordinary listen configuration

`nfa_dm_set_rf_listen_mode_config` (`nfa_dm_discover.cc:347-405`) writes:

```text
30 01 04             # SENS_RES byte 1
31 01 <platform>     # 00 normally; 0C for T1T
32 01 <sel_info>     # 00 T2T; bit 0x20 ISO-DEP; bit 0x40 NFC-DEP
```

The source comment says SENS_RES `0x0000` lets firmware use `0x0400`, suitable for ISO-DEP,
T2T and NFC-DEP. This is generic Listen-A infrastructure, not MIFARE Classic.

### Exclusive/raw listen configuration

`NFA_RequestExclusiveRfControl(poll_mask, tNFA_LISTEN_CFG*, ...)` suspends ordinary polling/HCE,
starts discovery from the supplied config, reports activation to a callback, and uses
`NFA_SendRawFrame` for peer data (`nfa_api.h:865-901`).

`nfa_dm_set_rf_listen_mode_raw_config` serializes all four caller-supplied Listen-A values
(`nfa_dm_discover.cc:457-503`). It classifies platform `0x0C` as T1T, SEL_INFO ISO-DEP bit as
T4T, and a configuration with neither as T2T.

## Required questions

1. **Can generic NFC-A listen use fixed NFCID1? — STATIC IMPLEMENTATION: yes.**
   `la_nfcid1_len` accepts 4/7/10 and copies caller bytes. Length 0 means “NFCC will decide”
   (`nfa_api.h:590-591`; serialization at `nfa_dm_discover.cc:498-500`).

2. **Can ATQA/SENS_RES be configured? — STATIC IMPLEMENTATION: host can request both bytes.**
   Fields are serialized at `nfa_dm_discover.cc:473-479`. Controller range/sanitization on this
   firmware has not been runtime-tested.

3. **Can SAK/SEL_RES be configured? — STATIC IMPLEMENTATION: host can request one byte.**
   Serialized at `nfa_dm_discover.cc:481-483`. Acceptance of arbitrary/RFU bit combinations is
   unknown.

4. **Does Android force a random UID? — not in this low-level path.**
   A nonzero valid length supplies a fixed UID; length 0 delegates selection to the NFCC. Whether
   the NFCC chooses random or stable bytes in that case is **UNKNOWN**. Ordinary
   `NFA_CeConfigureLocalTag` rejects a caller UID when a protocol mask is supplied
   (`nfa_ce_api.cc:116-153`), so public/normal HCE does not expose this fixed-UID route.

5. **Can the controller expose non-ISO-DEP SAK values? — source can request them; runtime
   acceptance is UNKNOWN.** A zero SEL_INFO is the normal T2T branch. No safe test here requested
   an arbitrary MIFARE-looking `0x08`.

6. **Does it reject SAK `0x08`? — UNKNOWN.** The observed `90 02 90` rejection concerns the
   entire MIFARE protocol/interface listen mapping, not a CORE_SET_CONFIG `LA_SEL_INFO=08` test.

7. **Are these parameters ISO-DEP/HCE-only? — no.** The exclusive path explicitly classifies
   neither-ISO-DEP-nor-NFC-DEP as T2T and supports a fixed NFCID1. However, generic NFC-A/T2T
   anticollision bytes are insufficient for Classic: no PICC-side Crypto1/authentication/sector
   command state machine is provided by this API.

## Alternative `setForceSAK`

The inactive `/system_ext` JNI method `setForceSAK(boolean enabled, int sak)` sends
`2F 0C 02 01 <enabled>` but never consumes the integer `sak` argument (disassembly
`0x13d750-0x13d7c0`). Therefore it does **not** prove arbitrary SAK control. OID F/0C overlaps
Android proprietary commands, so exact ST controller semantics remain unknown.

## Bottom line

Fixed UID and requested ATQA/SAK are statically available only through lower-level exclusive
Listen-A, not ordinary Android HCE. This can produce generic NFC-A/T2T behavior but supplies no
evidence of Classic PICC authentication. The standard MIFARE interface mapping itself is
runtime rejected in LISTEN mode; arbitrary `0x08` SEL_RES remains a narrower untested question.
