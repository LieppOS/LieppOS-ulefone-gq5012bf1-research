> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> The vendor is confirmed as **Microarray/MaFinger**; the modality is probably **optical in-display**, not capacitive. See the verification `fingerprint.md`.

# Fingerprint sensor

## Hardware found — PROVEN presence, exact die UNKNOWN

* SPI `spi1.0` binds driver `madev`; module is `microarray_fp_tee` and DT node is `madev_finger`.
* Android-facing nodes: `/dev/madev0` (`mafinger_device`) and `/dev/tkcore_fp` (`tkcore_client_device`). TrustKernel TEE client is present.
* DT exposes reset and interrupt GPIOs, `interrupts=<3 1 3 0>`, debounce `<3 0>`, status `okay`, and 16 pinctrl states switching SPI0 MI/MO/CLK/CS between SPI and GPIO fallback.

## Capability layer

The transport is consistent with a Madev/Microarray capacitive fingerprint module, but no public exact Madev die part number or datasheet was located. Sensor area, resolution, FPS, wet-finger performance, spoof resistance and gesture features are therefore UNKNOWN. TrustKernel provides secure matching/TEE integration; it does not identify the sensor die's analog capability.

## Board configuration / stock use

The kernel module, TEE device and GPIO/pinctrl contract are loaded. Stock Android exposes fingerprint authentication through the vendor framework; no evidence proves an always-on gesture sensor or fingerprint-as-shutter function. SPI speed, image dimensions and power sequencing are not in the public snapshot summary.

## Hidden / unused

* Gesture/wake, wet-finger enhancement and raw-image diagnostics may exist in the Madev/vendor ABI but are not exposed by standard Android APIs.
* SPI/GPIO fallback states could support factory test/recovery, not a second sensor.

## Verification

Capture the `madev` sysfs/module parameters and TrustKernel TA strings; inspect the sensor flex/package marking; exercise enrollment/authentication while logging SPI timing; do not expose raw fingerprint frames outside the TEE.

Sources: S01–S03; live `fingerprint.txt`, `buses.txt`; findings L14.
