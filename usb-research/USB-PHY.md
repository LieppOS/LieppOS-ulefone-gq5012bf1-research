# USB PHY reconstruction

## Production PHY

Classification: **PROVEN USB2 PHY**.

```text
/soc/usb-phy0@11f40000
  compatible = "mediatek,xsphy", "mediatek,mt6878-xsphy"
  reg = <0x11f40000 0x400>
  reg-names = "u2_port_base"
  |
  +-- usb2-phy0@11f40000
      #phy-cells = <1>
```

| Item | Value |
|---|---|
| platform driver | `mtk-xsphy` |
| stock module | `phy-mtk-xsphy.ko` |
| controller reference | `phys = <USB2-PHY 3>` |
| reference clock | `ref` |
| nvmem calibration | `intr_cal`, `term_cal` |
| masks | `0x3f`, `0xf00` |
| board tuning | `efuse-intr=0x23`, `eye-vrt=2`, `eye-vrt-host=2`, `discth=9` |
| special modes | USB2 JTAG and USB2 UART properties present |

The MT6375 charger references this exact PHY as `phy-names = "usb2-phy"` for BC1.2/USB charging integration.

Evidence: `USB-DEVICE-TREE.md`, `evidence/stock-usb-dt-nodes.txt`, `evidence/live-usb-dt-nodes.txt`.

## USB3 PHY search

The effective production tree has:

- no `usb3-phy` child;
- no `u3phy` reference in MTU3 `phys`;
- no production U3 register range;
- no U3 efuse/calibration properties;
- no U3 root hub at runtime.

A root-level development node exists:

```text
/usb-phy
  compatible = "mediatek,fpga-u3phy"
  status = "disabled"
```

It points to an FPGA I2C base, is disconnected from MTU3 and is identically disabled in the NothingOSS MT6878 source. Classification: **DISPROVEN as an operational phone PHY**.

## Donor control

The independent NothingOSS MT6878 source has the same sole USB2 PHY at `11f40000` and no production U3 child. In the same source family, MT6897 explicitly defines `usb3-phy0`, provides a U3 register range and adds `PHY_TYPE_USB3` to MTU3's `phys` list. This demonstrates what an enabled MediaTek U3 description would look like; MT6878 lacks it.

See `MT6878-DONOR-COMPARISON.md`.

## Speed consequences

The PHY evidence is consistent across all layers:

- DT: USB2-only reference and `maximum-speed = "high-speed"`;
- UDC sysfs: `maximum_speed=high-speed`;
- external host: phone at 480 Mbit/s;
- internal host: only a 480-Mbit/s root hub and 480-Mbit/s camera.

This proves stock's active PHY is USB2. It does not, by itself, prove an undocumented U3 macro is absent from the silicon/package.

## Custom-kernel warning

The USB2 calibration and board-specific eye settings are functional requirements. Replacing the XS-PHY driver or donor DT tuning blindly can break:

- ADB/MTP stability;
- Type-C role transitions;
- OTG peripherals;
- internal thermal-camera enumeration/streaming;
- BC1.2 charger detection.

A `maximum-speed` edit cannot manufacture a missing U3 PHY node, registers, calibration or PCB lanes.
