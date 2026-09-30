# Investigation of `pAuthKeyId = 0x00000002`

## 1. Executive Summary

- **Final Classification**: `loader key selector` / `authentication metadata only` (Host Userspace).
- **Previous Claim**: Qwen claimed that `pAuthKeyId=0x00000002` proves host-level firmware signing and blocks firmware modifications.
- **Finding**: In the host HAL stack (`nfc_nci.st21nfc.st.so`), `pAuthKeyId` is a **hardware chip family / loader profile selector** returned by the ST controller. It selects between:
  - Key ID `0x00000001` -> ST54J family (`st54j_fw.bin`, `loader_RA9`)
  - Key ID `0x00000002` -> ST21NFC family (`st21nfc_fw7.bin`, `loader_RA7`)
- The Android HAL stack performs **zero** cryptographic signature verification, public key checks, or hashing. It acts purely as a transport pipe streaming NCI `2F 04` commands to the controller.

---

## 2. Where `pAuthKeyId` is Populated

In `nfc_nci.st21nfc.st.so`, during `ft_cmd_HwReset`:
1. The HAL sends the proprietary loader query command:
   ```text
   Tx: 2F 04 05 80 8A 00 00 04
   ```
2. The controller responds with loader and chip information:
   ```text
   Rx: 4F 04 ... [offset 0x19: 4 bytes big-endian key ID]
   ```
3. At VA `0x215cc`–`0x215dc`, the HAL parses this field:
   ```asm
   215cc: b8419269     ldur    w9, [x19, #0x19]     ; load 4 bytes from response offset 0x19
   215d8: 5ac00929     rev     w9, w9               ; byte-swap big-endian to little-endian
   215dc: b9000549     str     w9, [x10, #0x4]      ; store into dev_info->pAuthKeyId
   ```
4. The HAL logs this value at VA `0x215f0`:
   ```asm
   215f0: adrp    x2, 0x7000
   215f4: add     x2, x2, #0x2fd                   ; "   pAuthKeyId = 0x%08X\n"
   215fc: ldr     w3, [x8, #0x4]                   ; dev_info->pAuthKeyId (0x00000002)
   21600: bl      __android_log_print
   ```

---

## 3. Where `pAuthKeyId` is Read & Used

In `ft_cmd_HwReset`, `pAuthKeyId` is evaluated at lines `0x21ab0` and `0x21dd0`:

```asm
; Check chip family / key profile
21ab0: ldr     w9, [x8, #0x4]                       ; load pAuthKeyId
21ab4: cmp     w9, #0x2                             ; Is it ST21 family (Key ID 2)?
21ab8: b.eq    0x21afc                              ; Use ST21 loader profile / RA7
21abc: cmp     w9, #0x1                             ; Is it ST54J family (Key ID 1)?
21ac0: b.ne    0x21b70

; Select default binary name if not overridden in config
21dd0: ldr     w9, [x9, #0x4]
21dd4: cmp     w9, #0x1
21dd8: b.ne    0x21e08
21ddc: adrp    x22, 0x7000
21de0: add     x22, x22, #0xc30                     ; "st54j_fw.bin"

21de8: ldr     w9, [x9, #0x4]
21df4: cmp     w9, #0x2
21df8: b.ne    0x21e08
21dfc: adrp    x22, 0x7000
21e00: add     x22, x22, #0x24                      ; "st21nfc_fw7.bin"
```

---

## 4. Evidence Matrix

| Question | Finding | Evidence Level | Details |
|---|---|---|---|
| Populated from? | NFCC response offset `0x19` | **STATIC IMPLEMENTATION** | Disassembly at `0x215cc` |
| Read by? | HAL firmware loader selection logic | **STATIC IMPLEMENTATION** | Disassembly at `0x21ab0`, `0x21dd0` |
| Host signature check? | **NONE** | **STATIC IMPLEMENTATION** | No crypto library calls (`libcrypto`, RSA, ECDSA) in HAL |
| Chip family mapping | `1` = `st54j_fw.bin`, `2` = `st21nfc_fw7.bin` | **STATIC IMPLEMENTATION** | String references at `0x7c30` & `0x7024` |
| Embedded tables | `loader_RA9` (key 1), `loader_RA7` (key 2) | **STATIC IMPLEMENTATION** | Exported symbols in `nfc_nci.st21nfc.st.so` |

---

## 4b. Embedded loader-patch tables corroborate the mapping

The HAL exports two loader-patch blobs whose own `AuthKeyId` bytes match the runtime field,
independently confirming the profile mapping (data read directly from `.data.rel.ro`):

| Symbol | Bytes | Meaning |
|---|---|---|
| `loader_RA7_patch_AuthKeyId` | `02` | ST21 family key id |
| `loader_RA9_patch_AuthKeyId` | `01` | ST54J family key id |
| `loader_RA7_patch_version` | `01 02 02 00` | RA7 patch version |
| `loader_RA9_patch_version` | `01 03 02 00` | RA9 patch version |
| `loader_RA7/RA9_patch_cmd_nb` | `6C` (=108) | packet count, matches decoded stream |

So `AuthKeyId` is used symmetrically for both the small in-HAL loader patch and the large
external `*_fw.bin` image: it names the controller key/profile, nothing more. Firmware format
and patchability are analyzed in `firmware-loader-analysis.md`.

## 5. Conclusion

`pAuthKeyId` is an internal ST hardware/chip discriminator. On the Ulefone Armor 29 Pro, the ST21NFCD silicon reports `0x00000002`, identifying it as part of the ST21 family requiring `st21nfc_fw7.bin` and the `RA7` loader protocol. It does NOT indicate that userspace verifies any signature.
