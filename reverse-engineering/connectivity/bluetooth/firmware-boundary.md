# Bluetooth firmware boundary

| blob | where | loader | used on GQ5012BF1? | source |
|---|---|---|---|---|
| `connsys_bt_mt6878_mt6637` (761,228 B, `…RAYAS_SOC7_0_E1_ASIC_BT_BWH_OFF-20241028193456`, sha256 `3fa1e9e7…6a4578f`) | partition `connsys_bt` (`stock/firmware/connsys_bt.img`, sha256 `4627391…02cceb4`) | LK → connsys EMI, signed | **yes** (SKU 6637) | proprietary |
| `connsys_bt_mt6878_mt6631` | same partition | LK | no | proprietary |
| `vendor/firmware/soc7_0_ram_bt_1{,a,b}_1_hdr.bin`, `soc7_0_ram_mcu_1{,a,b}_1_hdr.bin` | vendor | `bt_drv` `bgfsys_mcu_rom_patch_dl`/`bgfsys_bt_ram_code_dl` (only with `SUPPORT_BIN2IMG == 0`) | **no**: 6878 builds `SUPPORT_BIN2IMG=1` and DMESG shows the BIN2IMG path | proprietary; leftover/fallback |
| `vendor/firmware/BT_FW.cfg` | vendor | `btmtk_load_fw_cfg` + `libbluetooth_mtk.so` | yes (coex, tssi) | config text |
| per-unit BT address / calibration | nvdata (`APCFG/APRDEB/BT_Addr`, framework) | HAL | yes | per-unit, untouched |

The controller firmware is closed. No controller source exists, so nothing here claims to
reconstruct it.
