> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> **Ilitek 0-0041 and ChipOne-TDDI 0-0048 are unpopulated alternates** that share the FT3680 IRQ/reset pins. See `ilitek-population.md`.

# Touchscreen and touch variants

## Hardware found

### Primary touch — PROVEN
* FocalTech `fts_ts` / FT3680 on `spi3.0` (`/soc/spi3@11013000/focaltech@39`).
* CS0, SPI clock 6 MHz, IRQ GPIO 7, reset GPIO 6; DT compatible `focaltech,fts`.
* Live DT/module contract: `panel_max_display_num=<16>`, `touch_num=10`, ESD protection enabled, firmware-update support and initial-firmware loading enabled.
* Firmware image is embedded in the module (~118,972 bytes); no `focaltech_ts_fw_*.bin` was found in `/vendor/firmware`.
* `module_list` / `upgrade_setting_list` contain three records, but only record 0 is populated: two alternate module records are latent candidates, not proof of extra fitted controllers.

### Auxiliary touch — PROVEN binding, exact die UNKNOWN
* `hyn_ts` / `hynitron,hyn_ts` at I2C `0-0015`, used by the rear/mini display.
* `ilitek` at `0-0041` (`tchip,ilitek`) and `chipone-tddi` at `0-0048` are additionally probed/bound in the I2C/display topology; physical population and role are unresolved.

## Capability layer

* FT3680 exact public datasheet was not located. FocalTech FT3683G-family material supports up to 10 fingers, report rates up to 360 Hz, GOLED/POLED/TDDI configurations and wet/heavy-rain touch algorithms. These are family capabilities, not guaranteed FT3680 limits.
* Hynitron controller capabilities, coordinate resolution, scan rate and firmware identity are UNKNOWN.

## Board configuration

* Primary panel coordinates are handled by the SPI driver with reset/IRQ GPIOs and ESD recovery. `yft_tpd_gesture` supplies vendor gesture wake paths (`tpgesture_*`), and FHP nodes (`fhp_ft`, `fhp_input`) provide additional input plumbing.
* Embedded firmware means a ROM build can update/replace the driver but does not have an obvious vendor firmware blob to flash.
* Auxiliary Hynitron touch is electrically separate from primary FT3680 and belongs to the rear-display stack.

## Stock usage

* Standard touch input is enabled with 10 touch slots; stock gesture and ESD paths are loaded.
* Waterproof/glove/pen performance was not measured. Rear display touch is available through the vendor mini-display application rather than normal primary-panel input.

## Unused / hidden

1. FT3680's unpopulated module records indicate board-family support for alternate touch modules.
2. Family-level high report rate and wet-touch algorithms are not proven enabled by the stock sysfs/HAL snapshot.
3. Hynitron, Ilitek and ChipOne alternate paths could support a variant repair/replacement panel, but no safe cross-flash is established.

## Verification

Read FT3680 firmware/module IDs; inspect `/sys/bus/i2c/devices/0-0041` and `0-0048` status/driver ownership; capture rear panel flex markings; and test touch under water/gloves at each refresh mode.

Sources: S01–S03, S15; local `kernel/phase4-focaltech-ft3680-reconstruction.md` and findings L10/L11.
