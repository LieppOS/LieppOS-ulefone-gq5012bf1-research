> **Pass-2 pointer (2026-09-08).** First-pass working material. Where anything here conflicts with `../final/` or `../verification/findings/`, the verification pass wins. Two blanket corrections apply: the 2026-08-31 capture ran a **LieppOS GSI**, so its framework-level observations are not stock Ulefone behaviour; and `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this board's bill of materials.

# Web-search log

The web pass used `provider=anysearch` because the configured Exa/Brave routes were rate-limited or unavailable. Search results were treated as secondary evidence unless from a chip/OEM vendor. Full query list and claim mapping are in `queries.md` and `sources.md`.

## Completed query groups

* AW88394 smart PA; AW36515/AW36518 flash drivers; AW2013 RGB driver.
* FocalTech FT3680/FT3683G touch family.
* SPL07-003, MMC5603NJ, ICM-4N607 family, STK3A5X.
* Richtek RT6160; Southchip SC8571; SH366003.
* ST21NFCB/ST21NFCD; MediaTek MT6637/MT6639 connectivity family.
* Samsung S5KJN1/JN1; OmniVision OV64B; Sony IMX989.
* Dimensity 7400/MT6878 platform.
* Qorvo QM42195/QM45197 and Skyworks SKY853xx/SKY857xx FEM families.
* InfiRay/T2/M170-class 640×512/12-µm thermal modules.
* Hynitron touch and Armor 29 Pro Thermal teardown.

## Negative-search rule

No public exact datasheet was found for FT3680, MT6637, ICM-4N607, SC8571, SH366003, FM78100, VTDR6115, CO5300, OCP2131, WL2864C, Madev die or this phone's teardown. These are recorded as UNKNOWN, not as absent hardware.
