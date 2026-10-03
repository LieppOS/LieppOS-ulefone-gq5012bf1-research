# NFC configuration and RF tuning

Three configuration layers, with different owners and different risk profiles.

| file | owner | content | board-specific? |
|---|---|---|---|
| `/vendor/etc/libnfc-nci.conf` | `libstnfc-nci.so` (NFA/NCI stack) | polling masks, CE power states, AID matching, storage | mostly generic |
| `/vendor/etc/libnfc-hal-st.conf` | `nfc_nci.st21nfc.st.so` (ST HAL) | HAL module selection, FW/config file names, routing, pipes | partly board-specific |
| `/vendor/etc/st21nfc_conf.txt` | ST HAL / `STFlashTool` → written **into the CLF** | RF CustomA/CustomB, DPC table, antenna, UICC/SE/IOT/NFCC blocks | **yes — board RF tuning** |

## Controller protocol vs board tuning

`st21nfc_conf.txt` (2304 bytes, sha256 `6ac70312be4f…`, 44 lines) is not a
key/value file: it is an ordered script of NCI proprietary writes applied at
boot when the CLF's `CustomerVersion` does not match. Its structure:

```
REM CONFIG CRC IS 4646
REM RESET THE CUSTOMER FIELD
REM HARDWARE CONFIGURATION
REM Writing CustomA RF Parameters      <- analog RF tuning, NFC-A
REM Writing CustomB RF Parameters      <- analog RF tuning, NFC-B
REM Set DPC table                      <- dynamic power control
REM UICC CONFIG                        <- SWP/UICC link parameters
REM SE CONFIG                          <- off-host SE parameters
REM IOT CONFIG                         <- interoperability workarounds
REM ANTENNA CONFIG                     <- antenna/matching
REM NFCC CONFIG
REM WRITE CONFIGURATION CRC IN THE CUSTOMER FIELD
REM MATCHING ;57.4;2.38;105.18;Differential;Yes;15;1.2;No;No;EMI;1500;4.7;77;100;3900;75;1500;150
REM CONFIGURATION ;4650.62890756303;1166.20872689278;6.59234900898292;No;No;Differential;Yes;77;560;112;1.2;27;3900;EMI;150;18;4.7;100;4.5
REM TOOL VERSION 3
```

The two trailing `REM MATCHING` / `REM CONFIGURATION` lines are the ST antenna
tuning-tool record for **this antenna design**: differential antenna, EMI
filter, and the matching network values. They are design data, not per-unit
calibration.

**There is no per-unit calibration data anywhere in the NFC path**: no NVRAM
blob, no `/persist` NFC file, no per-device key in the configuration. The CLF
stores the applied configuration itself and reports it as `CustomerVersion
0x4646`, which equals the file's declared CRC. Nothing private needs to be
withheld; the file is a factory-identical image artifact.

Risk: changing this file (or its name) makes `STFlashTool`/the HAL rewrite the
CLF customer area on the next boot. See [`../protocol/recovery.md`](../protocol/recovery.md).

## Enabled NFC technologies — chip capability vs board enablement

| technology | ST21NFC capability | GQ5012BF1 enablement | evidence |
|---|---|---|---|
| NFC-A reader/writer | yes | **enabled** | `POLLING_TECH_MASK=0x2F` bit0 |
| NFC-B reader/writer | yes | **enabled** | `POLLING_TECH_MASK` bit1 |
| NFC-F reader/writer | yes | **enabled** | `POLLING_TECH_MASK` bit2 |
| NFC-V / ISO 15693 | yes | **enabled** | `POLLING_TECH_MASK` bit3 (0x08) |
| Kovio / barcode tags | yes | **enabled** | `POLLING_TECH_MASK` bit5 (0x20) |
| NFC-B′ | yes | **not enabled** | bit4 clear |
| active-mode A/F (P2P initiator) | yes | **not enabled** | bits 6/7 clear |
| peer-to-peer / LLCP | yes | **disabled** | `P2P_LISTEN_TECH_MASK=0x00` (also removed from Android 10+) |
| ISO-DEP | yes | **enabled**, `ISO_DEP_MAX_TRANSCEIVE=0xFEFF` (65279 B extended length) | HAL conf |
| host card emulation (A/B) | yes | **enabled** | `HOST_LISTEN_TECH_MASK=0x3`, feature `nfc.hce` |
| HCE-F (FeliCa) | yes | **enabled/declared** | feature `nfc.hcef`, `DEFAULT_SYS_CODE={FE:FE}` |
| off-host CE via UICC (A/B/F) | yes | **enabled** | `UICC_LISTEN_TECH_MASK=0x07` |
| MIFARE Classic | ST proprietary protocol slot | **protocol mapped** (`NFA_PROPRIETARY_CFG={05:FF:FF:06:8A:90:77:FF:FF}`, byte 5 = 0x90 ⇒ `NCI_PROTOCOL_MIFARE`), `LEGACY_MIFARE_READER=0x0` | NCI conf |
| CE while screen off | yes | **enabled** | `CE_ON_SCREEN_OFF_STATE=1`, `SCREEN_OFF_POWER_STATE=1` |
| CE while powered off | yes | **enabled** | `CE_ON_SWITCH_OFF_STATE=1` (both conf files), `OFFHOST_AID_ROUTE_PWR_STATE=0x3B` |
| low-power/always-on EE | yes | **enabled** | `ALWAYS_ON_SET_EE_POWER_AND_LINK_CONF=0x03` |
| wake-on-NFC (AP wake from RF) | yes | **enabled** | driver `enable_irq_wake()` + registered `st21nfc` wakeup source |
| low-power tag detection (LPTD) presence-check switch | yes | **disabled** | `LPTD_PRES_CHECK_SWITCH=0` |
| NDEF/T4T NFCEE (controller-resident tag) | yes (NFCEE 0x10) | **disabled in stock** | `NDEF_NFCEE_ENABLE=0` |

Other stack parameters worth carrying into a replacement ROM verbatim:
`NFA_PROPRIETARY_CFG`, `PRESENCE_CHECK_ALGORITHM=5`, `POLL_BAIL_OUT_MODE=0`,
`AID_MATCHING_MODE=0x03`, `NFA_AID_BLOCK_ROUTE=1`, `NFA_MAX_EE_SUPPORTED=0x05`,
`NFCC_CONFIG_CONTROL=0x01`, `NCI_RESET_TYPE=0x00`, `NFC_SNOOP_BUFFER_SIZE=256`,
`DEVICE_HOST_ALLOW_LIST={02:C0}`, `AID_FOR_EMPTY_SELECT={08:A0:00:00:01:51:00:00:00}`,
`CORE_CONF_PROP={20 02 13 06 a1 01 1e a2 01 19 80 01 01 08 01 01 11 01 01 19 01 01}`,
`STNFC_USB_CHARGING_MODE=1`, `STNFC_HAL_LOGLEVEL=0x13`, `STNFC_FW_DEBUG_ENABLED=1`.

`DEVICE_HOST_ALLOW_LIST={02:C0}` is notable: it allow-lists exactly the two HCI
hosts that exist on this board — `0x02` (UICC) and `0xC0` (eSE).
