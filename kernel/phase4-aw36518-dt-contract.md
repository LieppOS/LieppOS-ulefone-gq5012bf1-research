# GQ5012BF1 — AW36518 device-tree contract (Phase 3)

Source: offline decompile of the stock boot chain
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`, produced
from the stock `vendor_boot` FDT + DTBO overlay).  The flash nodes come from the
**base DTB**; the DTBO adds no AW365xx node and no property override, and the
`vendor_boot` payload FDT carries the same nodes.  No DT was modified in this
phase.

## AW36518 (this module)

```dts
i2c@11e03000 {                       /* mediatek,mt6989-i2c, runtime adapter 8 */
	aw36518@63 {
		compatible = "mediatek,aw36518";
		reg = <0x63>;
		status = "okay";
		#cooling-cells = <0x02>;
		phandle = <0x32d>;

		flash@0 {
			type = <0x00>;
			ct   = <0x00>;
			part = <0x01>;
			reg  = <0x02>;
		};
	};
};
```

Properties the stock driver actually consumes:

| Property | Consumer | Effect |
|---|---|---|
| `compatible = "mediatek,aw36518"` | `aw36518_of_table` | binding |
| `reg = <0x63>` | I²C core | address |
| `#cooling-cells = <2>` | `thermal_of_cooling_device_register()` | registers `flashlight_cooler` |
| child node iteration (`of_get_next_child`) | `aw36518_parse_dt` | one flashlight device per child |
| child `type`, `ct`, `part` (u32) | `aw36518_parse_dt` | `struct flashlight_device_id` → `flashlight_dev_register_by_device_id()` |
| child `reg` | inlined `aw36518_subdev_init` | binds `sd->fwnode` only when `reg == led_no`; here `reg = 2 != 0`, so no fwnode is bound |
| `flash-externel` (named GPIO) | inlined `aw36518_gpio_init` | optional external strobe/enable GPIO; **absent on this board** |

Resulting flashlight device identity registered by stock:
`type = 0, ct = 0, part = 1, name = "aw36518-led0", channel = 0, decouple = 0`.
`channel` is the loop index and `decouple` is hard-coded 0 (`u32 decouple = 0;`
never read from DT).

`aw36518_parse_dt` stops after the first successfully registered child: the
second iteration hits a UBSAN bound trap (`brk #0x5512`) because
`flash_dev_id[]` has one element (`aw36518_LED_MAX == 1`).  With the stock DT
(one child) this is unreachable.

## Sibling nodes on the same tree

```dts
i2c@11d72000 {                       /* runtime adapter 12 */
	aw36518_i2c13@63 {
		compatible = "mediatek,aw36518_v2";
		reg = <0x63>;
		#cooling-cells = <0x02>;
		flash@1 { type = <0>; ct = <1>; part = <1>; reg = <3>; };
	};
};

i2c@… {
	aw36515@63 {
		compatible = "mediatek,aw36515";
		reg = <0x63>;
		#cooling-cells = <0x02>;
		flash-externel = <0x89 0x74 0x00>;      /* only AW36515 has the GPIO */
		flash@0 { type = <0>; ct = <0>; part = <0>; reg = <0>; port@0 { endpoint { … }; }; };
		flash@1 { type = <0>; ct = <1>; part = <0>; reg = <1>; port@1 { endpoint { … }; }; };
	};
};
```

So the board exposes three distinct flash device IDs:

| Node | type | ct | part | name | media-graph endpoints |
|---|---|---|---|---|---|
| `aw36515@63` flash@0 | 0 | 0 | 0 | `aw36515-led0` | yes (`mtk-composite-v4l2-1` port@0) |
| `aw36515@63` flash@1 | 0 | 1 | 0 | `aw36515-led1` | yes (port@1) |
| `aw36518@63` flash@0 | 0 | 0 | 1 | `aw36518-led0` | no |
| `aw36518_i2c13@63` flash@1 | 0 | 1 | 1 | `aw36518_v2-led0` | no |

i.e. `part = 0` is the AW36515 pair (main/second colour temperature) and
`part = 1` is the AW36518 pair — the alternate BOM / second flash assembly.

The MediaTek flashlight core node itself is board-generic:

```dts
flashlight-core {
	compatible = "mediatek,flashlight_core";
	low-battery-level = <0x02>;
	battery-percent-level = <0x01>;
	battery-oc-level = <0x02>;
};
```
