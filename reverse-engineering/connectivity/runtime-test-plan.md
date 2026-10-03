# Future read-only runtime checks (not executed)

Everything here is **read-only**: no transmission control, no NVRAM, calibration, regulatory or
firmware writes. Run only on a stock, rooted boot that the owner explicitly authorises.

| goal | command (read-only) | expected |
|---|---|---|
| strap GPIOs | `cat /sys/kernel/debug/gpio \| grep -E 'gpio-(92\|131\|132) '` | 92 = lo, 131 = lo, 132 = hi (`hardware/mt6637.md`) |
| ConnFem HWID log | `dmesg \| grep -i 'GPIO(1[23][12])\|hwid'` | `hwid(2)` |
| live SKU | `cat /proc/device-tree/consys@18000000/compatible` | `mediatek,mt6878-6637-consys` |
| FM LNA GPIO | during user-initiated FM listening: `cat /sys/kernel/debug/gpio \| grep 'gpio-72 '`; `dmesg \| grep 'gpio_set_value 72'` | 72 = hi while FM on, lo after |
| FM audio route | while FM plays on the headset: `tinymix \| grep -E 'CONNSYS_I2S\|HW_GAIN0\|ADDA_DL'` | `HW_GAIN0_IN_CH* CONNSYS_I2S_CH*` = 1, `ADDA_DL_CH* HW_GAIN0_OUT_CH*` = 1 |
| FM ROM version | `dmesg \| grep -i 'ROM version\|load firmware'` | `v1`, `mt6635_fm_v1_patch.bin ok` |
| Wi-Fi FW origin | after a user turns Wi-Fi on: `dmesg \| grep -iE 'wmmcu\|patch is not downloaded\|WIFI_RAM'` | no `request_firmware` failure; LK-preloaded image |
| Wi-Fi capability | `iw phy` (read) | 2x2, HE, 6 GHz channels per the regdomain |
| BT path | `ls -l /dev/stpbt`; `cat /proc/stpbt/bt_fw_version` | node present; `...BT_BWH_OFF-20241028193456` |
| GNSS | `ls -l /dev/gpsdl0 /dev/gps_emi /dev/gps_pwr /dev/gps2scp` | present |
| loaded modules | `cat /proc/modules \| grep -E 'conn\|wlan\|bt_drv\|gps\|fmradio\|cfg80211\|mac80211'` | match `kernel/module-inventory.tsv` |
