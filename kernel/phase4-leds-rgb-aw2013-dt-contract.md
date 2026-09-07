# Phase 4 — `leds_rgb_aw2013` device-tree contract (GQ5012BF1)

Source of truth: the stock merged device tree
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`) plus the
live read-only `/sys/firmware/devicetree/base` capture in
`workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`.
Both agree exactly.

## 1. Exact stock node

```dts
soc {
	i2c@11d71000 {                          /* MediaTek mt6989-compatible I2C, bus 11 */
		compatible = "mediatek,mt6989-i2c";
		reg = <0x00 0x11d71000 0x00 0x1000 0x00 0x11300a00 0x00 0x80>;
		interrupts = <0x00 0x19b 0x04 0x00>;
		clocks = <0x39 0x01 0x3f 0x11>;
		clock-names = "main", "dma";
		clock-div = <0x01>;
		scl-gpio-id = <0x93>;               /* GPIO 147 */
		sda-gpio-id = <0x94>;               /* GPIO 148 */

		aw2013@0x45 {
			compatible     = "awinic,rgb,aw2013";
			reg            = <0x45>;                 /* I2C 7-bit addr 0x45 */
			aw2013-pwd-gpio = <0x89 0xbc 0x00>;      /* <&pinctrl 188 GPIO_ACTIVE_HIGH> */
			status         = "okay";

			aw@0 {
				label                = "red";
				reg                  = <0x00>;
				led-max-microamp     = <0x1388>;   /* 5000 uA */
				led-fixed-brightness = <0x40>;     /* 64 */
				default-state        = "off";
			};

			aw@1 {
				label                = "green";
				reg                  = <0x01>;
				led-max-microamp     = <0x1388>;   /* 5000 uA */
				led-fixed-brightness = <0x40>;     /* 64 */
				default-state        = "off";
			};

			aw@2 {
				label                = "blue";
				reg                  = <0x02>;
				led-max-microamp     = <0x1388>;   /* 5000 uA */
				led-fixed-brightness = <0x80>;     /* 128 */
				default-state        = "off";
			};
		};
	};
};
```

Live confirmation (`devicetree.tar`):

```
sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/aw2013-pwd-gpio
sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/aw@1/label
sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/aw@1/led-fixed-brightness
sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/aw@1/led-max-microamp
sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/aw@1/reg
sys/firmware/devicetree/base/soc/i2c@11d71000/aw2013@0x45/aw@1/default-state
```

Live binding (`buses.txt`):

```
===/sys/bus/i2c/devices/11-0045===
/sys/bus/i2c/drivers/leds-rgb-aw2013
/sys/module/leds_rgb_aw2013
of:Naw2013T(null)Cawinic,rgb,aw2013
```

## 2. Property-by-property contract, proven against the binary

| property | where | consumed by | binary evidence |
| --- | --- | --- | --- |
| `compatible = "awinic,rgb,aw2013"` | parent | `aw2013_match_table[0].compatible` | `.rodata+0x40` holds the literal string; `.modinfo` aliases `of:N*T*Cawinic,rgb,aw2013{,C*}` |
| `reg = <0x45>` | parent | I2C core | live `11-0045` |
| `aw2013-pwd-gpio` | parent | `yft_aw2013_parse_dts()` (inlined in probe) | `.text+0x5a8` loads `.rodata.str1.1+0x1ed` = `"aw2013-pwd-gpio"` into x1 of `of_get_named_gpio_flags(np, name, 0, NULL)`; the same string is reused as the `gpio_request()` label at `.text+0x634` |
| `status` | parent | OF core | — |
| child node presence | `for_each_available_child_of_node` | `aw2013_probe_dt` | `of_get_next_available_child` loop at `.text+0x770`/`0x788`; count must satisfy `1 <= count <= 3` else `-EINVAL` (`.text+0x794 mov w27,#-0x16`) |
| `reg` (child) | child | `led->num` | `of_property_read_u32(child,"reg",…)` at `.text+0x80c` (`.rodata.str1.1+0x16e`); rejected if `>= 3` (`.text+0x818 cmp w8,#3`) |
| `led-max-microamp` | child | `led->imax` | `.text+0x854` (`str+0x191`); `imax = min_t(u32, uA/5000, 3)` — magic multiply `0xd1b71759`, `lsr #44`, `csel …, #3, lo` at `.text+0x860..0x87c` |
| `led-fixed-brightness` | child | `led->fixed_brightness` | `.text+0x89c` (`str+0x482`); `csel w8, w8, #0xff, ge` at `.text+0x8b0` → default `0xff` when absent |
| `label` | child | LED class name | consumed by `led_classdev_register_ext()` via `init_data.fwnode` (`.text+0x82c add x10, child, #0x18` = `of_fwnode_handle()`, stored to `init_data.fwnode` at `.text+0x850`) |
| `default-state` | child | LED core | handled by `led_classdev_register_ext()`, not by the driver |

## 3. Derived hardware numbers

| parameter | DT value | driver effect |
| --- | --- | --- |
| I2C bus | `i2c@11d71000` → linux bus **11** | SCL GPIO 147, SDA GPIO 148 |
| I2C address | **0x45** | AW2013 default 7-bit slave address |
| chip-enable (PWD) GPIO | **188** (`<&pinctrl 188 0>`), controller `mediatek,mt6878-pinctrl`, `gpio-ranges = <0 0 196>` | driven **output high** in probe, before any I2C traffic |
| channels | **3** (`aw@0..2`) | `AW2013_MAX_LEDS = 3` |
| channel→colour | 0=red, 1=green, 2=blue | LED class names `red`, `green`, `blue` |
| per-channel max current | 5000 µA → `imax = 1` | `LCFG[n][1:0] = 1` → **5 mA** full-scale on every channel |
| fixed brightness | red 64, green 64, blue 128 | value actually written to `PWM[n]` whenever the LED is switched on |

## 4. What the reconstruction must not change

`compatible`, the driver name `leds-rgb-aw2013`, the property names
`aw2013-pwd-gpio`, `led-max-microamp`, `led-fixed-brightness`, `reg`, and the
child `label` values are all ABI:

* `compatible` is matched by `modules.alias` lines 1289–1290 and by the stock DT
  that ships in `vendor_boot`;
* the child `label`s become `/sys/class/leds/{red,green,blue}`, which are
  hard-coded in the Lights HAL and in `init.mt6878.rc` / `init.yft.rc` /
  `ueventd.rc` (see `phase4-leds-rgb-aw2013-userspace-contract.md`).

The reconstruction reproduces all of them byte-for-byte (`.rodata`,
`.rodata.str1.1` and `.data` are byte-identical to stock).
