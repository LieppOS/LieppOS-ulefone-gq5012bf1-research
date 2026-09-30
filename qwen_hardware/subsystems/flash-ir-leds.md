> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.

# Flash, IR and RGB LEDs

## Hardware found

* Awinic AW36515 at I2C `6-0063`: dual-channel boost flash/torch driver with independent channel registers, external strobe GPIO and thermal foldback.
* Awinic AW36518 at `8-0063` and AW36518-v2 at `12-0063`: single-channel boost flash drivers; kernel contract rejects a second LED number on each single-channel path.
* AW2013 at `11-0045`: 3-channel constant-current RGB indicator, chip ID 0x33, GPIO188 power, 5,000 µA/channel configured. Stock brightness was red 64, green 64, blue 128 with hardware blink.
* OEM claims four infrared LEDs/night-vision illumination and a 570-LED/1000-lumen auxiliary light. The local night-light report measured the device and found an emitter count inconsistent with the marketing count; exact LED package/wavelength is UNKNOWN.

## Three layers

**Chip:** AW36515/18 family provides I2C-programmed flash/torch current, timeout, boost regulation, strobe and thermal/current protection. AW2013 provides three current sinks and auto-pattern/breathing capability.

**Board:** all three flash-driver bindings and RGB driver are proven; rear cameras have flash units, front camera does not. The thermal HAL exposes `flashlight_cooler`, so flash output participates in thermal policy.

**Stock:** simple flashlight, camera flash/night vision and RGB notification/blink paths are enabled. AW2013 breathing/pattern and independent multi-channel control are not exposed as a general API.

## Hidden / unused

* AW2013 third-channel/pattern engine and AW36515 independent channels are underused.
* Per-LED current, IR wavelength/radiant intensity and thermal foldback limits are undocumented in every available source — no LED datasheet surfaced, and the capture ran a GSI containing none of Ulefone's own apps, so nothing here evidences stock app behaviour.
* Auxiliary-light “1000 lm” and “570 LED” figures remain claims, not a verified optical BOM.

## Verification

Read programmed AW36515/18 current codes, map channels to emitters, measure spectrum/radiance and thermal behavior, and inspect LED package markings. Preserve current/timeout limits when modifying a ROM.

Sources: S01–S04, S09–S11; `reports/night_light.md`; findings L06/L07.
