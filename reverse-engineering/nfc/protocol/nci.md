# NCI-level facts

The kernel driver is protocol-agnostic (a byte pipe), so everything here lives
in userspace. Collected for completeness; the configuration-side analysis is in
[`../configuration/analysis.md`](../configuration/analysis.md).

## Controller identity reported over NCI (live capture)

```
HAL version       140-20240525-24W21p0
HwVersion         0x04
HwRevision        0x04
FwVersion         0x01209280
LoaderVersion     0x020201
CustomerVersion   0x4646
firmware image    st21nfc_fw7.bin
```

## NFCEE discovery (live)

```
Tx 22 00 00                               NFCEE_DISCOVER_CMD
Rx 42 00 02 00 02                         OK, 2 NFCEEs
Rx 62 00 08 81 01 00 01 03 01 02 00       0x81 HOST_ID 0x02  UICC
Rx 62 00 08 82 01 00 01 03 01 c0 01       0x82 HOST_ID 0xC0  eSE
Tx 22 01 02 81 01 / Rx 42 01 01 00        enable 0x81 OK
Tx 22 01 02 82 01 / Rx 42 01 01 00        enable 0x82 OK
```

With `NDEF_NFCEE_ENABLE=1` the controller additionally exposes NFCEE `0x10`
(NDEF storage, CC: mapping 2.0, file `0xE104`, 8192 bytes, read+write allowed)
and emits `RF_NFCEE_DISCOVERY_REQ_NTF` `61 0A 0B 02 00 03 10 80 04 00 03 10 81 04`
requesting ISO-DEP passive listen on NFC-A and NFC-B.

## Kernel-visible NCI detail

`st21nfc_ping()` is the only place the kernel inspects NCI content: it accepts
the controller as alive when the first two bytes of a received frame are
`0x60 0x00`, i.e. `CORE_RESET_NTF` (MT=NTF, GID=0, OID=0). `0x7E` bytes are
treated as "no data" filler, both in `ping()` and in `read()` when the IRQ line
is low.

## Proprietary command surface

`st21nfc_conf.txt` drives `NCI_DIRECT_CTRL` writes for the CustomA/CustomB RF
parameter sets, the DPC table, and the UICC/SE/IOT/ANTENNA/NFCC blocks, framed
by a customer-field reset and a final CRC write. `STFlashTool` additionally uses
`NCI_PROP_NFC_FW_UPDATE_CMD` / `NCI_PROP_NFC_FW_RSP` and the loader APDUs
(`APDU_ACTIVATE_LOADER`, `APDU_ERASE_FLASH_LOADER`). Payload semantics are ST
proprietary and were not decoded.
