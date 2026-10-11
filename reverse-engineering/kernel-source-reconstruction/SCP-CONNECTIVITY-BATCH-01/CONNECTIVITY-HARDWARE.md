# GQ5012BF1 connectivity hardware (kernel view)

Labels as in `SCP-HOST-INTERFACES.md`. Detailed prior research is reused rather than repeated:
`reverse-engineering/connectivity/hardware/{topology,mt6637,rf-front-end}.md`, `../connfem/`, `../fm/route.md`.

## Topology

```text
MT6878 integrated CONNSYS (connv2 "SOC7_0", CONNAC2X D-die) --A-die SPI--> MT6637 A-die (RF companion)
  conninfra.ko  conn_infra MMIO 0x18000000..; EMI 12 MiB + GPS 1 MiB; PMIC VCN13/VRFIO18/VCN33_1/VCN33_2/VANT18
   ├─ wlan_drv_gen4m_6878 + wmt_chrdev_wifi_connac2   WF 0x18400000, SPI 0x1e4/0x2b4, WFDMA over AXI, cfg80211/mac80211
   ├─ bt_drv_6878 (BTIF/CCIF to BGF MCU)              BT 0x18800000, SPI 0x2b5/0x84 → bluetooth.ko HCI
   ├─ gps_drv_dl_v051 + gps_pwr                       GPS 0x18c00000
   ├─ fmradio_drv_connac2x                            `fm` SPI 0x1e6; LNA enable GPIO 72; FM digital audio → AFE "Connsys I2S"
   └─ connscp + gps_scp                               CONAP offload on SCP (tinysys IPI, SCP share memory)
connadp.ko: build-in adapter + power-throttling bridge (LOW_BATTERY notify) for all of the above
connfem.ko: front-end module selection: nofem/nofem on this board
uarthub_drv.ko: driver loaded; `uarthub { uarthub-disable = <1> }` (hub not used, no external UART combo)
wifi_cooling.ko: `wifi-cooler` thermal cooling device
mtk-btcvsd.ko: BT SCO CVSD/mSBC PCM path into ASoC
```

## Evidence table

| Element | Fact | Class |
|---|---|---|
| CONNSYS | `consys@18000000`, power-domain `<0x22 1>`, EMI 12 MiB, RO/RW splits (BT 0x2e0000, GPS 0xa0000, WiFi 0x300000) | ENABLED_IN_STOCK_DT |
| A-die SKU | static DTB says `mt6878-6631-consys`; LK rewrites it to `mt6878-6637-consys`. Strap `hwid-node <92 132 131>`, `adie-sku <1 1 0 0 2 2 1 0>`; `A-die chip id 0x66378a01` | PROVEN_RUNTIME (dmesg, live DT) |
| Transport | SoC-integrated (AXI WFDMA, BTIF/CCIF). No SDIO/PCIe/USB combo chip; uarthub disabled | ENABLED_IN_STOCK_DT + PROVEN_RUNTIME |
| Wi-Fi | `wifi@18400000`, IRQ SPI 0x1e4 + 0x2b4, EMI 20 MiB DMA pool; 2x2 11ax/6 GHz build options compiled in | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Bluetooth | `bt@18800000`, IRQ 0x2b5 + 0x84; `CHIP_ID 6878, ADIE_ID 6637` | ENABLED_IN_STOCK_DT + PROVEN_RUNTIME |
| GNSS | `gps@18c00000`; L1+L5 on MT6637; no MT6686 | ENABLED_IN_STOCK_DT + PROVEN_RUNTIME |
| FM | `fm` (`family-id 0x6983`, `conn-id 0x205`, SPI 0x1e6), `fmradio { fm_lna_gpio = <&pio 72 0> }`; antenna is the headset cable (ACCDET FM switch GPIO 195, AUDIO-BATCH-01) | ENABLED_IN_STOCK_DT |
| FEM | `connfem` with 7 pairings; runtime `FEM is not available` → nofem | PROVEN_RUNTIME |
| Clock | MT6685 52 MHz co-clock, XO buffer `BB2/RF1A` for gps/bt/wf/mcu | ENABLED_IN_STOCK_DT + PROVEN_RUNTIME |
| Thermal | consys thermal sensor; `wifi-cooler` | ENABLED_IN_STOCK_DT |
| Modem coupling | conninfra/wlan import `mtk_ccci_register_md_state_cb`, `get_smem_phy_start_addr` (ccci_md_all); wlan imports `mddp_drv_attach/detach` (MD data-path offload) | STOCK_BINARY_IMPLEMENTATION |
| Platform hooks | `register_devapc_vio_callback`, `aee_*` exception APIs, `lbat_user_register`, `register_low_battery_notify` | STOCK_BINARY_IMPLEMENTATION |
| Module loading | `uarthub_drv` first stage (order 97); `cfg80211`/`mac80211` 248/249; `connadp` 335; `connscp` 377, `connfem` 378, `conninfra` 379, `wmt_chrdev` 380, `wlan` 381, `fm` 387, `gps_drv_dl` 388, `bt_drv` 415 (vendor_dlkm); `gps_pwr`/`gps_scp` via `init` insmod (441/442) | PROVEN_RUNTIME |

## Not established

- Physical antenna count, placement and feeds (teardown).
- GPIO 92/131/132 strap levels (inferred, not read).
- The FM LNA part.
- Runtime radio performance.

The Wi-Fi capture had Wi-Fi off. A certified driver does not mean the radio works.
