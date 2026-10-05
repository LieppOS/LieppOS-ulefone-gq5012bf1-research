# XS-PHY USB2 tuning: DT → register map and stock values

Register offsets are relative to `u2_port_base` 0x11f40000. The U2PHY_COM block is at +0x300.

| DT property | field | register | stock value | applied in |
|---|---|---|---|---|
| nvmem `intr_cal` (mask 0x3f) / `mediatek,efuse-intr` | `P2AR_RG_INTR_CAL` (6 bit) | `XSP_USBPHYA_RESERVE` (+0x330) | **35 (0x23)** (`u2_intr:35`) | device and host props (`intr_ofs`/`host_intr_ofs` unset = -64 sentinel) |
| nvmem `term_cal` (mask 0xf00) | `P2ARA_RG_TERM_CAL` (4 bit) | `XSP_USBPHYA_RESERVEA` (+0x334) | **8** (`term_cal:8`; offsets unset = -16 sentinel) | device and host |
| `mediatek,eye-vrt` | `P2A1_RG_VRT_SEL` | `XSP_USBPHYACR1` (+0x304) | **2** | device |
| `mediatek,eye-vrt-host` | `P2A1_RG_VRT_SEL` | `XSP_USBPHYACR1` | **2** | host |
| `mediatek,discth` | `P2A6_RG_U2_DISCTH` | `XSP_USBPHYACR6` (+0x318) | **9** | device |
| `mediatek,eye-src`, `eye-term`, `rx-sqth`, `rev6`, `pll-fbksel`, `pll-posdiv` (+ `-host`) | HSTX_SRCTRL, TERM_SEL, U2_SQTH, PHY_REV6, PLL_FBKSEL, PLL_POSDIV | ACR5 / ACR1 / ACR6 / RESERVE0/1 | **unset (-22 = -EINVAL)**, so hardware defaults apply | — |
| `tx-chirpk-capable` | chirp-K TX | `XSP_U2PHYDTM*` | chirp-K disabled in normal state | power_on |
| `usb2jtag = <&infra_ao_reg_clk 1>`, `usb2uart` | JTAG/UART-over-USB muxes | infra_ao / PHY | not selected at runtime (normal USB mode) | special modes |

The stock values come from the existing read-only boot log (`last_kmsg.5.txt`, lines 0.97781x):

```text
mtk-xsphy 11f40000.usb-phy0: device src:-22 vrt:2 term:-22 rev6:-22
mtk-xsphy 11f40000.usb-phy0: host src:-22 vrt:2 term:-22 rev6:-22
mtk-xsphy 11f40000.usb-phy0: u2_intr:35 intr_ofs:-64 host_intr_ofs:-64 discth:9
mtk-xsphy 11f40000.usb-phy0: term_cal:8 term_ofs:-16 host_term_ofs:-16
mtk-xsphy 11f40000.usb-phy0: rx_sqth:-22 host_rx_sqth:-22
mtk-xsphy 11f40000.usb-phy0: pll_fbksel:-22, pll_posdiv: -22
```

The DT tuning values are identical to the MTK ALPS `mt6878.dts` reference. GQ5012BF1 adds **no** board-specific PHY tuning.

The runtime override knobs (`/proc/mtk_usb/<phy-node>/u2_phy/{term_sel,vrt_sel,phy_rev6,discth,rx_sqth,intr_ofs,term_ofs}`, mode 0644) are created by `u2_phy_procfs_init` and are root-only debug controls.
