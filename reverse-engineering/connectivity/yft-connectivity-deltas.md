# Ulefone / YFT connectivity deltas (GQ5012BF1)

The headline result: **no connectivity kernel module contains Ulefone/YFT source changes.**
Every module rebuilds byte-exact from public MediaTek code published by NothingOSS: kernel_modules
2115d27 = ALPS mp1-V9.9, KDM 6df320423600, and GKI common. The board identity lives in DT,
configuration files, the build environment and the MTK patch level. Confidence levels:
**PROVEN** (binary/DT/log), **STRONG** (consistent multi-source inference), **MEDIUM**.

| # | area | upstream / reference behaviour | GQ5012BF1 behaviour | evidence | reconstruction | confidence |
|---|---|---|---|---|---|---|
| 1 | A-die SKU strap | MTK `mt6878.dts`: `hwid-node = <92>; adie-sku = <0 1>` (mt6637 = 0, mt6631 = 1) | `hwid-node = <92 132 131>; adie-sku = <1 1 0 0 2 2 1 0>`. LK binds **6637** (live `mediatek,mt6878-6637-consys`) | DT, LDT, LK strings, DMESG A-die 0x66378a01 | DT values (no code) | PROVEN |
| 2 | strap levels | - | GPIO132 = 1, GPIO131 = 0, GPIO92 = 0 (ConnFem HWID 2 ⇒ nofem/nofem; consys index 2 ⇒ SKU 6637) | `hardware/mt6637.md` cross-check | - | STRONG |
| 3 | ConnFem | reference options | 7 FEM pairings listed; board resolves to **no external FEM** | DMESG `FEM is not available`, `connfem.cfg` 0 B | DT only | PROVEN |
| 4 | FM LNA | no `mediatek,fmradio` node in the MTK/NothingOSS DTS trees | `fmradio { fm_lna_gpio = <&pio 72 0>; status = "okay"; }`. The FM driver drives GPIO 72 high/low on power up/down | LDT, `fm_module.c` | DT only | PROVEN (node); MEDIUM (that GPIO 72 is an LNA/antenna enable on the PCB) |
| 5 | FM antenna | - | headset-cable antenna switched by GPIO 195 in `mt6369-accdet` (audio pass) | audio research | `../audio/yft-audio-deltas.md` | PROVEN |
| 6 | FM tuning | MTK defaults | `fm_cust.cfg`: RSSI long/short −296, desense −240, SMG 16421, de-emphasis 50 µs, OSC 26 MHz | vendor/firmware | config | PROVEN (file); provenance MTK-vs-YFT unknown |
| 7 | Wi-Fi config | `DisGTKCipherCheck` default 0 (`wlan_lib.c:7827`) | `wifi.cfg`: `DisGTKCipherCheck 1`, so HT/VHT/HE are kept when only the *group* cipher is TKIP/WEP (`bss.c:286`) | vendor/firmware | config | PROVEN |
| 8 | Wi-Fi driver patch level | NothingOSS products: V9.9 + Nothing patches (country code, 6 GHz disable on Tetris) | V9.9 + 13 selected ALPS V11.24 hunks, no Nothing patches, **6 GHz enabled** | function parity 5682/5682 | `reconstruction/wlan-gen4m-6878-alps-v11.24-backports.patch` | PROVEN |
| 9 | kernel_modules build variant | MTK user builds set `TARGET_BUILD_VARIANT=user` | **unset**: conninfra `CONNINFRA_DBG_SUPPORT=1`, `CONNINFRA_PLAT_BUILD_MODE=0`; bt `FW_LOG_DEFAULT_ON=1`, `BUILD_QA_DBG=1` (debug ops present in a user ROM) | parity + DMESG BUILD_MODE 0 | `scripts/build_ext.sh` (`TBV` empty) | PROVEN |
| 10 | Wi-Fi build stamp | `$(shell date)` | `DRIVER_BUILD_DATE=20251022145214` | `priv_driver_get_version` string | make var | PROVEN |
| 11 | BT config | MTK template | `BT_FW.cfg`: coex all 0, `bt_antswap[6878][6631]: 0x84 0x01 0x03` (never matched on the 6637 board), `bt_tssi_from_wifi 3`, `bt_tssi_target 3776` | vendor/firmware + DMESG "Ignore antswap setting" | config | PROVEN |
| 12 | conninfra config | - | `conninfra.cfg`: `co_clock_flag=1`. Clock = PMIC DCXO 52 MHz CO-TMS (no TCXO: `tcxo_gpio=0`, `tcxo_support=0`) | vendor/firmware, DMESG, `mt6878_soc.c` | config | PROVEN |
| 13 | GNSS calibration | MTK template | `MNL_Config.xml` IFB per channel, GGTO offsets, L5 DCB for chips 6637/6686, `L1Only=0` | vendor/etc | config | PROVEN (file); per-board origin MEDIUM |
| 14 | FM / GPS apps | MTK FMRadio, EM GPS | `YftFmRadio.apk` + `libyftfmjni.so`, `YGPS.apk` (system_ext) | partitions | userspace (proprietary) | PROVEN |
| 15 | firmware set | - | connsys partitions carry both 6631 and 6637 images; LK selects 6637 | `firmware/inventory.tsv` | - | PROVEN |
| 16 | KDM connectivity/power level | research tree was at the NothingOSS 957dac1 baseline for these dirs | stock = KDM 6df320423600 (Galaga V3.2 sync) for `connectivity`, `conn_scp`, `clkbuf`, `wifi_cooling.c`, `power_throttling` (6-level `LOW_BATTERY` enum) | parity | KDM commits `e4b5575`, `05f8044` | PROVEN |

There is no evidence of a YFT change to regulatory/country code, MAC derivation, firmware naming,
power sequencing or subsystem enablement beyond the rows above.
