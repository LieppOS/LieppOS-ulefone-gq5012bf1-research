# GQ5012BF1 NFC capability ceiling vs Flipper Zero

## Scope

Target phone: Ulefone Armor 29 Pro Thermal (GQ5012BF1 / MT6878T).
Project evidence has already reconstructed the phone's `st21nfc` driver as ST21 NFC driver version 2.2.0.19 against the exact GKI. This comparison separates stock Android APIs, realistic LieppOS/root/custom-NFC-stack possibilities, and capabilities that would require undocumented NFCC firmware support.

## Main architectural conclusion

The Linux `st21nfc.ko` driver is primarily the host transport/power/IRQ/recovery side of the NFC controller. Most protocol behavior lives above it in Android's NFC stack/HAL and inside the NFC controller firmware. Replacing or modifying the kernel driver alone therefore does not turn the handset into a transparent RF transceiver.

By contrast, Flipper Zero uses an ST25R3916 high-performance NFC front end and firmware designed to expose card analysis, raw frame transmission, emulation, reader analysis, and protocol-specific tooling.

## Capability comparison

| Capability | GQ5012BF1 stock Android | GQ5012BF1 with LieppOS/root/custom NFC stack | Flipper Zero | Practical verdict |
|---|---|---|---|---|
| NDEF tags | Yes | Yes, full custom tooling possible | Yes | Tie |
| NFC-A / ISO14443A reader | Yes | Yes, native/raw transceive after activation | Yes | Tie for normal reader use |
| NFC-B / ISO14443B reader | Android supports NfcB if exposed by NFCC | Can expose/develop lower-level tools | Yes | Likely tie for reader use |
| NFC-F / FeliCa reader | Android supports NfcF | Custom polling/APDU tools possible | Yes | Tie for normal reader use |
| NFC-V / ISO15693 reader | Android supports NfcV | Custom block/raw command tools possible | Yes | Tie for reader use |
| ISO-DEP / APDU | Strong | Excellent; arbitrary application-level APDU tooling | Strong | Phone is excellent here |
| Host Card Emulation Type 4 / ISO-DEP | Yes | Excellent; custom AID/APDU services | Flipper can emulate many saved cards, but is not an Android HCE environment | Phone advantage for programmable smart-card applications |
| NFC-F host card emulation | Possible when device exposes Android NFC-F HCE feature | Can customize framework/HAL | Supported NFC-F target/card-emulation hardware | Depends on exact phone NFCC config |
| Arbitrary NFC-A UID/ATQA/SAK emulation | Not exposed by standard Android HCE | Possibly only with vendor/NCI/FW support; not guaranteed | Built-in/manual virtual NFC-A cards | Flipper strong advantage |
| Type 2 / NTAG / Ultralight emulation | Not supported by ordinary Android HCE | Possible only if NFCC firmware exposes suitable low-level card emulation | Built-in support for many Ultralight/NTAG types | Flipper advantage |
| MIFARE Classic read | Device/NFCC-dependent | Could implement tooling if controller exposes MIFARE Classic support | Built-in Classic read/key dictionary workflow | Flipper advantage until phone NFCC support is proven |
| MIFARE Classic emulation | Not ordinary HCE | Would require specific NFCC firmware support | Built-in virtual Classic cards | Flipper major advantage |
| DESFire interaction | ISO-DEP/APDU access is practical | Excellent custom APDU tooling for owned cards/apps | Reads unprotected DESFire applications/files and supports NFC tooling | Phone strong for legitimate APDU development; neither bypasses cryptographic keys |
| Raw protocol frames | `transceive()` is available only after Android/NFCC activation at a technology layer | Native NCI and Android proprietary commands can go lower, but still controller-mediated | CLI can send raw 14443A/B, ISO15693 and FeliCa frames | Flipper advantage |
| Pre-anticollision / unusual frames | Generally hidden | Maybe through proprietary NCI/FW features; needs RE | Designed for this kind of low-level experimentation | Flipper advantage |
| Passive reader analysis/sniff-like observation | Standard Android does not provide general raw RF sniffing | Android observe-mode/poll-frame notification may help if NFCC firmware supports it; still not equivalent to transparent RF capture | Reader analysis is a core Flipper workflow | Flipper advantage |
| MIFARE Classic reader-nonce collection/key-recovery workflow | No standard equivalent | Theoretically researchable only if arbitrary card emulation/reader analysis becomes available | Built-in reader analysis/key-recovery workflow | Flipper major advantage |
| Write normal writable tags | Yes | Yes | Yes | Tie |
| Write UID-rewritable/magic cards | Stock apps vary; low-level wakeup/backdoor commands may be blocked | Some generations may be possible if the NFCC lets us issue the required raw commands | Explicit Gen1/Gen2/Gen4 magic-card tooling | Flipper advantage |
| Custom RF modulation / transparent mode | No Android API | No evidence yet that the handset NFCC exposes a transparent analog mode | ST25R3916 has stream/transparent/low-level modes | Flipper major hardware advantage |
| Field strength / analog tuning / RSSI experiments | Mostly hidden by NFCC | Possibly limited vendor diagnostics only | ST25R3916 exposes high-performance analog features including tuning/measurement capabilities | Flipper advantage |
| Peer-to-peer NFC | Controller family supports P2P class functionality; modern Android app support is limited | Could restore/build custom native P2P tooling if firmware exposes it | ST25R3916 hardware supports active/passive P2P | Both possible, Flipper easier for low-level work |
| Payment/HCE app development | Strong Android ecosystem | Very strong for custom ISO-DEP HCE applications | Not a payment/secure-element replacement | Phone advantage |
| Secure element integration | Phone architecture may integrate SE/eSE/UICC routing; exact GQ5012BF1 secure-element topology still needs its own audit | Can research/control routing if hardware/firmware exposes it | Not comparable to phone payment SE architecture | Phone potential advantage |
| Background app/UI/Internet integration | Excellent | Full Android/Linux capabilities | Limited embedded UI/storage/RPC | Phone major advantage |
| 125 kHz RFID (not NFC) | Impossible with NFC hardware | Impossible without external hardware | Built in | Flipper exclusive |

