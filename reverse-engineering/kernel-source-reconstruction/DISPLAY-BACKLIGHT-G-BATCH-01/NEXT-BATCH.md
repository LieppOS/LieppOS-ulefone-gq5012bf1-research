# Remaining after this batch (projected 23 G + 3 D + 11 C = 37 uncertified)

Recommended next unowned family: **charging, regulator and SPI board IO**. These are public-source candidates
(`LIKELY_EXACT_PUBLIC…`) with complete ALPS/GKI source located by Codex's inventory:

| Module | Source | Note |
|---|---|---|
| extdev_io_class | ALPS `drivers/power/supply` (extdev_io_class) | provider of rt5133 / charger IO |
| rt5133-regulator | ALPS `drivers/regulator` | DT regulator node |
| spi-mt65xx | GKI/ALPS `drivers/spi` | SPI controller for co5300 tiny LCD and fingerprint |

After those, the remaining G rows are OEM/ODM drivers with no public source located (`UNKNOWN_SEARCH_OTHER_OEM…`):

- aw36515, aw36518, aw36518_v2 (flash). Historical LieppOS Phase-4 reconstructions exist for aw36518/_v2 with
  22/23 functions; these are disassembly-derived and **not certifiable** as source.
- panel-ky-vtdr6115-dphy-cmd and spi_tiny_co5300_lcd (display panels).
- leds-rgb-aw2013, leds-ln2403, hynitron, the yft_* modules, fingerprint, microarray_fp_tee, sc851x/sc8571 chargers,
  sh366003_fg, custom-ldo, custom-ldo-wl2868, camera_eeprom_v4l2.
- tkcore_drv (TrustKernel).

These need an OEM GPL source release; the shared TrustKernel header request is in
G-CANONICAL-INTEGRATION-01/TRUSTKERNEL-ABI-BOUNDARY.md.

Category D: flashlight (OEM flashlight-core.c), fpsgo and msync2_frd (prebuilt `*_shipped` objects; project rule).
Category C: tmem_ffa and tkcore (TrustKernel ABI), plus the 9 earlier C rows with their recorded obligations.
