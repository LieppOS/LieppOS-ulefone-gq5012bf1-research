# NFC firmware boundary

## What kind of firmware the fitted controller uses

| question | answer | evidence |
|---|---|---|
| ROM firmware only? | **no** | the controller reports a *patch* level (`FwVersion = 0x01209280`) and a separate *loader* version (`0x020201`) |
| patch firmware? | **yes** | `/vendor/firmware/st21nfc_fw7.bin` is a patch image; the tools log `"integrates patch NFC FW version 0x%08X"` and `"FW patch needs to be applied."` |
| downloadable? | **yes**, over the normal I²C/NCI link in loader mode | `NCI_PROP_NFC_FW_UPDATE_CMD`, `APDU_ACTIVATE_LOADER`, `APDU_ERASE_FLASH_LOADER (area 1/2/4)` strings in both `nfc_nci.st21nfc.st.so` and `STFlashTool` |
| persistent flash in the CLF? | **yes** — erase-and-program of flash areas, plus a persistent "customer field" holding the configuration CRC | `APDU_ERASE_FLASH_LOADER`, `"WRITE CONFIGURATION CRC IN THE CUSTOMER FIELD"` in `st21nfc_conf.txt`, live `CustomerVersion = 0x4646` |
| runtime-loaded (RAM) firmware each boot? | **no** | nothing downloads an image on a normal boot; the kernel driver has no `request_firmware()` at all |
| separate NFC firmware partition? | **no** | all images live in `/vendor/firmware/` |

So: **flash-resident patch firmware, updated in place, only when a version
mismatch is detected.**

## Who may write it

| actor | path | trigger |
|---|---|---|
| `/vendor/bin/STFlashTool` | `/dev/st21nfc` | `init.stnfc.rc`, `class late_start`, `oneshot` — runs on **every** boot, both normal and factory mode |
| `nfc_nci.st21nfc.st.so` (`mFwUpdateTask`, `mHalFDState`) | `/dev/st21nfc` | NFC HAL open/reset, when the running patch or config version does not match |
| `st21nfc.ko` | — | **never**; the kernel only provides the byte pipe plus the GPIO reset/recovery sequences |

Update decision inputs, printed by both tools: `HwVersion`, `LoaderVersion`,
`CustomerVersion`, and the patch version embedded in the `.bin`. Unknown patch
images are rejected (`"integrates unknown patch NFC FW -- rejected"`). A failed
exit from loader mode is explicitly logged as a FW-update failure, and
`BackToFactoryLoaderIfPossible` / `"Reset to factory loader"` are the recovery
affordances.

## Steady state on the captured device

```
HwVersion       0x04
HwRevision      0x04
FwVersion       0x01209280   == patch inside st21nfc_fw7.bin
LoaderVersion   0x020201
CustomerVersion 0x4646       == "REM CONFIG CRC IS 4646" in st21nfc_conf.txt
```

Both match the shipped files, therefore a normal boot performs **no** flash
write. This is the condition a replacement ROM must preserve.

## Rules for a replacement ROM

1. Ship `/vendor/firmware/st21nfc_fw7.bin`, `/vendor/firmware/st21nfc_fw.bin`
   and `/vendor/etc/st21nfc_conf.txt` **byte-identical** to stock.
2. Keep `STNFC_FW_BIN_NAME`, `STNFC_FW_CONF_NAME`, `STNFC_FW_PATH_STORAGE`,
   `STNFC_FW_CONF_STORAGE` unchanged in `libnfc-hal-st.conf`.
3. Keep `stflashtool` in the init sequence (or knowingly accept that the CLF
   will not be re-synchronised after a controller-side downgrade).
4. Never ship a *different* firmware image or config: the first boot would
   erase and reprogram CLF flash.

## Proprietary / not reconstructable

| item | status |
|---|---|
| `st21nfc_fw7.bin` / `st21nfc_fw.bin` contents | signed ST patch images, **proprietary**, not decoded, not copied into this research tree |
| `nfc_nci.st21nfc.st.so` FW-download state machine | proprietary, mapped by strings only |
| `STFlashTool` | proprietary |
| CLF loader/ROM code | proprietary, on-die |
| ST proprietary NCI commands inside `st21nfc_conf.txt` | opaque payloads; block purpose is labelled by the file's own `REM` headers |

Nothing in the kernel scope depends on any of these: `st21nfc.ko` is a pure
transport + GPIO driver and is fully reconstructed.
