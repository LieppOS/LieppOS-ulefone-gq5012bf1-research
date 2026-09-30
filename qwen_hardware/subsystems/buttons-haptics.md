> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> The actuator is an **ERM motor on the MT6369 `VIBR` LDO with no haptic driver IC** - richer haptics are physically unattainable. See `haptics.md`.

# Buttons, hall, indicators and haptics

## Hardware found

* One Android vibrator is proven: `vibratorIds=[1]`. No separate LRA/ERM driver IC was visible as a dedicated I2C child; drive may be GPIO/PMIC-integrated.
* Vibrator service supports CLICK, DOUBLE_CLICK, TICK, HEAVY_CLICK and TEXTURE_TICK effects; no primitives or braking characteristics; frequency/output acceleration are NaN.
* Android reports amplitude scales LOW/NONE/HIGH/VERY_HIGH = 0.714/1.0/1.4/1.96, ramp step 5 ms, composition max 256 and primitive delay max 1000 ms.
* MT6375/board contract includes a Hall path (`hall_ctrl`); physical magnet placement/cover use is not separately measured.
* Physical power/volume/PTT/camera buttons are expected on this rugged chassis, but individual GPIO/keycode mapping was not available in the condensed snapshot.

## Board configuration / stock use

* Effect-only vibrator API is active; no resonant frequency, acceleration or primitive composition metadata is exposed, implying generic ERM/LRA abstraction.
* Notification LED is separate: AW2013 at `11-0045`, GPIO188 power, red/green/blue channels max 5 mA; stock fixed brightness red 64, green 64, blue 128 and hardware blink.
* Camera/flashlight illumination is separate AW36515/AW36518 hardware, not the notification LED.

## Hidden / unused

1. Haptic primitives, frequency control, braking and closed-loop amplitude are not exposed by stock.
2. AW2013 has three channels and an auto-pattern/breathing capability at chip level, but stock contract uses red/green and hardware blink only; blue/fancy breathing is unused.
3. Hall wake/cover-state behavior may be consumed by the rugged accessory/mini-display stack but is not proven by a cover test.

## Verification

Dump `/sys/class/leds`, keylayout/GPIO DT nodes and vibrator HAL implementation; test all physical buttons, hall magnets and haptic effects; identify motor type and measure resonance/current with an oscilloscope.

Sources: S01–S03, S11; `lights-vibrator.txt`; findings L07/L16.
