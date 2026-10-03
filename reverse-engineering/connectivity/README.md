# GQ5012BF1 connectivity stack — static reverse engineering

Offline/static only: no adb, no device state changes, no RF transmission, no NVRAM writes. The
live facts quoted below come from the earlier read-only capture
`workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649`.

## Result in one table

| scope | status | modules | functions | data | ABI |
|---|---|---:|---:|---:|---|
| CONNINFRA-KERNEL (conninfra, connadp, connscp, clkbuf, mt6685-core, uarthub_drv) | **DONE** | 6 | 1897/1897 | 851/851 | exact |
| FM-KERNEL (fmradio_drv_connac2x) | **DONE** | 1 | 365/365 | 79/79 | exact |
| MT6637-WIFI-KERNEL (wlan_drv_gen4m_6878, wmt_chrdev_wifi_connac2, cfg80211, mac80211, wifi_cooling, mddp) | **DONE** | 6 | 8705/8705 | 3174/3174 | exact |
| MT6637-BT-KERNEL (bt_drv_6878, bluetooth, mtk-btcvsd) | **DONE** | 3 | 1583/1583 | 289/289 | exact |
| GNSS-KERNEL-TRANSPORT (gps_drv_dl_v051, gps_pwr, gps_scp) | **DONE** | 3 | 577/577 | 149/149 | exact |
| CONNFEM (connfem) | **DONE** | 1 | 94/94 | 45/45 | exact |
| power_throttling dependencies (9 modules) | exact (dependency) | 9 | 200/200 | 191/191 | exact |
| Wi-Fi/BT/GNSS firmware, NVRAM/calibration, HALs/daemons, FM DSP patch | PARTIAL (proprietary) | - | - | - | - |
| antenna/RF physical layout | BLOCKED (teardown) | - | - | - | - |

Per-module numbers: [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv). Raw parity:
`binary-analysis/{function,data,abi}-parity.tsv` and `binary-analysis/per-module/`. Full
reproduction: `scripts/rebuild_all.sh` (log in `binary-analysis/rebuild-all-parity.txt`).

## Key findings

1. **Silicon:** MT6878 integrated CONNSYS (connv2 / SOC7_0 / CONNAC2X, HW ver 0x02050401) +
   **MT6637 A-die** (chip id `0x66378a01`). No external combo chip, no MT6686, no FEM.
   [`hardware/`](hardware/)
2. **LK picks the SKU at boot:** the static DTB says `mt6878-6631-consys`. LK reads
   `hwid-node` GPIOs 92/132/131 and patches it to `mt6878-6637-consys`, then loads the signed
   `connsys_{wifi,bt}_mt6878_mt6637` and `connsys_gnss` images from dedicated partitions into EMI
   0x87e00000. [`hardware/mt6637.md`](hardware/mt6637.md),
   [`firmware/inventory.tsv`](firmware/inventory.tsv)
3. **Exact donor:** NothingOSS `android_kernel_modules_nothing_mt6878` commit **2115d27**
   (`[SCM][MT6878][Upgrade] alps-mp-u0.mp1-V9.9`). It is not on any branch tip; it was found
   in the full history. The KDM side is `6df320423600` (Galaga V3.2 sync).
4. **Wi-Fi** = V9.9 + 13 hunks from ALPS V11.24 (selective MTK patch drop). Wi-Fi 6E 2x2,
   6 GHz enabled. [`wifi/`](wifi/)
5. **FM audio** is digital: CONNSYS I2S (master, 32 kHz) → AFE `CONNSYS_I2S` → HW_GAIN0 →
   ADDA DL → MT6369 → headset. The FM LNA enable is GPIO 72 and the antenna is the headset cable
   (GPIO 195). [`fm/route.md`](fm/route.md)
6. **BT** = BTIF to the BGF MCU, `/dev/stpbt`, no hci0, firmware preloaded by LK
   (`SUPPORT_BIN2IMG=1`). The `/vendor/firmware/soc7_0_ram_*` bins are unused fallbacks.
   [`bluetooth/`](bluetooth/)
7. **GNSS** = gps_drv_dl v051 on the MT6637 A-die, L1+L5, `/dev/gpsdl0/1`, SCP offload via
   connscp. [`gnss/`](gnss/)
8. **No Ulefone code deltas** in any connectivity module. All board identity is in DT, config
   files and the build environment (`TARGET_BUILD_VARIANT` unset).
   [`yft-connectivity-deltas.md`](yft-connectivity-deltas.md)

## Map

* [`STATUS.md`](STATUS.md): scope-by-scope status and blockers
* `hardware/`: [`topology.md`](hardware/topology.md), [`mt6637.md`](hardware/mt6637.md),
  [`rf-front-end.md`](hardware/rf-front-end.md)
* `kernel/`: [`module-inventory.tsv`](kernel/module-inventory.tsv),
  [`source-map.tsv`](kernel/source-map.tsv), [`dependency-graph.md`](kernel/dependency-graph.md)
* `conninfra/`, `fm/`, `wifi/`, `bluetooth/`, `gnss/`, `connfem/`: each has a README +
  `parity/summary.tsv`, and firmware/NVRAM boundaries where relevant
* [`firmware/inventory.tsv`](firmware/inventory.tsv): hashes and sizes only, no blobs copied
* `userspace/`: [`service-map.md`](userspace/service-map.md),
  [`dependency-map.tsv`](userspace/dependency-map.tsv)
* [`reconstruction/`](reconstruction/): `PROVENANCE.md` (git tree ids) + wlan backport patch
* [`residual-differences.md`](residual-differences.md),
  [`runtime-test-plan.md`](runtime-test-plan.md)
* `scripts/`: `connenv.sh`, `build_ext.sh`, `build_kdm.sh`, `parity_conn.sh`,
  `rebuild_all.sh`, `try_conn.sh`, `try_kdm.sh`, `hunks.py`, `intree_relink.sh`,
  `mkimg_list.py`, `gen_inventory.py`, `gen_firmware_inventory.py`, `gen_userspace_deps.py`
