# GQ5012BF1 connectivity hardware topology

Static/offline result. Evidence classes: **DT** = stock merged DTS
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`), **LDT** = live device tree
from the read-only capture `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`,
**DMESG** = same capture's `dmesg.txt`, **SRC** = exact-parity source (see `../kernel/source-map.tsv`),
**LK** = strings of `stock/firmware/lk.img`.

## Block diagram (proven)

```
                       MT6878 SoC (Dimensity 7300 class)
 +-------------------------------------------------------------------------------+
 |  AP (Linux)                                                                   |
 |   conninfra.ko ---- connv2 "SOC7_0" CONNSYS (D-die, inside MT6878)            |
 |     |   MMIO 0x18000000.. (conn_infra), 0x18400000 WF, 0x18800000 BGF/BT,     |
 |     |   0x18c00000 GPS, 0x1c000000 conn_infra_on/TIA2                          |
 |     |   EMI: consys_emi_reserved 0x87e00000 (13 MiB: 12 MiB connsys + 1 MiB GPS)|
 |     |        wifi-reserve-memory DMA pool 0x88b00000 (20 MiB)                 |
 |     |        consys_scp_emi-reserved 0x89f00000 (128 KiB)                     |
 |     +-- wlan_drv_gen4m_6878 (WF WM MCU, WFDMA over AXI)  IRQ 484, 692          |
 |     +-- bt_drv_6878 (BGF MCU over BTIF/CCIF)             IRQ 693, 132          |
 |     +-- gps_drv_dl_v051 (GPS MCU / data link)            IRQ 379-383, 389, 129 |
 |     +-- fmradio_drv_connac2x (FM core in A-die)          IRQ 486               |
 |     +-- connscp/gps_scp (CONAP on SCP over tinysys IPI)                         |
 |     +-- AFE "Connsys I2S" input  <==== FM digital audio (see ../fm/route.md)    |
 +----------------|--------------------------------------------------------------+
                  | A-die SPI (conninfra_spi_*), RF/clock, 52 MHz co-clock
           +------+------------------------+
           |  MT6637 A-die (RF companion)  |  chip id 0x66378a01 (DMESG)
           |  WF0/WF1 2x2 (2.4/5/6 GHz)    |  BT, GNSS (L1+L5), FM RX
           +------+------------------------+
                  | no external ePA/eLNA (ConnFem nofem/nofem, ../connfem/README.md)
               antennas (physical layout BLOCKED - teardown)

 PMIC rails used by connsys (SRC mt6878_pmic.c + DMESG consys_pmic_debug_log_mt6878):
   VCN13, VRFIO18, VCN33_1, VCN33_2, VANT18 (VANT18 read 0 at capture time)
 Co-clock: MT6685 clock IC (mt6685-consys child, mt6685-core.ko), DMESG
   "conf->tcxo_gpio=0 conn_hw_env.tcxo_support=0, 52M co-clock"
