# CONNINFRA / CONNSYS core (CONNINFRA-KERNEL)

**Status: CONNINFRA-KERNEL = DONE.** All foundation modules rebuild byte-exact.

| module | role | functions | data | ABI | source |
|---|---|---:|---:|---|---|
| `conninfra.ko` | connv2/connv3 core: power/reset, A-die SPI, EMI, pre-cal, coredump, connsyslog, thermal | 1356/1356 | 523/523 | exact | NothingOSS kernel_modules **2115d27** `connectivity/conninfra` |
| `connadp.ko` | build-in adapter, WMT adapter, connsys power throttling | 76/76 | 47/47 | exact | NothingOSS KDM **6df320423600** `drivers/misc/mediatek/connectivity` (+ `power_throttling` @6df320423600) |
| `connscp.ko` | CONAP ↔ SCP (tinysys IPI, SHM, DFD) | 104/104 | 66/66 | exact | KDM 6df320423600 `drivers/misc/mediatek/conn_scp` |
| `clkbuf.ko` | XO buffer control (`MTK_CONNINFRA_CLOCK_BUFFER_API_AVAILABLE`) | 80/80 | 66/66 | exact | KDM 6df320423600 `drivers/misc/mediatek/clkbuf` |
| `mt6685-core.ko` | MT6685 clock IC MFD (`mt6685-consys` child) | 3/3 | 7/7 | exact | KDM 957dac1 baseline `drivers/mfd/mt6685-core.c` |
| `uarthub_drv.ko` | UART hub (connv3 external combo); **disabled on this board** (`uarthub-disable = <1>`) | 278/278 | 142/142 | exact | KDM 957dac1 baseline (tree = 6df320423600) |

"ABI exact" means imports, exports, modversions (import + export CRCs), modinfo, vermagic and
section sizes all match. KCFI type hashes are part of the compared function bytes. Per-module
TSVs are in `../binary-analysis/per-module/`.

## Exact build environment (proven by parity)

* GKI 6.1.115 `android14-11`, vermagic `6.1.115-android14-11-g945dff7bc1bf`, clang r487747c,
  KDM config with `CONFIG_MTK_COMBO_CHIP_CONSYS_{6878,6897,6983,6985,6989}=y`.
* Source tree at `../vendor/mediatek/kernel_modules/connectivity/`, relative to `common/`. The
  `__FILE__` strings must read `../vendor/mediatek/kernel_modules/connectivity/...`.
* **`TARGET_BUILD_VARIANT` unset.** Proven by `connsys_d_die_cfg_mt6878` writing
  `CONN_INFRA_SYSRAM_SW_CR_BUILD_MODE = 0` (DMESG agrees: `Write CONN_INFRA_SYSRAM_SW_CR_BUILD_MODE
  to 0x00000000`) and by the presence of the `CONNINFRA_DBG_SUPPORT` debug ops
  (`conninfra_dbg_get_chip_info`, `conninfra_dbg_spi_1_read`, ...). A `user` build cannot compile
  (unused-function `-Werror`), and `userdebug` gives BUILD_MODE 2.
* Platforms compiled into stock conninfra: mt6878, mt6897, mt6985, mt6989 (connv2) and mt6639
  (connv3). Only `mt6878_6637_plat_data` binds on this board.

## Source-version history (how the donor was found)

| donor | conninfra functions exact | note |
|---|---:|---|
| NothingOSS 5f75a3b (Tetris U2.6, the only local snapshot) | 1323/1356 | missing `consys_write_bt_rcal_mt6878`, mt6897 VANT18, mt6639 dmp list |
| **2115d27 alps-mp-u0.mp1-V9.9** | 1349 → 1353 (variant unset) → **1356** (correct `__FILE__` path) | exact |
| c3d070e alps-mp-u0.mp1.rc-V11.24 | 1339 | too new |

The full NothingOSS history was fetched blobless into `/home/armol/kernel-work/public-mtk/nkm.git`
(87 commits, 7 branches).

## DT contract (live)

`consys@18000000` (`mediatek,mt6878-6637-consys`, set by LK), 28 MMIO windows, `power-domains =
<&scpsys 1>`, EMI `0x87e00000` + 12 MiB (`ro-bt 0x2e0000`, `ro-gps 0xa0000`, `ro-wifi 0x300000`,
`rw 0x480000`), `hwid-node`/`adie-sku` strap, `#thermal-sensor-cells = <0>` (consys thermal zone,
passive trip 119 °C). PMIC consys children `mt6363-consys`, `mt6369-consys` and `mt6685-consys`
supply VCN13/VRFIO18/VCN33_1/VCN33_2/VANT18 and the 52 MHz co-clock. Reserved memory:
`consys_emi_reserved` 0x87e00000/0xd00000, `wifi-reserve-memory` 0x88b00000/0x1400000,
`consys_scp_emi-reserved` 0x89f00000/0x20000. Details: `../hardware/topology.md`.

## Interfaces exported to children

81 exported symbols (export CRCs exact), e.g. `conninfra_pwr_on/off`,
`conninfra_sub_drv_ops_register`, `conninfra_spi_read/write/update_bits`, `conninfra_spi_1_*`
(GPS A-die), `conninfra_get_phy_addr`, `conninfra_trigger_whole_chip_rst`,
`conninfra_get_ic_info`, `connsys_coredump_*`, `connsys_log_*`, `conninfra_adie_top_ck_en_*`.
Consumers: wlan, bt, fm, gps_drv_dl (`../kernel/dependency-graph.md`).

## Userspace edges

`conninfra_loader` (`/dev/conninfra_dev`) sets `vendor.connsys.driver.ready`. `bt_dump`,
`wifi_dump` and `gps_dump` consume the coredump netlink. `/proc/driver/conninfra_dbg` and
`/dev/conn_dbg_dev` (connadp) take the `0x13 <coredump mode>` command from `init_conninfra.rc`.
