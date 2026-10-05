# YFT / Ulefone USB deltas (GQ5012BF1 vs MTK ALPS mt6878 reference)

The donor is MTK ALPS `5e415e059253` (NothingOSS mt6878 KDM history), with its `mt6878.dts` and TCPC 2.0.31_MTK (the TCPC-CLASS research). Every row is proven from stock binaries or the effective/live DT.

| area | donor behaviour | GQ5012BF1 behaviour | evidence | source/config difference | confidence |
|---|---|---|---|---|---|
| extcon OTG VBUS path | `set_vbus` = MT6375 regulator only | also drives **GPIO 37 `otg_gpio_select`** high/low around the regulator, logging "YFT_OTG_yft_otg_gpio set_high/low" | `extcon-mtk-usb.ko` 22/22 exact after patch 0002; DTBO `otg_gpio_select = <&pio 37 0>` | patch 0002 + DTBO | **proven** |
| ID-pin accessory | GPIO ID low = OTG cable: VBUS on + HOST | ID (GPIO 28) low = **internal thermal camera**: GPIO 152 `uvc_vbus_gpio`=1, GPIO 55 `uvc_switch_gpio`=1, `uvc_insert_status`=1, HOST. **The MT6375 OTG VBUS is not enabled** | exact rebuild; runtime thermal capture (1-1, HS) | patch 0002 + DTBO | **proven** |
| role gating | none | all TCPC/psy/ID role changes are suppressed while `yft_usb_flag == 1` (exported by `mt6375-charger.ko`) | exact rebuild (import `yft_usb_flag`) | patch 0002 | **proven** (the producer semantics of `yft_usb_flag` live in the charger research) |
| thermal sysfs | — | `/sys/class/yft_extcon/tiny2c_mode` (W: 1 = HOST, else NONE; R: always 0, stock bug), `/sys/devices/platform/extcon-usb/uvc_insert_status` (R) | exact rebuild; `init.yft.rc` chmods; SELinux `sysfs_yft_file` | patch 0002 | **proven** |
| extcon DT | `vbus-voltage = 5000000` | **5250000** (5.25 V OTG) | effective DT vs donor DTS | board DT | **proven** |
| extcon DT | no GPIOs | `id-gpios` 28, `otg_gpio_select` 37, `uvc_switch_gpio` 55, `uvc_vbus_gpio` 152; `status = "okay"` from DTBO | DTBO | board DT | **proven** |
| Type-C mux node | not present in mt6878 reference | `/soc/typec-mux-switch` (`orientation-switch`, `mode-switch`, `accessory`, endpoint ↔ tcpc) added. **No mux IC below it** (pass-through) | live DT; `mux_switch.ko` exact, no `mtk_typec_*_register` callers | board DT | **proven** |
| rt_pd_manager | ALPS 2.0.30-era: `vsc_status` struct print; no ALERT_RATELIMITED/PROTECTION; WD0 always | 2.0.31 + vendor: bitmask print, ALERT_RATELIMITED log, PROTECTION = detach, **WD0 skipped in bootmode 8/9** | 11/11 exact after patch 0001 | patch 0001 (the bootmode-skip form matches Xiaomi MTK BSP drops, so this is a vendor-wide TCPC drop, not necessarily YFT-authored) | **proven** (code); source comments unknown (srcversion) |
| TCPC DT | `en-fod`, `en-typec-otp` set | **removed** (FOD and Type-C OTP off) | effective DT vs donor | board DT | **proven** |
| MTU3 / xHCI / XS-PHY / usb_boost / usb_logger / usb_offload / usb_meta / RNDIS | — | **no delta**: byte-exact ALPS; MTU3/PHY DT nodes identical to donor | parity | — | **proven** |
| USB2-only | donor also U2-only (`maximum-speed = "high-speed"`, U2 PHY) | identical; additionally the **hardware IP reports 0 U3 ports** | kmsg + exact source | none (SoC) | **proven** |
| gadget defaults | MTK `init.mt6878.usb.rc` template | VID 0x0E8D, manufacturer/product from props (Ulefone / Armor 29 Pro), KPOC midi, `ro.vendor.usb.kpoc_adb=0` | stock vendor | product config | **proven** |
| dead userspace | — | `init.yft.rc` chmods `/sys/devices/platform/soc/11211000.usb1/mode` (no such device) | DT + rc | product config | **proven** |
