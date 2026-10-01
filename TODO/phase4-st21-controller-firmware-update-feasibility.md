# GQ5012BF1 ST21 NFC controller firmware-update feasibility

## Current conclusion

The ST21-family NFC controller firmware is not necessarily immutable.

ST's ST21NFCD documentation states that the controller contains eFlash for full
firmware update and implements a secure firmware-update mechanism.

The Android ST `st21nfc` HAL also contains a controller firmware-update state
machine. It supports controller loader mode, firmware-update retries, firmware
and configuration files stored under a configurable vendor firmware path, and
factory-reset-triggered update logic.

Therefore an Android phone can, in principle, deliver a firmware update to the
ST21 NFC controller.

However, this does **not** imply that arbitrary self-built firmware can be
installed. The secure firmware-update mechanism likely authenticates vendor
firmware independently of Android Verified Boot / the phone bootloader. An
unlocked Android bootloader does not automatically grant authority to sign NFC
controller firmware.

## Practical capability levels

| Operation | Current assessment |
|---|---|
| Read controller firmware/version information | Very likely possible |
| Observe/update decision logic in ST HAL | Possible |
| Extract vendor firmware/config blobs from stock partitions | Likely possible if shipped as files |
| Replay/install the same authentic vendor firmware | Likely possible through the vendor updater |
| Install another compatible ST/Ulefone-signed firmware build | Possible if controller accepts its signature/version/device policy |
| Modify configuration/custom-parameter blob | Potentially possible; must determine whether it is authenticated separately |
| Patch firmware bytes and flash the modified image | Probably rejected by secure update authentication |
| Build arbitrary custom ST21 firmware and flash it | Probably impossible without an accepted signing key or a controller vulnerability |
| Replace the controller's immutable boot ROM | Impossible through normal firmware update |

## Important distinction

The Linux `st21nfc.ko` driver is primarily the host transport/reset/recovery
layer. Firmware update logic is substantially above it in the ST NFC HAL and
inside the controller's own loader.

The controller's secure update trust root is separate from the Android boot
chain. Root access, a custom kernel, or an unlocked phone bootloader therefore
does not by itself remove controller firmware authentication.

## Answers so far (Phase 4b — static, read-only, reproducible)

All of this is derived from blobs and outputs committed in this repo; re-run
`hardware/nfc/tools/st21-fw-loader-reproduce.sh` and diff `hardware/nfc/analysis/
st21-gemini-audit/audit/`. Main write-up:
[`firmware-loader-rev2.md`](../hardware/nfc/analysis/st21-gemini-audit/firmware-loader-rev2.md)
(§n below), with [`firmware-format.md`](../hardware/nfc/analysis/st21-gemini-audit/firmware-format.md).

| # | Question | Status |
|---|---|---|
| 2 | Firmware/config inventory of the NFC stack | **answered** — one HAL generation drives it all: `vendor/lib64/nfc_nci.st21nfc.st.so` (MD5 `fda028cf…`, not stripped, 237 exports) with `hal_fd_load_files`/`hal_fd_*`/`LdUpdateHandler` inside it; images `vendor/firmware/st21nfc_fw.bin` + `st21nfc_fw7.bin` (both 215 568 B = 0x34a10), config `vendor/etc/st21nfc_conf.txt`, driven by `STNFC_FW_PATH_STORAGE`/`_CONF_STORAGE`/`_BIN_NAME`/`_CONF_NAME`, fallbacks `/vendor/firmware/`, `/vendor/etc/`, `{st54j_fw,st21nfc_fw7,st21nfc_fw,st54l_fw}.bin` (§2–3). No `libnfc_hal_dnld.so`/`libunlzodecompress.so` in this generation. |
| 4 | Full blob vs patch vs parameter blob | **answered** — all three coexist: two full images on the vendor partition, a *separate* CRC-checked config descriptor (binary **or** text flavour), and 2×24 610 B RA7/RA9 patch payloads embedded in the HAL's `.rodata` as `loader_RA*_patch*` with `(version, cmd_nb, AuthKeyId)` = `(0x20201, 108, 2)` / `(0x20301, 108, 1)` (§4). |
| 5 | Reverse the stock update checks and parser | **largely done** — 117-call-site trace of `[0x218a8, 0x237f0)` shows real `fopen`/`fread`/`fgetpos`/`fsetpos`/`stat` plus `CNfcConfig::GetStrValue`, and the loader APDU sequence (`APDU_ERASE_FLASH_CMD`, `APDU_ERASE_FLASH_LOADER` areas 4/1/2, `APDU_ACTIVATE_LOADER`, `APDU_AUTHENTICATION_CMD`, `APDU_EXIT_LOAD_MODE_CMD`, `NCI_PROP_NFC_FW_UPDATE_CMD` on a 100 ms per-command timer). Container framing: `0x80922001`, record tag `0x8015042f`, `0x10000088`, per-image word; the tag recurs at 0x4/0x1c/size−24 (header, second record, trailer). |
| 9 | Preserve stock blobs before experiments | **done** — hash-pinned in `hardware/nfc/analysis/st21-gemini-audit/evidence/*.sha256.txt`; the durable copies there and in `hardware/nfc/blobs/` are byte-identical to the V15 stock `vendor` partition (§1). |
| 8 | Are the config parameters authenticated? | **partly** — the HAL verifies only a CRC16 on both config flavours (`-> bin configuration CRC 0x%04X .`, `-> txt configuration CRC 0x%04X .`). A CRC is not authentication, so the *HAL* will forward a hand-edited config; whether the controller accepts it is #6. |
| 3 | Currently installed controller firmware version | **open, instrumented** — needs a live read: `STNFC_FW_DEBUG_ENABLED=1` is already shipped, and `%s - FW update file = %s`, `%s --> %s integrates patch NFC FW version 0x%08X (r:%d,t:%s).` and `Factory loader activated, revision 0x%06X` print it to logcat during open. |
| 6 | Where does image authentication happen? | **open** — HAL-side gate is *selection* by `loader_<gen>_patch_AuthKeyId` (`AuthCheckCoreResetNtf`, `AuthCheckUnload`), which proves the HAL never validates image bytes; so authentication, if any, is in the controller loader. Not yet observed on-device. |
| 7 | Anti-rollback / version policy | **open** — `loader_patch_version` is `.data` = `0xffffffff` and the rest of the selection slots `.bss`, i.e. chosen at runtime from the embedded table; nothing read-only shows a monotonic-version check. |
| 1 | Exact ST21 silicon/revision | **open** — RA7/RA9 are patch generations, not silicon revisions; the HAL probes `/sys/devices/soc0/{soc_id,hw_platform}` and `/sys/devices/system/soc/soc0/{id,hw_platform}`, and the candidate image names include `st54j_fw.bin`/`st54l_fw.bin` (eSE-oriented ST names), which still has to be resolved against the actual chip. |

Consequence for the table above: *"Modify configuration/custom-parameter blob"*
is more reachable than it looked — the shipped HAL gates that path on a CRC, not a
signature — while *"Patch firmware bytes and flash the modified image"* stays
unverifiable from static analysis alone, because nothing in the HAL authenticates
the image at all (§6 open).

## Safety

Do not attempt a controller firmware write until the stock firmware blob,
configuration, update protocol, loader/recovery behavior and rollback path are
understood. A failed controller update can leave NFC unavailable even if the
phone itself remains bootable.

Initial work should be static/read-only only.
