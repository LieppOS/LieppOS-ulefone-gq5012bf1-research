> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> There is **no external Wi-Fi/BT front-end module** (ConnFem resolves to `nofem + nofem`), and the LE-Audio properties came from a **GSI**, not stock. See `connfem-selected-fem.md` and `bluetooth.md`.

# Wi-Fi and Bluetooth

## Hardware found

* Connectivity ADIE chip ID is **0x6637** for both `vendor.connsys.wifi.adie.chipid` and `vendor.connsys.gps.adie.chipid`; the WLAN character device is `wmt_chrdev_wifi_connac2`. This proves a MediaTek MT6637-class connectivity die, even though a public MT6637 datasheet was not found.
* Stock services/modules: `connsys_wifi`, `connsys_bt` firmware paths, MediaTek Wi-Fi HAL, Bluetooth audio HAL, `wificond`, and vendor NVRAM (`Ready:1,6144`).
* RF front-end is selected through `mediatek,mt6878-connfem` / `epa-elna-mtk`; the catalog contains `nofem`, `wlan7207h/c`, Qorvo `qm42195/qm45197`, Skyworks `sky85320/sky85720/sky85732/sky85743`, `mxd7751s`, `rtc7620`.

## Capability layer

* Platform/OEM material identifies Wi-Fi 6E class operation and Bluetooth 5.x; the exact MT6637 feature ceiling and BT revision are not publicly substantiated here.
* Candidate FEMs are 2.4/5/6 GHz Wi-Fi 6E/7 front ends with LNA/PA/switch functions, but the physically selected candidate is UNKNOWN.
* Android stack supports Wi-Fi station/AP/hotspot, Wi-Fi Direct and suspend; GSMArena lists Wi-Fi 6E-class WLAN and Bluetooth A2DP/BLE/aptX-HD-class features.

## Board configuration / stock use

* `wifi`/`wifinl80211`/`wificond` services are present; snapshot mode was disabled, so no association, channel width, MCS or 6-GHz scan was measured.
* AP interfaces are configured as `ap0` and concurrent `ap1`; `ro.vendor.wifi.sap.concurrent.iface=ap1`.
* Bluetooth service had crashed zero times but was **never enabled** in the snapshot; codec negotiation, LE Audio, antenna diversity and throughput are UNKNOWN.
* ConnFem has three HWID GPIOs (131/132/92), providing eight hardware selections. Stock contract maps some HWIDs to BT ePA/eLNA and others to bypass; Wi-Fi flag indexing is unresolved.

## Hidden / unused

1. 6-GHz Wi-Fi 6E, wider channels and 2×2/MIMO capabilities may be physically available but cannot be claimed without runtime scan/throughput.
2. Candidate FEM catalog and HWID table support alternate RF population/board variants.
3. BT LE Audio/Auracast and aptX-HD are stack/platform possibilities, not proven active with BT disabled.

## Verification

Read runtime ConnFem HWID GPIO values and selected part table; enable Wi-Fi and run 2.4/5/6-GHz scans plus iperf; enable BT and capture `dumpsys bluetooth_manager`, codec list and LE feature mask; inspect RF shields/FEM markings.

Sources: S01–S07, S20; findings L15 and props `vendor.connsys.*`.
