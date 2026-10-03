# GNSS firmware / userspace boundary

| item | where | loader / consumer | source |
|---|---|---|---|
| `connsys_gnss` image (523,368 B, sha256 body `7ad6007c…db68`; partition sha256 `e118764a…55c4`) | partition `connsys_gnss` | LK `platform_load_connsys` → GPS EMI 0x88a00000, signed | proprietary |
| `mnld`, `libmnl.so`, `libDR.so`, `libladder.so` | vendor | MNL daemon (position engine) | proprietary |
| `mtk_agpsd`, `mtk_lbs_service`, AGPS carrier profiles | vendor | SUPL/LPP/RTCM | proprietary (XML is config) |
| `android.hardware.gnss-service.mediatek` + `-impl` libs | vendor | AIDL GNSS HAL | proprietary |
| `MNL_Config.xml` | vendor/etc | mnld | config (IFB, GGTO, DCB per chip) |
| GNSS NVRAM / per-unit data | nvdata (`libnvram` linked by mnld) | mnld | per-unit, untouched |

The kernel transport (`gps_drv_dl_v051`, `gps_pwr`, `gps_scp`, `connscp`) is exact. The engine,
firmware and assistance stack have no source.
