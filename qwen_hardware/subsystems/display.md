> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> The rear display is **1.04-inch / 340x340 on a Chipone CO5300**, not 3.97-inch; the main panel is rated 2200 nits peak by the OEM and the 500-nit figure came from a GSI. See `rear-display.md` and `00-snapshot-provenance-correction.md`.

# Displays and display support ICs

## Hardware found

| Display | Hardware / config | Stock status |
|---|---|---|
| Primary | 1080×2400 AMOLED; `VTDR6115` panel/DDIC contract; 4-lane DSI, RGB888, 870 Mbit/s/lane, 435 MHz PLL | PROVEN active |
| Rear auxiliary | **CORRECTED 2026-09-08: 1.04-inch AMOLED, 340x340, 600 nits peak, driven by a Chipone CO5300 over SPI0 at 60 MHz** (`spi_tiny_lcd_co5300`); vendor `yft_*` stack | PROVEN, DDIC identified - see `../verification/findings/rear-display.md` |
| Bias/gate | `lcd_ocp2131` / OCP2131 on I2C `6-003e`, `mediatek_drm_gateic` | PROVEN |
| Touch-class companion | `chipone-tddi` at `0-0048` is probed/bound in the display path; physical association UNKNOWN | PROVEN binding, population unresolved |

Evidence: live `displays.txt`, `buses.txt`, merged DT, `kernel/phase4-panel-vtdr6115-hardware-contract.md`, `hardware/MASTER-HARDWARE-INVENTORY.md` §display.

## Chip / panel capability layer

* VTDR6115 contract implements video-mode DSI, sync-pulse, low-power mode, non-continuous clock and no-EOT mode flags (`0x0e05`); 60/90/120 Hz switching is selected by DCS command `6c 00/01/02`.
* DCS brightness is 12-bit through `0x51`; HBM command is `51 0f ff`, disable is `51 03 ff`.
* SoC ceiling is higher than the captured system's policy: Dimensity 7400/MiraVision class supports up to FHD+@144 Hz, while this panel path exposes 120 Hz.
* OCP2131 is a positive/negative AMOLED bias/gate supply IC; exact voltage/current/protection limits are UNKNOWN without a datasheet.

## Board configuration

* Primary mode is DSI video, 4 lanes at 870 Mbit/s/lane. The panel driver exports `/sys/class/primary_lcm/set_hbm_backlight`.
* Framework reports `supportedRefreshRates=[120.00001,90.0,60.0]`; snapshot active mode was 60 Hz.
* **Framework values below are from the LieppOS GSI capture**, so they describe that build, not Ulefone stock: HDR types `[2,3,4]` (HDR10/HDR10+ class, HLG and Dolby Vision mapping), with framework luminance capped at `mMaxLuminance=500`, `mMaxAverageLuminance=500`, PQ panel cap ~490 nit — versus the OEM's 2200-nit peak rating.
* `supportedColorModes=[0]` (NATIVE only). **No AOD/doze, CABC or local-HBM implementation was found in the GSI capture — which is not evidence about stock Ulefone software.** ATA/ID readback is a stub (driver-level, valid).
* Rear display is outside the primary Android display/HWC contract and uses the vendor mini-LCD package/firmware.

## Stock usage

* **Observed under the LieppOS GSI** (not stock policy): 60/90/120 Hz selectable, active at 60 Hz. HBM is private/vendor-controlled rather than an Android public display mode.
* **Observed under the LieppOS GSI:** HDR metadata advertised while framework luminance is capped at 500 nit (`mNits=[2.0, 490.0]`). The OEM rates the main panel at **2200 nits** peak, so the 500-nit figure is a GSI framework artefact, not a panel limit.
* Rear display is used for auxiliary/thermal functions, not as a normal full-resolution Android desktop.

## Unused / hidden capability

1. 144 Hz is a SoC ceiling but not exposed by the VTDR6115 mode table.
2. AOD/doze, CABC, local-HBM and panel identification/readback are absent from stock implementation.
3. DCS `0x51` gives direct 12-bit/HBM control, so alternative brightness curves are technically possible but can damage AMOLED hardware if limits are bypassed.
4. `chipone-tddi` and `ilitek` I2C bindings indicate alternate display/touch builds or probing support; physical population is UNKNOWN.

## Missing information

Panel vendor, exact AMOLED stack-up, peak luminance measurement, OCP2131 rails/current ratings, rear-panel DDIC, and whether the ChipOne/Ilitek parts are fitted or only software candidates require teardown, panel label capture, or a rooted DT/status check.

Sources: S01–S05, S08; local contract docs listed above.
