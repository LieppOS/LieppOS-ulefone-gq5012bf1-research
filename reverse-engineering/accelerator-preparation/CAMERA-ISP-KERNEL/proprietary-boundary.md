# Proprietary boundary — CAMERA-ISP-KERNEL

The owned normal-world kernel scope is DONE. The following remain deliberately outside it:

* CameraProvider/HAL services and libraries;
* 3A, tuning, image-quality and calibration-interpretation algorithms;
* CCU/CCD/ISP firmware and secure-world payloads;
* per-unit EEPROM calibration and signing keys;
* sensor/EEPROM/VCM/OIS/flash/LDO components already owned elsewhere.

They remain under `CAMERA-HAL-ISP` (PARTIAL) or their existing component owners. See
[firmware-boundary.md](firmware-boundary.md) for the exact retained firmware inventory and
[source-to-userspace-contract.md](source-to-userspace-contract.md) for the HAL boundary.

The maintained repository and preserved source bundle contain only public source, explicit
source patches and build/verification scripts—no stock `.ko`, `.img`, `.bin`, proprietary
library or calibration payload.
