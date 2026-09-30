# Crypto1 evidence: reader side versus PICC side

## Search scope

Searched active `libnfc_nci_jni.so`, active ST HAL, inactive `/system_ext` ST JNI/stack,
AOSP-matched source, config, and the structurally decoded but opaque firmware stream for:
Crypto1, MIFARE/MFC, AUTH A/B, keys, nonce/PRNG/LFSR, 48-bit, sector trailer and PICC.
String evidence: `evidence/crypto1-string-hits.txt`.

## Hit classification

| Evidence | Classification | Why |
|---|---|---|
| `RW_Mfc*`, `rw_mfc_authenticate`, `nfa_rw_check_mifare_data` | **reader-side** | RW module operates after a remote tag is discovered |
| `NativeNfcTag::doConnect` protocol/interface `0x90` | **reader-side** | Selects interface to connect/reselect a remote target |
| `MFC_KeyA`, `MFC_KeyB`, six-byte KeyMAD/KeyNDEF/default key | **reader-side** | Host builds an authenticate request for a remote block |
| `performHaltPICC` | **reader-side** | “PICC” is the remote card being halted; name alone is not card emulation |
| HAL `HAL_FD_STATE_AUTHENTICATE`, `AuthKeyId`, optional `libstnfc-auth.so` | **firmware/authentication or unrelated** | Controller startup/firmware state, not Classic sector auth |
| Firmware `80 88`/`80 36` opaque fields | **generic firmware auth: unknown** | No algorithm or Classic relation recovered |
| Alternative `default_mifare_route` / “Mifare route is UICC” | **off-host routing: unknown** | Possible NFCEE-side MIFARE applet; not proof of its implementation or keys |
| Listen-side nonce/PRNG/LFSR/sector command decoder | **NOT FOUND** | No active-host implementation or decoded firmware evidence |

## Concrete reader-side authentication flow

Matched source `libnfc-nci/src/nfc/tags/rw_mfc.cc:916-972`:

```text
rw_mfc_authenticate(block, KeyA)
  append MFC_KeyA or MFC_KeyB
  append block number
  append remote tag UID[4]
  choose six-byte KeyMAD / KeyNDEF / KeyDefault
  append key
  send 12-byte request to lower MIFARE interface
```

Calls at `rw_mfc.cc:182-186`, `408-412`, and `1006-1011` authenticate before formatting,
writing, or reading a remote sector. The code tracks `sector_authentified` in an RW control
block. This is unambiguously the **reader** proving possession of a key to a card; it does not
generate a card nonce or authenticate an external reader.

The installed JNI's unique “non ISO_DEP and non Mifare” function likewise selects
`NFA_INTERFACE_MIFARE` only for a discovered `MIFARE_CLASSIC` target; full analysis is in
`non-isodep-non-mifare-function.md`.

## What PICC-side evidence would require

A usable Classic emulator would need at least:

1. Listen-A activation with Classic-like anticollision/select;
2. card-side handling of AUTH A (`0x60`) / AUTH B (`0x61`);
3. nonce generation and the Classic PRNG protocol;
4. Crypto1 keystream/parity in the card-to-reader direction;
5. encrypted READ/WRITE/value command state machine, ACK/NAK framing, and sector storage;
6. an exposed controller, NFCEE, or host interface able to meet frame/timing requirements.

None is identified in active host binaries. The standard DH `0x90` LISTEN discovery map is
runtime rejected. Generic exclusive NFC-A/T2T raw framing proves only a byte/frame path; it does
not prove access to encrypted parity/short-frame controls or suitable timing for software
Crypto1.

## NFCEE caveat

The inactive ST stack's off-host MIFARE route is the only non-reader lead. It may reflect a
design where a specific UICC implements MIFARE card behavior. But:

- that stack was not loaded in the observed active process;
- NFCEE existence does not advertise a Classic applet;
- no applet, keys, sector memory, card nonce, or successful RF transaction was observed;
- routing to a secure element would not make arbitrary Android-controlled cloning possible.

Classification: **STATIC IMPLEMENTATION of routing; PICC-side Crypto1 capability UNKNOWN**.

## Verdict

- MIFARE Classic reader authentication: **PROVEN RUNTIME + STATIC IMPLEMENTATION**.
- Active-host PICC-side Crypto1: **NOT FOUND**.
- Standard MIFARE Listen mapping: **PROVEN RUNTIME REJECTED**.
- Off-host/UICC PICC-side Crypto1: **UNKNOWN**, with only an inactive routing lead.
- Firmware-internal PICC-side Crypto1: **UNKNOWN** because executable payload is opaque; no
  reachable enable path was found.
