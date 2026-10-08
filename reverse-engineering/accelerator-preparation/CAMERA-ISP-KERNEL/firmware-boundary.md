# Firmware boundary — CAMERA-ISP-KERNEL

The normal-world kernel component is reconstructed; the camera firmware and algorithms
are **retained proprietary binaries** and are not claimed as source.

| artifact | bytes | SHA-256 | owner / disposition |
|---|---:|---|---|
| `firmware/ccu.img` | 103 168 | `892e293149a866f02ab4481a3c4565e259e71b6fcacb7ca3a28fe778ddcada58` | CAMERA-HAL-ISP; retain |
| `vendor/firmware/lib3a.ccu` | 1 237 916 | `2a052eca46591846d6a4b83912d624cd6726779a18148fd855519454baedcf96` | CAMERA-HAL-ISP; retain |
| `vendor/firmware/lib3a.ccu_dummy` | 52 | `fe17e88fc38b47b0d1d3191343b6812900c81f106b3259a03213e80b5308706a` | CAMERA-HAL-ISP; retain |

The hashes are inventory evidence only. A signed scatter image is not proof that Linux
loads it through `request_firmware()`, and the historical `loader_claim` column in
[firmware-boundaries.tsv](firmware-boundaries.tsv) is not promoted into such a claim.

## Reconstructed host side

`mtk_ccd_remoteproc.ko`, `ccd_rpmsg.ko`, `mtk_ccuv.ko`, HCP, IMG_SYS and camsys now have
source/parity closure for their normal-world transport, buffer, remoteproc/RPMsg and
control plumbing. That establishes the host ABI implementation present in the shipped
kernel modules; it does **not** reconstruct the remote image.

## Explicit exclusions

* CCU/CCD/ISP remote instruction and data images;
* signed/secure-world payloads and signing keys;
* 3A, tuning, image-quality, depth/AI model and calibration-interpretation algorithms;
* per-unit EEPROM calibration data;
* proprietary CameraProvider/HAL libraries and services.

Those remain in `CAMERA-HAL-ISP` (PARTIAL) or their existing sensor/EEPROM owners. No
firmware, HAL blob, calibration dump or stock `.ko` is included in the maintained source
repository or its bundle.

## Runtime requirement

A device test still has to show firmware authentication/load, remoteproc state, RPMsg
endpoint creation, CCU request/response and teardown. Static module parity is not a claim
that the retained firmware boots or that its protocol succeeds.