```

## Platform capability vs. enabled on this board

| item | platform capability (source/DT reference) | GQ5012BF1 actual | evidence |
|---|---|---|---|
| CONNSYS generation | connv2, SOC7_0 (CONNAC2X); conninfra.ko also carries mt6897/mt6985/mt6989 + connv3 mt6639 code | MT6878 connv2 only; `Consys HW version id(0x02050401)` | DMESG, SRC |
| A-die SKU | `mt6878-6637-consys`, `mt6878-6631-consys`, `mt6878-6631-6686-consys` | **6637** (LK rewrites compatible at boot; static DTB says 6631) | LDT compatible, LK strings, DMESG `A-die chip id: 0x66378a01` |
| SKU strap | reference `hwid-node=<92>; adie-sku=<0 1>` (`mt6637 = 0, mt6631 = 1`) | `hwid-node=<92 132 131>`, `adie-sku=<1 1 0 0 2 2 1 0>` | DT/LDT vs `kernel_device_modules-6.1/arch/arm64/boot/dts/mediatek/mt6878.dts:11091` |
| external GNSS A-die (MT6686) | supported (6631+6686 SKU) | not used (SKU 6637) | LDT, LK |
| Wi-Fi | gen4m CONNAC2X 2x2, 11ax, 6 GHz, NAN, TWT, APF, MDDP | all compiled in (`CFG_SUPPORT_WIFI_6G=1`, `CFG_SUPPORT_CONNAC2X_2x2=1`, `CFG_SUPPORT_802_11AX=1`, `CFG_SUPPORT_802_11BE=0`) | build defines of exact-parity build |
| FEM | 7 ePA/eLNA pairings in DT | nofem/nofem | DMESG `connfem_is_available: FEM is not available` |
| uarthub (BT UART hub for external combo) | driver loaded | `uarthub-disable = <1>` | DT |
| FM | A-die FM RX, I2S to AFE | enabled, LNA enable GPIO 72, antenna = headset cable (GPIO 195 switch) | LDT `fmradio/fm_lna_gpio`, audio research |
| SCP offload (CONAP) | connscp + gps_scp, geofence/batching | loaded; `connscp` node `mediatek,mt6897-conn_scp`, 128 KiB SHM | DT, init.gps_scp.rc |
| thermal | consys thermal sensor (A-die), wifi cooler | `consys` thermal zone, passive trip 119 °C; `wifi-cooler` node | DT |

## MMIO / IRQ map (live DT)

| node | compatible | reg (base,size) | interrupts (GIC SPI) |
|---|---|---|---|
| `consys@18000000` | `mediatek,mt6878-6637-consys` (live) | 28 windows: 0x18000000/0x470, 0x10001000/0xee4 (infracfg), 0x10005000/0xa7c (GPIO), 0x11ec0000/0xa04, 0x18001000..0x1807xxxx conn_infra blocks, 0x1c001000, 0x1c00a000, 0x1803c000, 0x1803e000 | - |
| `wifi@18400000` | `mediatek,wifi` | 0x18400000 (remap-idx 1), 0x18000000/0x700000 | 484, 692 |
| `bt@18800000` | `mediatek,bt` | 0x18800000, 0x18000000, 0x18001000, 0x18051000, 0x18060000, 0x18812000, 0x10001000 (4 KiB each) | 693, 132 |
| `gps@18c00000` | `mediatek,mt6878-gps` | conn_gps_base 0x18c00000/1 MiB, conn_infra_base, status_dummy_cr 0x1c000000, tia2_gps_on/rc_sel/debug 0x1c0130xx | 379,380,381,382,383,389,129 |
| `fm` | `mediatek,fm` (family-id 0x6983, host-id 0x6878, conn-id 0x205) | - | 486 |
| `fmradio` | `mediatek,fmradio` | `fm_lna_gpio = <&pio 72 0>`, status okay | - |
| `connscp` | `mediatek,mt6897-conn_scp` | scp-shm 0x20000, remap offset 0x2100000 | - |
| `connfem` | `mediatek,mt6878-connfem` | 7 pinctrl states, HWID GPIOs 131/132/92 | - |
| `uarthub` | `mediatek,mt6878-uarthub` | `uarthub-disable = <1>` | - |

## Power / reset / boot sequence (SRC + DMESG)

1. **LK** (`app_load_connsys`): reads `hwid-node` GPIOs, indexes `adie-sku`, sets
   `compatible = "mediatek,mt6878-6637-consys"`, writes `emi-addr` (connsys 0x87e00000, GPS
   0x88a00000), loads the signed `connsys_bt_mt6878_mt6637`, `connsys_wifi_mt6878_mt6637` and
   `connsys_gnss` images from the `connsys_*` partitions into connsys EMI (see
   `../firmware/inventory.tsv`).
2. **conninfra.ko** probes `mt6878_6637_plat_data` (`g_consys_hw_ops_mt6878_6637`: A-die 6637
   thermal formula, `consys_adie_detection_adie6637_mt6878`, pre-cal backup/restore).
3. `conninfra_loader` (vendor/bin, `/dev/conninfra_dev`) triggers driver-ready
   (`vendor.connsys.driver.ready`) and init `insmod`s `bt_drv_6878`, `gps_pwr`, `gps_scp`.
4. On first unblank conninfra runs **pre-calibration**: BT on → Wi-Fi on → BT cal → Wi-Fi cal →
   RF CR backup to EMI (`consys_pre_cal_backup_mt6878 emi base=0x87e00000 offset=0xb701a4 size=2048`).
5. Sub-drivers (`sub_drv_ops`) power on/off through `conninfra_pwr_on/off`; whole-chip reset via
   `conninfra_trigger_whole_chip_rst`; coredump to EMI + netlink (`conndump_*`, `bt_dump`,
   `wifi_dump`, `gps_dump` daemons).

## What remains physical/runtime

* Antenna count/placement, RF matching, shield cans — BLOCKED (teardown), see `rf-front-end.md`.
* Literal level of GPIO 92/131/132 (inferred, see `mt6637.md`).
