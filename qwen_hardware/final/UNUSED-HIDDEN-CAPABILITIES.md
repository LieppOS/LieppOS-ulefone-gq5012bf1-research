# Unused and hidden capabilities

**Revised 2026-09-08** after second-pass verification (`../verification/`). Four previously listed items remain **removed as disproven**; second-pass corrections remove false lens/power-IC certainty and identify LN2403 only at LIKELY confidence.

Rank: **A** = directly proven fitted but disabled or under-exposed; **B** = board/driver evidence plus strong silicon capability, not yet verified at runtime; **C** = do not promise without new proof.

## A - fitted and stock-disabled or visibly under-exposed

1. **DW9781C OIS path.** The controller is bound at i2c `4-000e`; a bound WL2864C/WL2868C-family PMIC supplies VDDOIS; every camera reports `availableOpticalStabilization = [0]` (OFF only). **Do not assign it to the main lens:** sensor0 carries `oisvdd`, sensor4 carries `oisen`, and bus topology does not identify the gimbal. Controller/path fitted; lens ownership UNKNOWN.
2. **Camera high-rate and full-resolution modes.** The vendor HAL already publishes 211-215 stream configurations per camera, up to 8192x6144 (main, front, ultrawide) and 9216x6912 (OV64B), including a 7680x4320 (8K) still size on the main camera. What the stock camera application exposes was never measured.
3. **Three bound flash/IR driver ICs**: AW36515 dual independent 2 A channels plus two AW36518-family 1.5 A devices, behind a simple flashlight/night-vision UI.
4. **AW2013 RGB pattern engine** - three channels with auto-breathing and pattern support, used only for basic blink.
5. **IMU and magnetometer output rates** - die ceilings exceed the HAL's 500/100 Hz caps.
6. **Direct panel control** - 12-bit DCS brightness and HBM commands exist; the OEM rates the panel at 2200 nits peak, far above anything a generic framework configuration will request.
7. **FM radio receiver (NEW).** `/fm` and `/fmradio` are enabled with a discrete FM LNA GPIO, FM firmware and a headset-cable antenna switch, and Ulefone ships `YftFmRadio.apk`. **Any custom ROM that omits the FM stack silently deletes a working, fitted radio.** Receive only - no FM transmit firmware ships.
8. **3.5 mm headset jack with 3- and 4-button remote decoding (NEW).** `mt6369-accdet` is enabled with efuse-calibrated key threshold tables. Easy to lose in a port.
9. **Rear 1.04-inch CO5300 AMOLED.** Driven privately over SPI0 with its own backlight, gesture and AOD-status sysfs; it was not registered as an HWC/DisplayManager display in the GSI capture, so AOSP will not drive it without re-implementing the vendor path.

## B - strongly supported by board evidence, not yet verified at runtime

10. **Sensor-level HDR and remosaic** (OV64B staggered HDR, JN1 Smart-ISO) - sensor and platform support exist; public API exposure does not.
11. **Thermal radiometry, FFC and AGC** through the InfiRay AC020 SDK - a private USB-UVC path that no standard Android API can see. Per-unit calibration lives in `/mnt/vendor/nvcfg/infiray` and **must be preserved**.
12. **Dual-band GNSS (L1 + L5/E5a/B2a) across five constellations plus QZSS, with Galileo OSNMA** - fully configured and calibrated for the fitted 0x6637 die; never demonstrated with a fix.
13. **Wi-Fi 6E 6 GHz operation** on the MT6637's internal PA - note that there is **no external FEM to enable**, so 6 GHz range is bounded by the ADIE itself.
14. **PD/PPS direct charging at up to 6 A / 20 V (120 W)** through two bound SC8571 charge pumps (exact part: 2-cell, 8 A, 98.65% peak; board cap 6.55 A each), plus **10 W wired reverse output** through SC8510. Only an SDP host was observed.
15. **Fingerprint factory and gesture paths** - the Microarray SPI/TEE transport exposes more than standard Android authentication, deliberately not public.

## C - do not promise without new proof

16. **USB 3.x SuperSpeed or DisplayPort Alt Mode** - the external product specification says USB 2.0.
17. **Bluetooth LE Audio / Auracast** - the enabled `bluetooth.profile.bap.*` properties seen earlier came from a **GSI system image**, not from stock, and the radio was never powered on. The controller's LE feature mask has never been read.
18. **Full 8K or 4K120 video recording** - a published still-stream size is not a video profile.
19. **1000-lumen auxiliary-light performance and exact IR wavelength/radiant power** - LN2403 is now LIKELY identified as Natlinear's 2 A buck constant-current LED driver, but that datasheet does not identify the fitted emitters, optics, lumen output, wavelength or radiant power. Separately, the ConsumerIR software chain is reconstructed through the selected MTK LIRC backend, but its physical emitter and measured optical output remain unverified.
20. **Retention of IP69K/MIL-STD-810H after opening or reflashing** the phone.

## Removed - previously listed, now disproven

* ~~**Wireless charging (50 W) and reverse wireless charging (30 W)**~~ - **no such hardware exists**: no device-tree node, no `wireless` power supply, no receiver IC, and Ulefone documents wired-only 10 W reverse. The `mt5786group` sysfs paths that suggested it belong to a shared, platform-wide ODM init file describing *other* products. See `../verification/findings/wireless-charging.md`.
* ~~**UFCS fast-charge support**~~ - the kernel enumerates `SDP DCP CDP PD PD_PPS` only, and no UFCS artefact exists anywhere. See `charging-capabilities.md`.
* ~~**Alternate RF front-end modules selectable via ConnFem HWID**~~ - the board resolves to `nofem + nofem`; the seven alternative pairings are other boards' options. There is nothing to unlock. See `connfem-selected-fem.md`.
* ~~**Richer haptics (amplitude/frequency control)**~~ - the motor is an ERM driven from a DC LDO with no haptic driver IC; primitives and closed-loop effects are physically unattainable. See `haptics.md`.
* ~~**Active fan/TEC cooling**~~ - every cooling device exposed by the thermal HAL is electrical throttling; no fan, TEC, pump, tachometer or BLDC node exists. A passive vapour chamber/graphite/copper stack remains possible and teardown-only.

## Safe enablement order

1. **First, take a proper read-only capture on the untouched stock system** - the single most valuable missing measurement, since every framework-level claim above is currently unverified for stock.
2. Read-only runtime dumps: regulator rails, UFS gear, DRAM info, PD/APDO during charge, GNSS `GnssStatus` under open sky, Bluetooth HCI feature masks, NFC `HwVersion`.
3. Non-destructive camera and display experiments with thermal logging, after backing up stock images.
4. Controlled OIS, flash and charging tests on a bench supply - never by raising blind voltage or current limits.
5. Only then expose features in a ROM. Preserve stock firmware, modem NV/calibration, camera EEPROMs, fingerprint/TEE data and the InfiRay thermal calibration in `/mnt/vendor/nvcfg/infiray`.
