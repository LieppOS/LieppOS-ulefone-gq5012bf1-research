# MT6878 USB capability and donor comparison

## Sources and confidence

Primary implementation source:

- NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878`;
- remote: <https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878>;
- inspected commit: `957dac185efe46cbf6336b0fff9516d84c8cd78f`;
- source: `device_modules/arch/arm64/boot/dts/mediatek/mt6878.dts`;
- frozen excerpts and hash: `evidence/nothing-mt6878-usb-nodes.txt`.

Public product sources checked:

- MediaTek Dimensity 7300 product page: <https://www.mediatek.com/products/smartphones/mediatek-dimensity-7300>;
- MediaTek Dimensity 7400 infographic: <https://www.mediatek.com/hubfs/Dimensity%207400_Infographic.pdf>.

The public MediaTek marketing material identifies the chipset but does not publish USB controller, PHY, port-count or maximum-speed data. Secondary processor databases, notably PhoneDB, claim USB 3.0/5-Gbit/s capability and label their data preliminary. No public primary MediaTek passage confirming that claim was found. The secondary claim is retained as conflicting evidence, not promoted to fact.

## Side-by-side DT comparison

| Property | GQ5012BF1 effective stock DT | NothingOSS MT6878 donor | Same? | Meaning |
|---|---|---|---|---|
| controller path | `/soc/usb0@11201000` | `ssusb: usb0@11201000` | YES | Same MT6878 USB instance |
| compatible | `mediatek,mtu3` | `mediatek,mtu3` | YES | Same MTU3 dual-role core |
| MAC registers | `0x11201000 + 0x2e00` | same | YES | Same controller block |
| IPPC registers | `0x11203e00 + 0x100` | same | YES | Same power/port-control block |
| device IRQ | GIC SPI 384 | GIC SPI 384 | YES | Same interrupt |
| host child | `xhci0@11200000` | `xhci0@11200000` | YES | Same host block |
| host IRQ | GIC SPI 385 | GIC SPI 385 | YES | Same interrupt |
| role | `dr_mode = "otg"` | same | YES | Dual-role USB2 path |
| maximum speed | `high-speed` | `high-speed` | YES | Both explicitly capped at 480 Mbit/s |
| controller PHY list | one `<USB2>` PHY | one `<&u2port0 PHY_TYPE_USB2>` | YES | No production U3 PHY reference |
| PHY parent | `usb-phy0@11f40000` | same | YES | Same register block |
| PHY compatible | `mediatek,xsphy`, `mediatek,mt6878-xsphy` | same | YES | Same MT6878 XS-PHY driver |
| PHY child | `usb2-phy0@11f40000` only | same | YES | U2-only instantiated production PHY |
| enabled U3 child | none | none | YES | No source-described production USB3 PHY |
| FPGA U3 node | disabled `mediatek,fpga-u3phy` | identical disabled node | YES | Development placeholder, not product path |
| role-switch graph | MTU3 ↔ `extcon-usb` | MTU3 ↔ `extcon-usb` | YES | Same MediaTek architecture |
| extcon VBUS | 5.25 V, 1.8 A | 5.4 V, 1.3 A | NO | Board/OEM power-policy tuning |
| UVC route GPIOs | GPIO 55 switch, GPIO 152 VBUS, plus GPIO 28/37 | absent in donor base | NO | Ulefone thermal/accessory customization |
| USB2 PHY tuning | eye VRT `2`, host `2`, discth `9`; no explicit eye-term | eye-term `7`, eye VRT `7`, host `2`, discth `9` | PARTIAL | Board-specific USB2 signal tuning |
| MTU3 Type-C name properties | omitted | `rt-pd-manager`, `port0`, `mtk-master-charger` | NO | Ulefone delegates through its extcon/overlay arrangement |

The GQ controller/PHY topology is not an accidental minimal reconstruction: it closely matches the OEM-published Nothing/MediaTek MT6878 base source, while adding Ulefone-specific thermal switching and power policy.

The donor `mgk_64_k61_defconfig` builds the same platform pieces as modules: `CONFIG_DEVICE_MODULES_USB_MTU3=m`, `CONFIG_DEVICE_MODULES_USB_XHCI_MTK=m`, and `CONFIG_DEVICE_MODULES_PHY_MTK_XSPHY=m`. It also builds MediaTek USB boost, META, offload and logger modules. There is no MT6878-specific production U3-PHY configuration accompanying them.

## Comparison with sibling MediaTek source

The same NothingOSS source drop contains other MediaTek SoC descriptions:

- MT6878: no production U3 PHY marker; only the USB2 child at `11f40000`;
- MT6897: an explicit production `u3phy: usb-phy0@11e40000`, a `usb3-phy0@11e43000` child, and the MTU3 `phys` list includes both `PHY_TYPE_USB2` and `PHY_TYPE_USB3`;
- MT6985/MT6989: explicit production U3 PHY instances also exist.

This controls for coding style: when a sibling platform has a production U3 PHY, the MediaTek source describes it explicitly and references it from MTU3. MT6878 does not.

## Capability verdict

The evidence supports three separate statements:

1. **GQ5012BF1 stock USB3 path:** `DISPROVEN` — no enabled production U3 PHY, MTU3 is High-Speed-only, UDC maximum is High-Speed, and the xHCI host creates only a 480-Mbit/s root hub.
2. **Public MT6878 production kernel path:** `STRONGLY_SUPPORTED USB2-only` — the OEM-published MT6878 source independently has the same single U2 PHY and High-Speed cap, with no product override enabling U3.
3. **MT6878 transistor/package-level USB3 capability:** `UNKNOWN`, with accessible production USB3 **STRONGLY_DISFAVORED** — no public primary datasheet section or package ball map was obtained, while a preliminary secondary database claims 5-Gbit/s USB3.

Therefore this project must not state either “MT6878 definitely supports USB3” or “USB3 is physically impossible in silicon” as a proven fact. The strongest responsible conclusion is:

> All authoritative implementation evidence available for MT6878 exposes only one USB2 High-Speed MTU3/XS-PHY path. A secondary database claim of USB3 remains unverified and conflicts with the published kernel implementation.

## Number of ports

The MT6878 source describes:

- one MTU3 dual-role controller;
- one xHCI child;
- one USB2 PHY port;
- no production USB3 PHY port.

The controlled GQ thermal test created one USB2 xHCI root hub and placed the camera directly on port 1. No SS companion root hub appeared. This establishes one operational USB2 root-port path in this product/source configuration; it does not prove the package contains no inaccessible test or reserved interfaces.

## Implication for enabling USB3

Changing only:

```dts
maximum-speed = "super-speed";
```

would be invalid. A working SuperSpeed design would also require, at minimum:

- a real MT6878-compatible production U3 PHY node/register block;
- a USB3 PHY child and MTU3 `phys` reference;
- correct clocks, resets, power domains, efuse calibration and driver support;
- package pins and board lanes;
- orientation/mode switching and ESD path to the receptacle.

None of those prerequisites is established for GQ5012BF1 or the MT6878 public source.
