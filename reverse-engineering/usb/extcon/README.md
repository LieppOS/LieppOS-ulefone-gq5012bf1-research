# extcon-mtk-usb: exact GQ5012BF1 reconstruction

| | stock (A) | rebuild (B) |
|---|---|---|
| file | `vendor_ramdisk lib/modules/extcon-mtk-usb.ko`, sha256 `9e6adf23…cb2bf`, 46 864 B | `par/extcon-mtk-usb-B2.ko` |
| functions | 22 | **22/22 byte-identical**, KCFI 22/22, relocs per function 22/22 |
| data objects | 28 | **28/28** (incl. `.data` order: `class_attr_tiny2c_mode`, `dev_attr_vbus_limit_cur`, `dev_attr_uvc_insert_status`) |
| imports / CRC | 64 | 64/64 name+CRC, `__versions` order equal |
| modinfo | 7 (no `srcversion`, no `MODULE_VERSION`) | 7/7 |
| sections | 39 | 39/39 equal except `.note.gnu.build-id`; B1==B2 |
| depends | `tcpc_class,mt6375-charger` | same |

Source: MTK ALPS `5e415e059253` `drivers/misc/mediatek/extcon/extcon-mtk-usb.c`, plus patch [`../reconstruction/kdm-patches/0002-…`](../reconstruction/kdm-patches/). It builds against the TCPC 2.0.31 `inc/` headers from patch 0001; the notifier enums are unchanged up to `DR_SWAP`. Parity is in [`parity/extcon-mtk-usb/`](parity/extcon-mtk-usb/).

This **supersedes** the previous workspace reconstruction (`PARTIAL/EXTCON-MTK-USB/source/extcon_mtk_usb.c`, Nothing donor `957dac1`). That one was ABI-exact but only 12/22 functions byte-identical (24 functions in total) and carried a hand-written struct layout. The new source keeps the ALPS `extcon-mtk-usb.h` layout unchanged (`sizeof = 0x1b0`, `vbus_cur_inlimit` at 0x1ac) and adds only globals.

## GQ5012BF1 (YFT) delta over ALPS, as proven by the exact rebuild

| addition | exact form |
|---|---|
| globals | `extern int yft_usb_flag` (exported by `mt6375-charger.ko`); `static int yft_otg_select_gpio_num, yft_uvc_switch_gpio_num, yft_uvc_vbus_gpio_num, yft_tiny2c_status`; `static bool uvc_insert_status`; `static struct mtk_extcon_info *yft_extcon`; probe-local `static struct class *yft_extcon_class` |
| `yft_parse_dts(node, name)` | `of_get_named_gpio` → `gpio_to_desc` check → `gpio_is_valid` log → `gpio_request(gpio, name)` → `gpio_direction_output(gpio, 0)` → `gpio_set_value(gpio, 0)`. Returns the GPIO, or -1 (8 `printk` traces, no log level) |
| `get_otg_select_gpio()` (global, not exported) | finds `mediatek,extcon-usb`, then `yft_otg_select_gpio_num = yft_parse_dts(np, "otg_gpio_select")` |
| `mtk_usb_extcon_set_vbus()` (inlined) | **on**: `gpio_set_value(otg_select, 1)` + "set_high", then the original regulator voltage/current/enable. **off**: `gpio_set_value(otg_select, 0)` + "set_low", then `regulator_disable` |
| `mtk_usb_extcon_detect_cable()` (GPIO 28 IRQ work) | the ALPS VBUS on/off is **removed**. id=0 (accessory present): `uvc_vbus` GPIO 152 = 1, `uvc_switch` GPIO 55 = 1 (if > 0), `uvc_insert_status = 1`, then role **HOST**. id=1: both GPIOs 0, status 0, role **NONE**. Each branch returns early if `yft_usb_flag == 1` |
| boot-time ID check (inlined `id_pin_init`) | same GPIO/status sequence and role HOST, **without** the `yft_usb_flag` gate |
| `mtk_usb_extcon_psy_detector()` | returns early if `yft_usb_flag == 1` |
| `mtk_extcon_tcpc_notifier()` | each `set_role` site (SRC-in→HOST, SINK-in→DEVICE, plug-out→NONE, DR_SWAP→DEVICE/HOST) returns early if `yft_usb_flag == 1`. The VBUS path is the YFT `set_vbus` above |
| probe additions | after `extcon_wq`: parse `uvc_vbus_gpio`, then `uvc_switch_gpio` + `device_create_file(dev_attr_uvc_insert_status)` (through a helper; that ordering is proven by `.data` layout). Then `yft_extcon = extcon`, `printk("yft_tiny2c_mode=%d")`, `class_create("yft_extcon")` + loop over the `tiny2c_mode` class attribute array. At the end: `get_otg_select_gpio()` if not yet parsed, and `dev_err(dev, "end\n")` |
| sysfs | `/sys/devices/platform/extcon-usb/uvc_insert_status` (0444), `/sys/class/yft_extcon/tiny2c_mode` (0664). Writing `1` queues role **HOST**, anything else role **NONE**. Reads always return 0, because `yft_tiny2c_status` is never written: an upstream bug that has been preserved |

The "bypss" spelling, the "cannnot"-style typos, the `'mediatek,usb3'` error text and the "failed. … =%d" messages that print `yft_otg_select_gpio_num` for the UVC GPIOs are all stock bugs, reproduced byte-for-byte.

## Role/VBUS contract

```text
TCPC (type_c_port0) notifier, TCP_NOTIFY_TYPE_USB|VBUS|MISC (mask 0xe)
  SOURCE_VBUS(8)  mv!=0 → set_vbus(on): GPIO37=1, MT6375 usb-otg-vbus 5.25 V / 1.8 A, enable
                  mv==0 → set_vbus(off): GPIO37=0, regulator_disable, vbus_cur_inlimit=0
  TYPEC_STATE(13) UNATTACHED→ATTACHED_SRC                       → role HOST
                  UNATTACHED→SNK|NORP_SRC|CUSTOM_SRC|DBGACC_SNK  → role DEVICE (skipped if bypss-typec-sink;
                                                                    DT sets mediatek,bypss-typec-sink = 1)
                  SRC|SNK|NORP|CUSTOM|DBGACC → UNATTACHED        → role NONE
  DR_SWAP(17)     UFP & c_role≠DEVICE → NONE then DEVICE;  DFP & c_role≠HOST → NONE then HOST
power_supply notifier (primary_chg / charger phandle, PROP_CHANGED)
  psy_detector: with tcpc_dev, set DEVICE if online(SDP/CDP) and c_role==NONE
GPIO 28 (id) both edges → detect_cable (internal UVC accessory) → HOST/NONE + UVC GPIOs
/sys/class/yft_extcon/tiny2c_mode → HOST/NONE
all paths → extcon_wq → update_role: extcon USB/USB-HOST state + usb_role_switch_set_role(mtu3)
```

`mediatek,bypss-typec-sink = <1>` is the reason **device mode is not entered on Type-C SINK attach** here. Device role on charger/PC attach instead comes from the power-supply path (`psy_detector` → `usb_is_online` with an SDP/CDP charger type from `mtk_chg_type_det`/MT6375 BC1.2). The donor DT sets the same flag.

## Runtime class

**ACTIVE**: probed on `/extcon-usb` (`okay` in the DTBO). The GPIO 28 IRQ appears as `extcon-usb` in `/proc/interrupts` in the existing runtime capture.
