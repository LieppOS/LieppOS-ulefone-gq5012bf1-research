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

## Exact GQ5012BF1 questions still to answer

1. Identify the exact ST21 silicon/revision used by GQ5012BF1.
2. Inventory stock `/vendor/firmware`, `/vendor/etc`, NFC HAL libraries and
   configuration for ST firmware/config filenames.
3. Recover the currently installed controller firmware version.
4. Determine whether Ulefone ships a full firmware blob, patch blob, custom
   parameter blob, or only controller configuration.
5. Reverse-engineer the stock HAL's firmware-update checks and image parser.
6. Determine whether image authentication occurs in the Android HAL, the
   controller loader, or both.
7. Determine anti-rollback/version-policy behavior.
8. Determine whether configuration parameters are cryptographically
   authenticated or can be independently changed.
9. Preserve the stock firmware/config blobs before any active experiment.

## Safety

Do not attempt a controller firmware write until the stock firmware blob,
configuration, update protocol, loader/recovery behavior and rollback path are
understood. A failed controller update can leave NFC unavailable even if the
phone itself remains bootable.

Initial work should be static/read-only only.
