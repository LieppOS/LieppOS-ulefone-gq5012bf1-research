> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> An **FM radio receiver**, a **3.5 mm headset jack** and an **IR-transmitter PWM path** are documented in `fm-radio-and-headset-jack.md`, `hidden-support-ics.md` and `../verification/findings/ir-blaster.md`.

# Miscellaneous hardware and indicators

## Illumination

* Three Awinic flash/IR drivers: AW36515 dual-channel at `6-0063`, AW36518 single-channel at `8-0063`, AW36518-v2 at `12-0063`. I2C, GPIO and thermal-cooler paths are proven.
* AW2013 at `11-0045` is a separate 3-channel RGB indicator sink. Stock uses red/green/blue channels with 5-mA maxima, GPIO188 power and fixed brightness/hardware blink.
* OEM claims a 570-LED/1000-lumen auxiliary light with 1/50/100% steps; the local physical night-light report counted substantially fewer visible emitters and measured light behavior, so the marketing count/lumen figure is unresolved.
* Four infrared LEDs/night-vision illumination are claimed by Ulefone and consistent with the AW36515/18 multi-channel hardware, but per-LED wavelength and radiant power are UNKNOWN.

## Camera and auxiliary peripherals

* Four conventional camera sensors, four calibration EEPROMs, AF VCMs and one DW9781C OIS controller are covered in `cameras.md`.
* Thermal core uses the separate Miko/FM78100/tiny2c USB path; rear mini-display uses `tiny_lcd_miscdev` and Hynitron touch.
* Pogo/magnetic accessory connector is listed by GSMArena; pinout, USB/UART/I2C protocol and waterproofing are UNKNOWN.

## Other

* NFC, fingerprint, hall, sensors, speaker PA and Type-C are documented separately. No IR blaster was listed by the independent specification, but the stock software chain now proves an MTK LIRC/PWM ConsumerIR implementation; physical emitter/function remains unverified.
* No microSD/removable-storage hardware was proven from the captured software inventory.

## Verification

Count LED dies under magnification, measure optical spectrum/radiant intensity, identify flash-driver channel-to-emitter wiring, read accessory connector pinout from DT and continuity, and inspect PCB silkscreen/package markings.

Sources: S01–S05, S09–S11, S21; `reports/night_light.md`; findings L06/L07/L13.
