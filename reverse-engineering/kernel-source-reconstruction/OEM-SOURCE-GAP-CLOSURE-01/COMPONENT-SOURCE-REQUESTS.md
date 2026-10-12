# DRAFT: component vendor requests (NOT SENT — each requires user approval)

These are secondary routes, to use if Ulefone does not respond. Each names only the GPL module(s) of that vendor
and their shipped hashes (see MISSING-SOURCE-MATRIX.tsv). Ulefone, as the distributor, is the primary addressee
(`ULEFONE-SOURCE-REQUEST.md`). Component vendors may have no obligation to the end user, so these are courtesy
requests.

| Vendor | Modules (modinfo licence) | Ask | Note |
|---|---|---|---|
| **MediaTek** | `flashlight.ko` (GPL) | `flashlight-core.c` + Kconfig as delivered to the GQ5012BF1 ODM (PT strict, `flashlight_drvctrl`, `flashlight_sw_ctrl_*`) | Usually not public; ODM may hold the modified copy |
| **MediaTek** | `fpsgo.ko`, `msync2_frd.ko` (**Proprietary**) | source of `xgf_v3_ko_quark` and `mtk_disp_msync` | Courtesy only; no GPL claim |
| **Richtek / MediaTek** | `charger_class` 1.0.0_G, `mtk_chg_type_det` 1.0.2_MTK, `rt_pd_manager` 1.0.11, `tcpc_class` 2.0.31_MTK, `tcpc_mt6375` 1.0.3 (GPL) | exact source files at those versions | Only srcversion/line metadata differ; any exact copy closes 5 C rows |
| **Awinic** | `aw883xx_driver` (GPL v2) | AW883XX driver v1.7.1 (scene/bin parser) | 235/236 functions already exact |
| **FocalTech** | `focaltech_touch_spi_ft3680` (GPL v2) | FT3680 SPI driver revision shipped | 67/166 functions |
| **STMicroelectronics** | `st21nfc` 2.2.0.19 (GPL) | exact 2.2.0.19 tree | 22/24 functions |
| **SouthChip** | `sc851x_charger`, `sc8571_charger` (GPL v2) | MTK charger_class variants as delivered | public SC8541 template (LKML 2025-10-13) is a different chip |
| **Sinowealth** | `sh366003_fg` (GPL v2) | SH366003 MTK gauge driver | |
| **Will Semi / ODM** | `custom-ldo-wl2868`, `custom-ldo` (GPL / GPL v2) | WL2864/WL2868 misc LDO driver | public WL286x drivers have a different ABI |
| **Hynitron** | `hynitron` (GPL v2) | CST driver + firmware header as built | firmware arrays are a separate boundary |
| **ODM (YFT)** | `yft_devinfo`, `yft_tiny2c_usb`, `yft_tpd_gesture`, `fingerprint`*, `yft_gpio_keys`* (GPL) | driver sources + private headers | *currently in Codex batch-02 |
| **Panel / LCM vendors** | `panel-ky-vtdr6115-dphy-cmd`, `spi_tiny_co5300_lcd`, `leds-ln2403` (GPL / GPL v2) | panel/LED driver sources | MediaTek-authored VTDR6115 panel (shaohua.deng@mediatek.com) |
| **TrustKernel** | `tkcore`, `tkcore_drv` (GPL) | see `TRUSTKERNEL-SOURCE-REQUEST.md` | |
