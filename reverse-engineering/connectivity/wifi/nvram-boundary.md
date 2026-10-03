# Wi-Fi NVRAM / calibration boundary

| item | location | consumer | notes |
|---|---|---|---|
| Wi-Fi NVRAM file (per-unit MAC, TX power, calibration) | `/mnt/vendor/nvdata/APCFG/APRDEB/WIFI` (nvdata partition, per-device) | `wlan_assistant` → `/dev/wmtWifi` → `wmt_chrdev_wifi_connac2` → gen4m (`OID_CUSTOM_MTK_NVRAM_RW`, `get/set_nvram_policy`, module param `nvram`) | per-unit; **must not be altered**; not in the stock image |
| XO NVRAM (crystal trim) | read by `wlan_assistant` ("Open XO NVRAM file failed" path) | driver | per-unit |
| MAC fallback | `/data/vendor/macwifi` | `wlan_assistant` | runtime |
| NVRAM layout descriptors | `vendor/etc/wifi/nvram/wfnv_desc_data_soc70.bin` (340,374 B), `wfnv_desc_map_soc70.bin` (19,140 B) | `libwifinvram.so`, `libwifinvramdata.so` | proprietary tables, generic for SOC7_0 |
| boot-time pre-cal | conninfra pre-cal → EMI backup `0x87e00000 + 0xb701a4`, 2048 B (DMESG) | conninfra / gen4m `wlan_precal_*` | regenerated each boot |
| TX power control cfg | `txpowerctrl.cfg` absent ("no txpowerctrl.cfg or file is empty") | gen4m | stock default |
| regulatory | compiled `rlm_domain.c` tables + cfg80211 signed regdb | kernel | the country code comes from the framework |

The NVRAM content is board calibration data, not source. Nothing in this pass reads or writes it.
A read-only inspection plan is in `../runtime-test-plan.md`.
