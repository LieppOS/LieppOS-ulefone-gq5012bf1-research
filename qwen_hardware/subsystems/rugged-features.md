> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Water resistance is **1.5 m / 30 min** (not 2 m), with IP68 + IP69K, MIL-STD-810H and Gorilla Glass 3. See `ip-mil-certification.md`.

# Rugged and physical features

## Proven / strongly supported

* Product is a thick, heavy Armor-series chassis: GSMArena reports 688 g and 33.8 mm.
* Android/vendor stack contains Hall control, USB-port/skin/PA thermal sensors, flashlight thermal cooling, rear auxiliary display, thermal camera, night-vision/IR native components and a pogo/magnetic accessory path.
* Ulefone claims IP68/IP69/IP69K, MIL-STD-810H and 2-m/30-min water protection; these are official claims, not test evidence.
* The chassis includes large battery, loudspeaker smart PA, hardware auxiliary light, camera array, NFC, fingerprint and programmable physical controls consistent with an industrial/rugged design.

## Capabilities and limits

* Rugged certification protects a complete assembly; it does not guarantee that an opened/rebuilt ROM device retains the seal.
* Thermal thresholds and charging safeguards are part of the reliability envelope. Raising them in a custom ROM can damage the pack, USB port, AMOLED, flash LEDs or PA.
* Hall/magnetic accessory behavior and sealed pogo connector are hardware/software integration points; no replacement ROM should assume the accessory protocol.

## Unproven

No independent IP/impact test report, teardown, gasket cross-section, Gorilla/glass grade, glove rating, underwater audio behavior, drop height, or MIL-STD test matrix was found. Vapor chamber/active cooler is UNKNOWN.

## Verification

Use OEM certification/test reports where available; inspect gaskets and port plugs only after accepting water-resistance loss; test glove/wet touch and accessory behavior; do not use a custom kernel's altered thermal limits as a ruggedness claim.

Sources: S04/S05/S23; live thermal/display/touch/accessory evidence.
