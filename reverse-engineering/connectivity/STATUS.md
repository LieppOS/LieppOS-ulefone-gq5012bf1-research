# Connectivity status (2026-10-03)

Totals: **20 connectivity modules, 13,221/13,221 functions, 4,587/4,587 data objects, every ABI
check exact**. A further 9 power_throttling dependency modules are exact (200/200, 191/191).

| named scope | status | basis | what is outside the scope |
|---|---|---|---|
| CONNINFRA-KERNEL | DONE | conninfra 1356/1356 523/523; connadp 76/76 47/47; connscp 104/104 66/66; clkbuf 80/80 66/66; mt6685-core 3/3 7/7; uarthub_drv 278/278 142/142; DT contract + EMI/reserved-memory/SKU logic mapped | connsys MCU firmware |
| FM-KERNEL | DONE | fmradio_drv_connac2x 365/365 79/79; DT `fm`/`fmradio` contract; digital CONNSYS-I2S audio route proven | FM DSP patch/coeff blobs, YFT FM app/JNI, audio HAL. FM-RADIO-HEADSET keeps physical LNA/antenna matching |
| MT6637-WIFI-KERNEL | DONE | wlan 5682/5682 968/968; wmt_chrdev 28/28 38/38; cfg80211 1435/1435 1237/1237; mac80211 1420/1420 837/837; wifi_cooling 8/8 7/7; mddp 132/132 87/87 | WIFI-FIRMWARE (connsys_wifi image), WIFI-NVRAM-CALIBRATION, ANDROID-WIFI-HAL, supplicant/hostapd |
| MT6637-BT-KERNEL | DONE | bt_drv_6878 294/294 118/118; bluetooth 1257/1257 153/153; mtk-btcvsd 32/32 18/18; BTIF transport/no-hci0 proven | BT-CONTROLLER-FIRMWARE, BT-VENDOR-HAL (`libbluetooth_mtk*`, BT audio HAL) |
| GNSS-KERNEL-TRANSPORT | DONE | gps_drv_dl_v051 550/550 126/126; gps_pwr 12/12 10/10; gps_scp 15/15 13/13; connscp (above) | connsys_gnss firmware, mnld/libmnl, AGPS/SUPL, GNSS HAL |
| CONNFEM | DONE | connfem 94/94 45/45, export CRCs 8/8 (previously 7/8 with a hand reconstruction); nofem/nofem board selection | antenna/PCB (RF-ANTENNAS, BLOCKED) |
| MT6637-WIFI (whole) | PARTIAL | kernel split out to DONE | proprietary firmware, NVRAM, HAL; radio performance |
| BLUETOOTH (whole) | PARTIAL | kernel split out to DONE | controller firmware, HAL, live feature validation |
| GNSS (whole) | PARTIAL | kernel split out to DONE | engine/firmware, runtime characterisation |
| FM-RADIO-HEADSET | PARTIAL | headset side (audio pass) + FM kernel (this pass) closed | physical LNA/antenna matching, RF performance |
| RF-ANTENNAS | BLOCKED | software side complete | teardown |

## Remaining physical/runtime blockers

1. Antenna count/placement/feeds (teardown).
2. Literal strap GPIO levels 92/131/132 (inferred). A read-only check is in
   `runtime-test-plan.md`.
3. FM LNA part behind GPIO 72 and its RF matching (teardown).
4. Runtime confirmation of the LK-preloaded Wi-Fi image path (the capture had Wi-Fi off).
5. Per-unit NVRAM/calibration content (deliberately not read).

## Organized workspace (`Reverse Engineer - *`)

* Moved PARTIAL → DONE: `CONNFEM` (the hand reconstruction was superseded by the exact V9.9
  source).
* New DONE scopes: `CONNINFRA-KERNEL`, `FM-KERNEL`, `MT6637-WIFI-KERNEL`, `MT6637-BT-KERNEL`,
  `GNSS-KERNEL-TRANSPORT`.
* Still PARTIAL, with updated READMEs pointing at the kernel scopes: `MT6637-WIFI`,
  `BLUETOOTH`, `GNSS`, `FM-RADIO-HEADSET`.
* Totals after this pass: DONE 39, PARTIAL 77, BLOCKED 6 (folder counts).

## Shared KDM tree side effect (for the power workstream)

Research KDM commit `05f8044` moves `drivers/misc/mediatek/power_throttling` to NothingOSS
6df320423600: 6-level `LOW_BATTERY` enum, `LBAT_INTR_1/2`, `HPT`. This was required for connadp
parity. It also makes 9 power modules exact: mtk_low_battery_throttling 52/52 46/46,
pmic_lbat_service 28/28 22/22, mtk_bp_thl 17/17 18/18, mtk_battery_oc_throttling 22/22 16/16,
mtk_dynamic_loading_throttling 10/10 12/12, mtk_md_power_throttling 8/8 6/6,
mtk_cpu_power_throttling 27/27 32/32, mtk_gpu_power_throttling 27/27 31/31, pmic_lvsys_notify
9/9 8/8. `mtk_bp_thl.h` is unchanged, and it already contains the audio pass's
`BATTERY_PERCENT_PRIO_AUDIO = 9`. `pbm`, `power/supply` and `ufs` still compile. `mtk_pbm`
stays exact at 31/31 39/39.