## What is realistically worth building on LieppOS

The best targets are a privileged NFC laboratory app/service with raw `TagTechnology.transceive()` tooling for NFC-A/B/F/V and ISO-DEP; an APDU console and script engine; tag dump/compare/write tools for owned tags; custom HCE Type-4 applications; native NCI diagnostics; NFCC capability discovery; and a controlled investigation of Android proprietary NCI observe/polling-frame features.

A second-stage research track should determine whether the exact GQ5012BF1 ST21 controller firmware exposes proprietary MIFARE Classic support, arbitrary listen-mode parameters/UID control, Type-2 emulation, low-level RF frame injection before normal activation, and useful RF diagnostics. These cannot be inferred from `st21nfc.ko` alone.

## Bottom line

For normal standards-compliant reading, writing, ISO-DEP/APDU work and programmable HCE applications, the phone can equal or exceed Flipper because Android supplies a powerful application environment. For arbitrary card cloning/emulation parameters, MIFARE Classic tooling, reader analysis, raw frames, magic-card workflows, and analog/RF experimentation, Flipper remains substantially stronger because its ST25R3916 and firmware intentionally expose lower layers.

The most interesting LieppOS goal is therefore not to clone Flipper feature-for-feature, but to build the strongest Android NFC research stack possible and then probe exactly where the ST21 NFCC firmware boundary is.

## External references checked 2026-09-11

- Android Developers, Near field communication overview: https://developer.android.com/develop/connectivity/nfc
- Android Open Source Project, Android proprietary NCI commands: https://source.android.com/docs/core/connect/android-proprietary-nci-commands
- STMicroelectronics, ST21NFCB product page: https://www.st.com/en/secure-mcus/st21nfcb.html
- Flipper Zero Documentation, NFC: https://docs.flipper.net/zero/nfc
- Flipper Zero Documentation, Reading NFC cards: https://docs.flipper.net/zero/nfc/read
- Flipper Zero Documentation, Adding new NFC cards: https://docs.flipper.net/zero/nfc/add-manually
- Flipper Zero Documentation, Tech specs: https://docs.flipper.net/zero/development/hardware/tech-specs
- STMicroelectronics, ST25R3916 product page: https://www.st.com/en/nfc/st25r3916.html
