# Wi-Fi (MT6637-WIFI-KERNEL)

**Status: MT6637-WIFI-KERNEL = DONE.** WIFI-FIRMWARE, WIFI-NVRAM-CALIBRATION and
ANDROID-WIFI-HAL stay proprietary/PARTIAL ([`firmware-boundary.md`](firmware-boundary.md),
[`nvram-boundary.md`](nvram-boundary.md)).

## Kernel modules

| module | functions | data | ABI | source / build |
|---|---:|---:|---|---|
| `wlan_drv_gen4m_6878.ko` | **5682/5682** | **968/968** | exact (imports 389, modversions 390, modinfo 8, 23 sections) | NothingOSS kernel_modules 2115d27 (ALPS mp1-V9.9) **+ 13 hunks from c3d070e (ALPS mp1.rc-V11.24)**, `MODULE_NAME=wlan_drv_gen4m_6878 SEGMENT=SP DRIVER_BUILD_DATE=20251022145214` |
| `wmt_chrdev_wifi_connac2.ko` | 28/28 | 38/38 | exact | 2115d27 `wlan/adaptor/build/connac2x` |
| `cfg80211.ko` | 1435/1435 | 1237/1237 | exact | GKI common `net/wireless` (vendor in-tree build, scm g945dff7bc1bf) |
| `mac80211.ko` | 1420/1420 | 837/837 | exact | GKI common `net/mac80211`; loaded, unused (gen4m is fullMAC) |
| `wifi_cooling.ko` | 8/8 | 7/7 | exact | KDM 6df320423600 |
| `mddp.ko` | 132/132 | 87/87 | exact | KDM 957dac1 baseline (MD direct path / tethering offload) |
| `connfem.ko` | 94/94 | 45/45 | exact | 2115d27 (see `../connfem/`) |

### The 13 V11.24 hunks (stock = V9.9 + these, nothing else)

Patch: `../reconstruction/wlan-gen4m-6878-alps-v11.24-backports.patch`. They were found by
function-level diffing (5654/5682 → 5679 → 5682) and identified by:

| file | hunk | binary evidence |
|---|---|---|
| `common/wlan_oid.c` | `roamingFsmInDecision(prAdapter, FALSE, ucBssIndex)` | `wlanoidFwEventIT` passes `w1=0` (new arg) |
| `include/mgmt/roaming_fsm.h`, `mgmt/roaming_fsm.c` (3) | new `fgIgnorePolicy` parameter; `(policy != CONNECT_BY_BSSID \|\| fgIgnorePolicy)` | `roamingFsmInDecision` size 212 vs 200, KCFI type change |
| `mgmt/ais_fsm.c` (6) | callers + two MLO probe-count resets + `aisScanGenMlScanReq` MLO reset | callers' args; MLO hunks (compiled out, `CFG_SUPPORT_802_11BE_MLO=0`) proven by `__LINE__` shifts (+4, +4, +7 lines) in later `DBGLOG` call sites |
| `nic/que_mgt.c` | NULL check in `qmPopOutDueToFallAhead` | size 756 vs 728 |
| `os/linux/gl_kal.c` | `kalNapiPoll` RX-direct restructure | size 948 vs 1076, −1 line shift for later functions |
| `os/linux/gl_p2p_kal.c` | `if (!prNetdevice) return;` in `kalP2PUpdateAssocInfo` (same as NothingOSS 70caf53 "sap: add dev pointer check") | size 544 vs 532 |

V11.24 hunks that are **not** in stock (and were left out): `kalProcessRadiotap` truesize check,
`kalSkbReuseCheck` reorder, `kalRxIndicateOnePkt` free-on-error, `kalInformFtEvent` MLD NULL
checks, `kalHardStartXmit` NULL check, `kalVnfSendCmd` memzero, `BACKOFF_VOLT` header move,
`roamingFsmSendFtActionFrame` MLD NULL check, `qmHandleRxReorderWinShift` TID bound. This is a
selective ODM/MTK patch drop, not a full V11.24 upgrade.

`DRIVER_BUILD_DATE` is the `$(shell date)` stamp from `Kbuild.main`. The stock value
`20251022145214` is consistent with the vendor build date (2025-10-22).

## Chip / feature contract (build defines of the exact build)

`SOC7_0`, `_HIF_AXI=1`, `CFG_SUPPORT_CONNAC2X=1`, `CFG_SUPPORT_CONNAC2X_2x2=1`, `CFG_WIFI_IP_SET=1`,
`CFG_SUPPORT_802_11AX=1`, `CFG_SUPPORT_WIFI_6G=1`, `CFG_SUPPORT_WIFI_6G_PWR_MODE=1`,
`CFG_SUPPORT_802_11BE=0`, `CFG_SUPPORT_802_11BE_MLO=0`, `CFG_SUPPORT_NAN=1`, `CFG_SUPPORT_TWT=1`,
`CFG_SUPPORT_APF=1`, `CFG_SUPPORT_DBDC_DOWNGRADE_{BW,NSS}=1`, `CFG_SUPPORT_WIFI_DBDC6G=0`,
`CFG_MTK_MDDP_SUPPORT=1`, `CFG_SUPPORT_GET_LTE_SAFE_CHANNEL=1`, `CFG_CHIP_RESET_SUPPORT=1`,
`CFG_POWER_ON_DOWNLOAD_EMI_ROM_PATCH=1`, `CFG_MTK_ANDROID_EMI=1`.

So: **Wi-Fi 6E, 2x2, 2.4/5/6 GHz, STA + P2P + SoftAP (`ap0`, concurrent `ap1`) + NAN + TWT**.
The framework (live `dumpsys wifi`) reports STA+STA and STA+AP concurrency and
`WIFI_FEATURE_AWARE/PNO/TDLS/MOBILE_HOTSPOT/AP_STA`.

* Bus/transport: AXI/WFDMA inside the SoC (`wifi@18400000`, IRQ 484/692, `remap-idx 1`), EMI
  20 MiB DMA pool `wifi-reserve-memory` 0x88b00000.
* conninfra: `conninfra_sub_drv_ops_register` (pre-cal, reset, thermal), `conninfra_pwr_on`,
  `connsys_coredump_*`, connsys log, connadp power throttling.
* Country code / regulatory: `rlm_domain.c` tables compiled into the driver (V9.9 tables;
  NothingOSS's later country-code commits are absent). `cfg80211` requires a signed regdb
  (`CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y`). `txpowerctrl.cfg` is absent ("no txpowerctrl.cfg").
* MAC provisioning: `wlan_assistant` reads NVRAM `/mnt/vendor/nvdata/APCFG/APRDEB/WIFI`
  (fallback `/data/vendor/macwifi`) and writes it to the driver through `/dev/wmtWifi`.
* Suspend/WoW: `CFG_WOW_SUPPORT=1` (`include/config.h` default) and 19 WoW functions in the stock
  module. Runtime WoW configuration is not proven offline.
* Hotspot: SoftAP through cfg80211 `ap0`; hostapd `android.hardware.wifi.hostapd-V1`; MDDP
  offload to the modem for tethering.

## Rebuild

`scripts/build_ext.sh wlan/core/gen4m MODULE_NAME=wlan_drv_gen4m_6878 SEGMENT=SP
DRIVER_BUILD_DATE=20251022145214` (tree commit `7de5e1c` in
`$G/vendor/mediatek/kernel_modules/connectivity`).
