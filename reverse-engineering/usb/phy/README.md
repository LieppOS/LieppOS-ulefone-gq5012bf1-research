# USB PHY: MediaTek XS-PHY, USB2 port only (exact)

| module | functions | data | import CRCs | relocs | sections | source |
|---|---|---|---|---|---|---|
| `phy-mtk-xsphy.ko` | 63/63 | 35/35 | 60/60 | 1250/1250 | 43/43 bar build-id; B1==B2 | ALPS `5e415e059253` `drivers/phy/mediatek/phy-mtk-xsphy.c`, **unmodified** |

Parity tables are in [`parity/phy-mtk-xsphy/`](parity/phy-mtk-xsphy/).

## Instance map

| PHY | present | evidence |
|---|---|---|
| USB2 port 0 (`usb2-phy0@11f40000`, `u2_port_base` 0x11f40000/0x400) | **yes**. Used by MTU3 (`PHY_TYPE_USB2 = 3`) and by MT6375 BC1.2 (`phy-names = "usb2-phy"`) | DT, `/proc/iomem`, `mtk-xsphy` bound |
| USB3 port | **no**. There is no child, no `u3_port_base`, and no U3 efuse (`efuse-tx-imp`/`rx-imp`). The `u3_phy_*`, `proc_sib_*` and `tx-lctx*` code is dormant | DT |
| shared/combo PHY | no | DT |
| `/usb-phy` `mediatek,fpga-u3phy` | **disabled** FPGA I2C test PHY (`fpga_i2c_physical_base 0x11c22000`), not referenced | DT |
| ippc resource in PHY | absent (`failed to get ippc resource(id-0)` at boot), so the SIB/loopback procfs is disabled | stock kmsg |

## Lifecycle (exact source)

| op | behaviour |
|---|---|
| `init` | `u2_phy_instance_init`: reads efuse INTR_CAL (mask 0x3f) and TERM_CAL (mask 0xf00) through nvmem `u2_phy_data`. If the efuse is 0, it falls back to DT `efuse-intr = 0x23` and the register default for term |
| `power_on` | `u2_phy_instance_power_on`, slew-rate calibration (`u2_phy_slew_rate_calibrate`, ref clk26m), LPM PLL. `tx-chirpk-capable`: chirp-K is disabled in normal state ("Disable tx_chirpK.") |
| `set_mode(DEVICE)` | `u2_phy_props_set` (device eye/termination/discth/sqth), then `U2PHYDTM1` FORCE_IDDIG + RG_IDDIG |
| `set_mode(HOST)` | `u2_phy_host_props_set` (host_* variants), FORCE_IDDIG with RG_IDDIG=0 |
| `set_mode(OTG)` | release IDDIG force |
| submodes | `BC11_SW_SET/CLR` (BC1.2 switch for MT6375 charger detection), `DPDMPULLDOWN_SET/CLR`, `DPPULLUP_SET/CLR` |
| `power_off`/`exit` | U2 power off |
| suspend/resume | `mtk_xsphy_suspend/resume` (system PM). Special `usb2uart` mode (UART over D+/D−) and `usb2jtag` (`infra_ao_reg_clk` 1) |

Register-level tuning: [`tuning.md`](tuning.md).

## Classification audit (workspace `PARTIAL/USB-PHY`)

The workspace component contained two files that are **not USB PHY material**:

- `source/panel-ky-vtdr6115-dphy-cmd.c`: a **DSI D-PHY display panel driver** (VTDR6115). It was matched only by the substring "dphy". It is an older reconstruction iteration (sha256 `75e531fb…`). The canonical, exact version lives in `DONE/VTDR6115-DISPLAY` (sha256 `c54c8b85…`). The original stays in the research repo at `kernel/phase4-panel-vtdr6115-recon/`.
- `scripts/47-resume-approved-b-physical-provisioning.sh`: a slot-B partition **provisioning/flash** script, matched only by the substring "phy" in "physical". It has nothing to do with the USB PHY.

Both were removed from the USB-PHY component during the 2026-10-05 move to DONE. The script was relocated to `PARTIAL/PARTITION-OWNERSHIP/scripts/` because its original path is offline. No USB-PHY claim ever depended on either file.
