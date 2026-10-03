# Wi-Fi firmware boundary

| blob | where | loader | when | source? |
|---|---|---|---|---|
| `connsys_wifi_mt6878_mt6637` sub-image (1,617,596 B, `t-neptune-main-soc7_0-2104-RAYAS_SOC7_0_E1_ASIC_MT6637-20241028193456`, sha256 `0670150b…2a4fb1`) | partition `connsys_wifi` (`stock/firmware/connsys_wifi.img`, sha256 `308b7bd9…e3c239`) | **LK** `platform_load_connsys` into connsys EMI (0x87e00000 region), signed (cert1/cert2) | boot, before Linux | proprietary, no source |
| `connsys_wifi_mt6878_mt6631` sub-image | same partition | LK, only for SKU 6631 | not used here | proprietary |
| `WIFI_RAM_CODE_soc7_0_1_1.bin`, `soc7_0_ram_wmmcu_1_1_hdr.bin` | **absent** from vendor | gen4m `soc7_0_ConstructFirmwarePrio/ConstructRomName` | not expected on this board: the exact build has `CFG_WLAN_LK_FWDL_SUPPORT=1` (Kbuild.main), i.e. LK pre-loads the WF image into EMI. The file-name constructors are still compiled in (`apucsoc7_0FwName`), but no file exists in any stock partition. The only runtime proof would be a Wi-Fi-on log, which is not in the capture (Wi-Fi was off) | - |
| `vendor/firmware/wifi.cfg` (21 B: `DisGTKCipherCheck 1`) | vendor | gen4m `wlanCfgParse` | Wi-Fi on | config text |
| `vendor/etc/wifi/nvram/wfnv_desc_{data,map}_soc70.bin` | vendor | `libwifinvram`/`wlan_assistant` | NVRAM init | proprietary descriptor tables |

The kernel driver needs no firmware file of its own on this board. Wi-Fi function depends on the
LK-loaded, MediaTek-signed image, so replacing it is out of scope. The kernel driver's DONE status
does not depend on it.
