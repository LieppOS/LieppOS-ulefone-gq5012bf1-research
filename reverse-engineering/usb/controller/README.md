# USB controller: MTU3 + xHCI (exact)

| module | functions | data | import CRCs | exports | relocs | sections | source |
|---|---|---|---|---|---|---|---|
| `mtu3.ko` | 209/209 | 176/176 | 165/165 | 15/15 | 2903/2903 | 62/62 bar build-id | ALPS `5e415e059253` `drivers/usb/mtu3/` (DUAL_ROLE, TRACING, DEBUG_FS), **unmodified** |
| `xhci-mtk-hcd-v2.ko` | 357/357 | 440/440 | 202/202 | (see abi tsv) | 6462/6462 | 68/68 bar build-id | ALPS `drivers/misc/mediatek/usb/usb_xhci/` (the KDM copy of xHCI core plus `xhci-mtk`), **unmodified** |
| `usb_boost.ko` | 50/50 | 54/54 | 48/48 | | 1024/1024 | exact | ALPS `usb_boost/`, unmodified |
| `usb_logger.ko` | 35/35 | 46/46 | 45/45 | | 491/491 | exact | ALPS `usb_logger/`, unmodified |

Parity tables are in [`parity/<module>/`](parity/), with `function-parity.tsv`, `data-parity.tsv`, `abi-parity.tsv`, `relocation-parity.tsv`, `SUMMARY.txt` and `sections.txt` for each module. B1==B2 is file-identical for all four.

## Behaviour (from the exact source)

- **Probe** (`mtu3_plat.c`): clocks `sys_ck`/`host_ck`/`frmcnt_ck` (the absent `ref_ck`/`mcu_ck`/`dma_ck` are optional), `vusb33`, power domain SSUSB. `ssusb_u3_drd_check()` reads IPPC `IP_DEV_CAP`/`IP_XHCI_CAP` and gets **`usb3-drd: 0`** on stock. `mtu3_hw_init` reads `IP_TRUNK_VERS` = 0x1008 and gets **"U2 IP"**. `max_speed` is clamped to high-speed.
- **Role switch** (`mtu3_dr.c`): DT `usb-role-switch` makes MTU3 register `usb_role_switch` `11201000.usb0-role-switch` (`ssusb_role_sw_set` → `ssusb_set_mode`). `mediatek,clk-mgr` selects `ssusb_mode_sw_work_v2`:
  - **leaving host**: `is_host = false`, `ssusb_set_vbus(0)` (no MTU3 vbus supply, so a no-op), a 100 ms wait for host-device removal (USB audio), depopulate xHCI (`ssusb_host_register(false)`), power off, `switch_port_to_off`;
  - **leaving device**: `mtu3_stop`, gadget disconnect, power off, `pm_relax`;
  - **entering host**: PHY `PHY_MODE_USB_HOST` (applies the host eye/termination props), `ssusb_host_enable`, IPPC force IDDIG=host, populate the xHCI child, `noise-still-tr`;
  - **entering device**: `pm_stay_awake`, PHY `PHY_MODE_USB_DEVICE`, device enable, force IDDIG=device, `mtu3_start`;
  - `USB_ROLE_NONE` is a real "off" state with v2.
- **sysfs** on `11201000.usb0`: `mode` (written by the USB HAL), `role_mode`, `max_speed`, `saving`, `u3_lpm`. The debugfs `mode` file is also present.
- **xHCI** (`xhci-mtk.c`): created only while host. `allow_single_roothub = 1`, so with zero USB3 Supported-Protocol ports only the USB2 HCD is registered (`USB3 root hub has no ports`, 1 USB2 port). The scheduler is `xhci-mtk-sch.c` (MTK bandwidth). ADSP offload uses `usb_offload.ko` through `mediatek,usb-offload`.
- **PM**: wakeup through `mediatek,syscon-wakeup` (pericfg_ao 0x214, version 105 → `uwk - reg:0x214, version:105`). `mediatek,hwrscs-vers = 1` gives HW resource requests (`ssusb_hwrscs_req state = 1`).
- **usb_boost**: DVFS boost on USB activity. The `mt6878-usb-boost` branch sets vcore 725 mV and small-core 1.25 GHz, and is used for USB audio.
- **usb_logger**: tracepoint fan-out for MTU3/xHCI.

## Runtime class

- `mtu3`: **ACTIVE** (UDC `11201000.usb0`, always bound).
- `xhci-mtk-hcd-v2`: **ACTIVE only in host role** (unbound in gadget mode).
- `usb_boost`, `usb_logger`: **ACTIVE**.
