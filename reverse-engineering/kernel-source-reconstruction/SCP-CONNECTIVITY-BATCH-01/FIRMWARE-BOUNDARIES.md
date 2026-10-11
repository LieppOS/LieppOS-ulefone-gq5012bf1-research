# Firmware and userspace boundaries (not reconstructed, not inferred)

The 20 modules of this batch are the **normal-world Linux host side only**. Everything below stays
proprietary or out of scope, and no claim about its content is made.

| Boundary | Where it lives | Linux interface (now source-identical) |
|---|---|---|
| SCP RISC-V firmware (sensor drivers, fusion, batching, CHRE, CONAP GNSS offload, audio DSP tasks) | signed `scp` partition, loaded before Linux; `vendor/firmware/remoteproc_scp` is a 32-byte stub | `scp.ko` IPI/mailbox, share memory, recovery notify, coredump |
| CONNSYS Wi-Fi WM firmware + patch | `connsys_wifi_mt6878_mt6637` sub-images (`…ASIC_MT6637-20241028193456`) | `wlan_drv_gen4m_6878` / `conninfra` loader and WFDMA |
| BT controller firmware | `connsys_bt_mt6878_mt6637` | `bt_drv_6878` BTIF/CCIF + HCI to `bluetooth.ko` |
| GNSS MCU firmware, MNL engine, AGPS/SUPL | connsys GNSS image; `mnld`, `libmnl`, `MNL_Config.xml` | `gps_drv_dl_v051` data link, `gps_pwr`, `gps_scp` |
| FM DSP patches/coefficients | connsys FM blobs | `fmradio_drv_connac2x` |
| Wi-Fi NVRAM / RF calibration | per-unit NVRAM (deliberately not read) | `wlan` NVRAM ioctl path |
| Wi-Fi/BT/GNSS HALs, wpa_supplicant/hostapd, `libbluetooth_mtk*` | vendor userspace | char devices / nl80211 |
| Sensors multi-HAL, YFT `sensorcali` | vendor userspace | `/dev/hf_manager` |
| Modem / CCCI firmware | MD image (out of scope; PRESERVE:MODEM) | only the imported CCCI/MDDP symbols, witnessed from ALPS source |

The batch did not change, decode or load any firmware. No radio, SCP or firmware command was issued and
no register was touched. Firmware inventory from prior research: `reverse-engineering/connectivity/firmware/inventory.tsv`.
