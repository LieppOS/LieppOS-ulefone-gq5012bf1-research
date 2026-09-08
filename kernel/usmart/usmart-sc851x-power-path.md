# uSmart ↔ SC851x power-path determination

## Classification

```text
USMART_SC851X_RELATION = PROVEN_UNRELATED
CAN_STOCK_USMART_CHARGE_PHONE = NO_SOFTWARE_SUPPORT_FOUND
```

Scope of `PROVEN_UNRELATED`: the stock DT/software **control and VBUS source
path**. No board schematic was available to prove every upstream copper rail,
but SC8510 is not the uSmart switch, VBUS regulator, connector detector, USB
controller, or userspace interface.

## Proven stock uSmart/accessory path

The user-facing uSmart connector supports Ulefone USB endoscope/microscope
accessories. Stock evidence maps that accessory path as follows:

```text
uSmart UVC accessory
  │
  ├─ detection/status: extcon-usb/uvc_insert_status
  ├─ physical selection: extcon-usb uvc_switch_gpio (GPIO 55)
  ├─ accessory 5-V gate: extcon-usb uvc_vbus_gpio (GPIO 152)
  ├─ source regulator: vbus-supply phandle 325
  │    └─ /soc/i2c@11280000/mt6375@34/chg/otg
  │       regulator-name = "usb-otg-vbus"
  ├─ policy/role driver: extcon-mtk-usb.ko
  │    ├─ regulator_set_voltage/current_limit
  │    ├─ regulator_enable/disable
  │    ├─ usb_role_switch_set_role
  │    ├─ extcon_set_state_sync
  │    └─ depends=tcpc_class,mt6375-charger
  └─ USB host controller: 11211000.usb1/11210000.xhci
       └─ voldmanaged=usbotg:auto
```

This chain names the regulator provider: the `vbus-supply` phandle resolves to
**MT6375 `usb-otg-vbus`**, not SC8510.

## Stock DT evidence

`/extcon-usb`, compatible `mediatek,extcon-usb`:

- `id-gpios = <&gpio 28 0>`
- `otg_gpio_select = <&gpio 37 0>`
- `uvc_switch_gpio = <&gpio 55 0>`
- `uvc_vbus_gpio = <&gpio 152 0>`
- `vbus-supply = <325>`
- `vbus-voltage = <5250000>`
- `vbus-current = <1800000>`
- `vbus-limit-current = <500000>`
- `mediatek,bypss-typec-sink = <1>`
- `tcpc = "type_c_port0"`

Phandle 325 resolves to:

`/soc/i2c@11280000/mt6375@34/chg/otg`

- `regulator-name = "usb-otg-vbus"`
- `regulator-compatible = "mt6375,otg-vbus"`

By contrast, `/soc/i2c@11e01000/sc851x-charger@6f` contains only its own
SC851x protection/timing/frequency fields and IRQ GPIO. It has no USB/UVC,
extcon, VBUS, regulator-supply, or connector phandle.

## Separate built-in tiny2c thermal-camera path

The similarly named `yft_tiny2c_usb` stack must not be conflated with SC851x or
with the external connector's 5-V regulator:

```text
/yft_tiny2c_usb (mediatek,yft_tiny2c_usb)
  ├─ tiny2c_usb_vdd_1v8  GPIO 192
  ├─ tiny2c_usb_vdd_3v3  GPIO 191
  └─ tiny2c_usb_vddio_3v3 GPIO 149

/soc/i2c@11e03000/fm78100@0x3c
  ├─ reg = <0x3c>
  └─ compatible = "mediatek,tiny2c_usb"
```

`yft_tiny2c_usb.ko` drives these low-voltage GPIO rails and probes the `0x3c`
I2C device. The thermal-camera application `M170infDlp.apk` contains the paths
`/sys/devices/platform/yft_tiny2c_usb/`, `tiny2c_usb_mode`, and `tiny2c_mode`.
This is a parallel YFT USB-camera path. It still contains no SC851x reference.

The external uSmart/UVC selection lives in `extcon-mtk-usb.ko`; the stock UI
contains `/sys/devices/platform/extcon-usb/uvc_insert_status` and package
`com.endoscope.otgcamera`.

## Why SC851x is excluded

### Binary ABI

`sc851x_charger.ko` imports only generic I2C/regmap/GPIO/IRQ/sysfs/PM helpers.
It imports none of:

- regulator APIs;
- USB role-switch APIs;
- extcon APIs;
- `tcpc_class` APIs;
- MT6375 charger or `yft_usb_flag` APIs;
- power-supply or charger-class APIs.

It exports no symbol that the accessory stack could call. `depends=` is empty.

### DT graph

There is no phandle edge between the SC8510 node and `extcon-usb`, USB1,
MT6375 OTG, `yft_tiny2c_usb`, or the `0x3c` camera bridge/sensor node.

### Userspace

A stock partition sweep excluding kernel modules found zero userspace references
to `sc851x`, `sc8510`, `sc8517`, `6-0069`, or `AUDIO_EN`. The actual accessory
paths appear in init, fstab, SystemUI, and thermal-camera app artifacts.

### Behavior

SC851x probe programs its own raw register fields and registers a fault-log IRQ.
It never enables a VBUS regulator, switches a USB role, detects UVC insertion,
or toggles the uSmart GPIOs. Its shutdown-only `AUDIO_EN` clear is not a
connector-power operation.

## Can uSmart charge the phone?

No stock software support was found for using the uSmart connector as a phone
charging **sink**:

- the mapped regulator is named `usb-otg-vbus` and is driven as a source;
- the USB1 path is enumerated/mounted as `usbotg` host media;
- UVC/endoscope accessories are powered peripherals;
- the extcon node explicitly bypasses the Type-C sink path;
- no uSmart-specific power-supply/charger sink registration or charge-policy
  control was found.

Therefore the required conclusion is `NO_SOFTWARE_SUPPORT_FOUND`, not a claim
that an unknown rewiring is electrically impossible. No power was applied to
the connector during this investigation.

## Confidence and boundary

- SC8510 absent from uSmart software/DT control graph: **high**.
- uSmart UVC VBUS source is MT6375 OTG via extcon driver: **high**.
- connector supports stock phone charging as a sink: **no software support
  found**.
- complete board-level upstream power topology: **blocked by missing schematic**.
