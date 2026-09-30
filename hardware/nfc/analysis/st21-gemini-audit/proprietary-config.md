# `NFA_PROPRIETARY_CFG` byte-for-byte reconstruction

## Result

The device value is:

```text
05 FF FF 06 8A 90 77 FF FF
```

It is a positional byte array copied into `tNFA_PROPRIETARY_CFG`; it is not an identifier/mask/count record.

Evidence:

- Device config and its own field comments: `blobs/libnfc-hal-st.conf:44-55`.
- Struct order: `aosp-reference/packages-modules-Nfc/libnfc-nci/src/include/vendor_cfg.h:27-40`.
- Parser: `aosp-reference/packages-modules-Nfc/libnfc-nci/src/adaptation/NfcAdaptation.cc:616-636`.
- Defaults, including the tenth CI byte: `aosp-reference/packages-modules-Nfc/libnfc-nci/src/nfa/dm/nfa_dm_cfg.cc:100-114`.
- Preserved excerpts: `evidence/aosp-listen-proprietary-source-excerpts.txt`.

## Decoding

| Offset | Field | Current byte | Meaning | Source evidence |
|---:|---|---:|---|---|
| 0 | `pro_protocol_18092_active` | `0x05` | Proprietary numeric protocol value for 18092 active | `vendor_cfg.h:29`; parser `NfcAdaptation.cc:620-621` |
| 1 | `pro_protocol_b_prime` | `0xFF` | B-prime unsupported/invalid | `vendor_cfg.h:30`; parser `:622-623`; config says `0xFF` means unsupported |
| 2 | `pro_protocol_dual` | `0xFF` | Dual protocol unsupported/invalid | `vendor_cfg.h:31`; parser `:624-625` |
| 3 | `pro_protocol_15693` | `0x06` | Proprietary/legacy ISO15693 protocol value | `vendor_cfg.h:32`; parser `:626-627` |
| 4 | `pro_protocol_kovio` | `0x8A` | Kovio protocol value | `vendor_cfg.h:33`; parser `:628` |
| 5 | `pro_protocol_mfc` | `0x90` | MIFARE protocol value | `vendor_cfg.h:34`; parser `:629` |
| 6 | `pro_discovery_kovio_poll` | `0x77` | Poll-Kovio discovery type | `vendor_cfg.h:36`; parser `:630-631` |
| 7 | `pro_discovery_b_prime_poll` | `0xFF` | Poll B-prime unsupported/invalid | `vendor_cfg.h:37`; parser `:632-633` |
| 8 | `pro_discovery_b_prime_listen` | `0xFF` | Listen B-prime unsupported/invalid | `vendor_cfg.h:38`; parser `:634-635` |
| 9 | `pro_protocol_chinese_id` | not supplied | Retains compiled default (`0x84` in this reference) | `vendor_cfg.h:39`; parser only overwrites when size > 9 at `:636`; default `nfa_dm_cfg.cc:111` |

## Relevance to MIFARE Classic listen mode

- The structure defines a MIFARE **protocol number** (`0x90`), not a mode/capability bit.
- It has a vendor Listen-B-prime discovery-type field, but no MIFARE listen field and no alternate MIFARE discovery-type field.
- It does not contain an interface-mode mask or a PICC/Crypto1 enable flag.

Therefore:

```text
MIFARE listen control: NOT FOUND in this structure
alternate proprietary MIFARE listen protocol: NOT FOUND in this structure
vendor MIFARE listen discovery type: NOT FOUND in this structure
```

This conclusion is scoped only to `NFA_PROPRIETARY_CFG`; it says nothing definitive about ST HAL commands or firmware internals.
