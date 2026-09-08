# uSmart/accessory software evidence ledger

This ledger separates direct stock evidence from inference and records the
negative SC851x search.

## Direct configuration evidence

### `vendor/etc/init/hw/init.yft.rc`

Stock grants write/read access to the board USB-camera controls:

```rc
# yft silence add for yf usb camera
chmod 0666 /sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode
chmod 0666 /sys/devices/platform/soc/11211000.usb1/mode
chmod 0666 /sys/class/yft_extcon/tiny2c_mode

# yft ljb add for endoscope test
chmod 0777 /sys/devices/platform/extcon-usb/uvc_insert_status
```

It also exposes `/sys/devices/platform/yft_tiny2c_usb/sensor_id` for the thermal
imaging product variant.

### `vendor/etc/fstab.mt6878` and `fstab.emmc`

Both contain:

```fstab
/devices/platform/soc/11211000.usb1/11210000.xhci* auto vfat \
    defaults voldmanaged=usbotg:auto
```

That is USB host/removable-media treatment, not a charger sink declaration.

## Kernel module evidence

### `extcon-mtk-usb.ko`

Metadata:

```text
name: extcon_mtk_usb
description: MediaTek Extcon USB Driver
depends: tcpc_class,mt6375-charger
alias: of:N*T*Cmediatek,extcon-usb
```

Relevant defined functions include:

- `show_uvc_insert_status`
- `show_tiny2c_mode` / `store_tiny2c_mode`
- `mtk_usb_extcon_set_vbus`
- `mtk_usb_extcon_set_role`
- `get_otg_select_gpio`

Relevant imports include:

- `regulator_set_voltage`, `regulator_set_current_limit`
- `regulator_enable`, `regulator_disable`, `regulator_is_enabled`
- `usb_role_switch_get`, `usb_role_switch_set_role`
- `extcon_set_state_sync`
- GPIO helpers and `yft_usb_flag`

Strings name `uvc_switch_gpio`, `uvc_vbus_gpio`, `usb-otg-vbus`,
`uvc_insert_status`, `source vbus`, and `vbus turn %s`.
Relocation-aware excerpts are preserved at
`workspace/phase4-sc851x/usmart/extcon-uvc-power-objdump.txt`.

### `yft_tiny2c_usb.ko`

Metadata:

```text
name: yft_tiny2c_usb
description: Module For tiny2c_usb
depends: mt6375-charger
aliases: mediatek,yft_tiny2c_usb; i2c:tiny2c_usb-sensor
```

It directly imports `gpio_to_desc`, `gpiod_set_raw_value`,
`gpiod_get_raw_value`, `of_get_named_gpio_flags`, and `yft_usb_flag`.
Functions include `tiny2c_usb_power_init`, `tiny2c_usb_mode_store`, and
`tiny2c_usb_read_chipid`. Strings name 1.8-V, 3.3-V, 3.3-V-I/O and optional
5-V GPIOs. Relocation-aware excerpts are preserved at
`workspace/phase4-sc851x/usmart/yft-tiny2c-mode-objdump.txt`.

### `sc851x_charger.ko`

Metadata:

```text
name: sc851x_charger
description: SC SC851X Driver
depends: (empty)
aliases: none
exports: none
```

No regulator, extcon, USB, TCPC, MT6375, `yft_usb_flag`, power-supply, or
charger-class symbol is imported. The only GPIO is its IRQ. The only sysfs node
is raw `registers`. This is an incompatible control surface for uSmart.

## DT graph evidence

| node | role-defining properties |
|---|---|
| `/extcon-usb` | `uvc_switch_gpio`, `uvc_vbus_gpio`, `vbus-supply`, USB role/TCPC, ID GPIO |
| `/soc/i2c@11280000/mt6375@34/chg/otg` | phandle 325, `regulator-name="usb-otg-vbus"` |
| `/yft_tiny2c_usb` | 1.8-V/3.3-V/3.3-V-I/O GPIO rails |
| `/soc/i2c@11e03000/fm78100@0x3c` | `compatible="mediatek,tiny2c_usb"`, `reg=<0x3c>` |
| `/soc/i2c@11e01000/sc851x-charger@6f` | `compatible="sc,sc8510"`, `reg=<0x69>`, SC851x-local configuration and IRQ only |

No SC851x phandle appears in any of the accessory nodes and no accessory
phandle appears in the SC851x node.

## APK/userspace evidence

`YftSystemUI.apk` contains:

- `/sys/devices/platform/extcon-usb/uvc_insert_status`
- `/sys/devices/platform/yft_tiny2c_usb/sensor_id`
- `com.endoscope.otgcamera`
- endoscope uninstall/prompt resource keys

`M170infDlp.apk` contains:

- `/sys/devices/platform/yft_tiny2c_usb/`
- `tiny2c_usb_mode`
- `tiny2c_mode`
- thermal-camera package/library identifiers

Stock extracted-partition search, excluding `.ko` files, found **zero**
references to:

```text
sc851x | sc8510 | sc8517 | 6-0069 | AUDIO_EN
```

## Public product context

Ulefone describes the Armor 29 Pro Thermal uSmart connector as supporting its
E01/E02/E03 endoscopes and C01 microscope. Those are USB camera peripherals,
consistent with the stock UVC/USB1 host path. This context is not used to infer
register behavior.

## Conclusions

| question | result |
|---|---|
| Does stock software use SC851x to detect uSmart insertion? | No; extcon/UVC path does |
| Does SC851x switch uSmart data routing? | No; `uvc_switch_gpio` is in extcon DT/driver |
| Does SC851x source uSmart VBUS? | No; `vbus-supply` resolves to MT6375 `usb-otg-vbus` |
| Does SC851x expose a callable connector API? | No exports, no framework object |
| Does stock support charging the phone through uSmart? | `NO_SOFTWARE_SUPPORT_FOUND` |
| Required relation classification | `PROVEN_UNRELATED` (software/control/VBUS-source scope) |

All device-derived evidence was collected earlier through read-only snapshots.
No sysfs write, GPIO toggle, role switch, reverse-power action, or accessory
power test was performed for this investigation.
