> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> The controller is an **ST21NFC-family CLF with no embedded secure element**; off-host routing is UICC-only, and there is **no eSIM**. See `st21-variant.md` and `esim-euicc.md`.

# NFC and secure element

## Hardware found — PROVEN

* STMicroelectronics **ST21NFC-family** controller at I2C `6-0008`, driver/module `st21nfc`.
* NCI service: `android.hardware.nfc-service.mediatest`; client library `libst21nfc_aidl_nci_client.so`.
* Firmware set includes `st21nfcbin_hdr_103a13111000_93111.bin` and three `.se` secure-element images. Stock secure-element services expose SIM1 and SIM2 instances.

## Capability layer

ST21NFCB/ST21NFCD family is a 13.56-MHz contactless controller supporting NFC card/reader/writer and NFC-DEP/P2P operation, with ISO14443/FeliCa/ISO15693-class protocols and mobile secure-element routing. Exact B/D variant is UNKNOWN; firmware header and module strings were not enough to prove it.

## Board configuration / stock use

* `ro.vendor.mtk_nfc_addon_support=1`, `nfc.initialized=true`; `nfc_hal_service` is running.
* SIM/eSE services expose two secure-element instances, consistent with dual-SIM/eSE routing. `persist.lieppos.armor29.nfc_routing_watchdog=true` is a watchdog policy, not proof of a specific antenna.
* OEM/GSMArena claim NFC payment support. Polling, HCE, UICC routing and actual payment transaction were not run in the frozen capture.

## Hidden / unused

* Reader/writer, card emulation and P2P modes may all be supported by the controller even if UI exposes only payment/HCE flows.
* Multiple `.se` images and SIM1/SIM2 routes indicate alternative secure-element routing paths; secure transactions should remain TEE/SE-controlled.

## Verification

Read ST21 firmware header/variant, dump NCI capabilities and routing table, test ISO14443A/B, FeliCa and HCE, and verify antenna matching only with RF test equipment. Do not modify payment/eSE routing on a production device without backup.

Sources: S01–S03, S19; `kernel/phase4-st21nfc-analysis`; findings L18.
