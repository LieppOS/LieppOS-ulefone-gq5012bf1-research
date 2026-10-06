# Stock load order by subsystem (normal boot)

Source: `resolved-load-order.tsv` (443 insertions, simulated with AOSP libmodprobe rules;
total and membership equal to the captured stock `/proc/modules`). Subsystem buckets are
name-regex groupings (approximate; `scripts/subsystem_summary.py`); seq = global insertion index.

| subsystem | modules | seq range | phase split |
|---|---:|---|---|
| debug/aee/boot-profiling | 20 | 1–181 | first-stage 20 |
| clock/power-domain/pinctrl/PMIC/regulator | 62 | 13–423 | first-stage 51, vendor 11 |
| storage (UFS/MMC/RPMB/blocktag) | 9 | 115–124 | first-stage 9 |
| display/GPU/MM | 50 | 9–436 | first-stage 34, vendor 16 |
| input/touch/keys/fp | 9 | 183–440 | first-stage 4, vendor 3, init.touch.rc 2 |
| power/charging/battery/Type-C | 32 | 85–333 | first-stage 22, vendor 10 |
| USB | 28 | 99–438 | first-stage 7, system_dlkm 13, vendor 8 |
| camera/ISP/flash/codec | 33 | 40–407 | first-stage 1, vendor 32 |
| audio | 16 | 87–352 | first-stage 2, vendor 14 |
| connectivity (WiFi/BT/GPS/FM/NFC) | 23 | 97–442 | first-stage 2, system_dlkm 8, vendor 11, rc insmod 2 |
| modem/CCCI | 10 | 204–376 | system_dlkm 1, vendor 9 |
| sensors/SCP/tinysys | 12 | 59–392 | first-stage 6, vendor 6 |
| TEE/security | 16 | 16–425 | first-stage 5, system_dlkm 1, vendor 10 |
| other | 123 | 14–443 | first-stage 24, system_dlkm 37, vendor 61, rc 1 |

Landmarks (seq): `bootprof` 1, `clk-mt6878` 23, `mt6363-regulator` 38, `mtk-smi` 54,
`iommu_secure` 70, `mediatek-drm` 89, `8250_mtk` 98, UFS/RPMB 115–124, `sh366003_fg` 146,
`sc851x/sc8571` 158–159, `microarray_fp_tee` 186 (end of first stage at 187);
system_dlkm 188–247; vendor pass starts 248 (`gz_trusty_mod` 258, `apusys` 302,
`mt6878-mt6369` 323, `custom_ldo_wl2868` 363, `mtk_cam_isp7sp` 365, `imgsensor` 368,
`spi_tiny_co5300_lcd` 436, `yft_tiny2c_usb` 438); touch 439–440; rc insmod 441–443.

Shipped-but-not-loaded and dependency-only classes: `module-classification.tsv`
(457 unique shipped: 183 first-stage listed, 4 first-stage dependency-only, 250
second-stage listed, 6 rc/service, 14 never loaded; 14 duplicates across partitions).
