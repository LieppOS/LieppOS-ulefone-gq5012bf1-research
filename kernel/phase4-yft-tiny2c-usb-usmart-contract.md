# yft_tiny2c_usb relation to uSmart

## Classification

**`SHARED_USB_PATH`**, with an explicit scope limit: the module itself is not a uSmart
controller and does not share a direct power-control edge with uSmart.

| candidate relationship | result | evidence |
|---|---|---|
| `DIRECT_CONTROLLER` | no | no uSmart/UVC switch/detect GPIO, no extcon/role/VBUS call, no uSmart userspace ABI |
| `SHARED_POWER_PATH` | no direct edge | yft GPIO 192/191/149 are thermal low-voltage enables; uSmart VBUS is the separate MT6375 OTG/extcon path |
| `SHARED_USB_PATH` | **yes, board-level** | thermal applications pair this module with `yft_extcon/tiny2c_mode`; uSmart accessories use the same secondary USB/extcon infrastructure through different UVC GPIO/USB1 controls |
| `UNRELATED` | false only at board USB-fabric level | control and endpoint functions are distinct, but the common secondary USB route is proven |
| `UNKNOWN` | no for software topology | direct versus shared responsibilities are separated by imports, DT nodes and userspace paths |

The direct uSmart chain remains:

```text
MT6375 OTG/VBUS -> extcon-mtk-usb -> USB1/UVC switch/detect GPIO path -> uSmart accessory
```

The built-in thermal chain is:

```text
yft_tiny2c_usb GPIO rails + yft_usb_flag -> paired extcon tiny2c mode -> internal USB thermal camera
```

No evidence makes SC851x part of either chain. The withdrawn SC851x/uSmart hypothesis remains
withdrawn: `sc851x_charger.ko` has no regulator/extcon/USB/MT6375 edge and no relevant DT
phandle.
