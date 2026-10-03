# Secure-element topology

## Result

| endpoint | exists | exposed to Android apps | evidence class |
|---|---|---|---|
| Device Host (NFCEE 0x00) | yes | yes — HCE / HCE-F | PROVEN |
| UICC (NFCEE **0x81**, HCI HOST_ID 0x02) | yes | yes — `ISecureElement/SIM1`, `/SIM2`, OMAPI `android.hardware.se.omapi.uicc` | PROVEN (runtime `NFCEE_DISCOVER_NTF`) |
| embedded SE (NFCEE **0x82**, HCI HOST_ID 0xC0) | **yes, advertised by the controller** | **no** — no `android.hardware.se.omapi.ese` feature, no eSE OMAPI terminal, no AP-side eSE HAL or device node | PROVEN |
| NFCEE 0x83 (in `OFFHOST_ROUTE_UICC={81,83}`) | never advertised in any capture | n/a | PROVEN absent at runtime |
| NDEF/T4T NFCEE 0x10 | yes, when `NDEF_NFCEE_ENABLE=1` | disabled in stock (`NDEF_NFCEE_ENABLE=0`) | PROVEN |
| discrete SPI secure element (ST54-class) | **no** | — | PROVEN |

## Why "no discrete/SPI eSE"

- The HAL binary supports four ST families (`st21nfc`, `st54j`, `st54k`,
  `st54l`); the board selects the **controller-only** ST21NFC path
  (`NCI_HAL_MODULE="nfc_nci.st21nfc"`, `STNFC_FW_BIN_NAME="st21nfc_fw7.bin"`).
- `CONFIG_NFC_ST54_SPI=m` exists in the vendor defconfig but **`st54spi.ko` is
  not present in vendor_dlkm, system_dlkm or any ramdisk**, and no SPI SE node
  exists in the device tree.
- `st21nfc.ko` exposes `st21nfc_register_st54spi_cb()` for exactly that driver;
  with no registrant, `ST21NFC_USE_ESE` (ioctl `_IOW(0xEA,9,uint)`) and the
  reset callbacks are no-ops on this device.

## Why NFCEE 0x82 is nevertheless real

Live NFC initialisation (captured previously, see
`../../../Reverse Engineer - PARTIAL/ST21NFC/notes/st21nfc-current-findings.md`):

```
Tx 22 00 00                                  NFCEE_DISCOVER_CMD
Rx 42 00 02 00 02                            status OK, 2 NFCEEs
Rx 62 00 08 81 01 00 01 03 01 02 00          NFCEE 0x81, HOST_ID 0x02  -> UICC
Rx 62 00 08 82 01 00 01 03 01 c0 01          NFCEE 0x82, HOST_ID 0xC0  -> eSE
Tx 22 01 02 82 01 / Rx 42 01 01 00           NFCEE 0x82 enabled OK
i2cNfccMayUseEse(1) ... i2cNfccMayUseEse(0)  eSE arbitration around it
```

HCI HOST_ID 0xC0 is the ST/ETSI identifier for an embedded secure element.
The controller therefore has an eSE endpoint it is willing to enable. Because
the ST54-SPI path is absent, that endpoint can only be reached *through the
CLF* (HCI pipe `OFF_HOST_ESE_PIPE_ID=0x5E`, routing `OFFHOST_ROUTE_ESE={82}`),
never through Android OMAPI.

**Do not report this device as having a usable eSE for payment applets.**
Android advertises UICC OMAPI only, and no OMAPI eSE terminal exists.

## UICC endpoint is slot-independent

With the SIM in slot 1 and again in slot 2, NFCEE discovery was byte-identical
(`0x81` + `0x82`, no `0x83`), while `dumpsys secure_element` followed the active
slot (SIM1 connected ↔ SIM2 connected). Physical slot selection therefore
happens **below** the NCI layer, inside the MediaTek UICC/CLF switching path
(`ro.vendor.mtk_uicc_clf=1`, DSDS). NFCEE 0x81 is a single logical UICC route.

Consequently the vendor comment that maps UICC_2 to `0x85` and the
`OFFHOST_ROUTE_UICC={81,83}` list are **stale/generic ST reference values**, not
a description of this board.

## Routing actually installed

Configured defaults (`libnfc-hal-st.conf`): `DEFAULT_ROUTE`,
`DEFAULT_ISODEP_ROUTE`, `DEFAULT_OFFHOST_ROUTE`, `DEFAULT_NFCF_ROUTE`,
`DEFAULT_SYS_CODE_ROUTE` all `0x81` (UICC), power state `0x3B`.

Runtime behaviour: the stack installs the UICC defaults but then reports
`"Route does not support A/B, using DH as default"` and installs the default AID
on route `0x00` (Device Host). Effective routing must therefore be described
per protocol/AID, not as a blanket "everything goes to the UICC".

## Android-side services

```
android.hardware.secure_element@1.2-service-mediatek
    ISecureElement/SIM1   (MtkUiccSEHal se1)
    ISecureElement/SIM2   (MtkUiccSEHal se2)
android.se.omapi.ISecureElementService
features: android.hardware.se.omapi.uicc   (no .ese)
```

These are MediaTek UICC/SWP terminals that talk to the modem/UICC stack, not to
`st21nfc.ko`. They are outside the ST21NFC kernel scope.
