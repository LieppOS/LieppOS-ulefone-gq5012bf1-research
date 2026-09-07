# AW36515 device-tree and media-graph contract (GQ5012BF1)

Source: the stock merged device tree
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`, produced
from the stock boot DTB + DTBO overlay) and the read-only live sysfs snapshot
`workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt`.

## Node

```
/soc/i2c@11e01000 {                 /* alias i2c6, mediatek,mt6989-i2c */
	aw36515@63 {
		compatible    = "mediatek,aw36515";
		reg           = <0x63>;
		status        = "okay";
		flash-externel = <0x89 0x74 0x00>;   /* pio, pin 116, flags 0 */
		#cooling-cells = <0x02>;
		phandle       = <0x32c>;

		flash@1 {
			type = <0x00>;
			ct   = <0x01>;
			part = <0x00>;
			reg  = <0x01>;
			port@1 { endpoint { remote-endpoint = <0x319>; }; };
		};

		flash@0 {
			type = <0x00>;
			ct   = <0x00>;
			part = <0x00>;
			reg  = <0x00>;
			port@0 { endpoint { remote-endpoint = <0x318>; }; };
		};
	};
};
```

Live confirmation:

```
===/sys/bus/i2c/devices/6-0063===
/sys/bus/i2c/drivers/aw36515
/sys/module/aw36515
aw36515
of:Naw36515T(null)Cmediatek,aw36515
```

## How the driver consumes the node

| DT item | consumed by | effect |
|---|---|---|
| `compatible` | `aw36515_of_table` | driver match |
| `reg = <0x63>` | I²C core | client address |
| `flash-externel` | `of_get_named_gpio(np, "flash-externel", 0)` in probe | external strobe GPIO (pin 116) |
| `#cooling-cells` | `thermal_of_cooling_device_register(dev->of_node, "flashlight_cooler", …)` | registers the cooling device |
| child `type`/`ct`/`part` | probe's inlined DT parser | fills `flash_dev_id[i]` |
| child `reg` | `aw36515_subdev_init` | binds `subdev_led[led_no].fwnode` when `reg == led_no` |
| child `port@N/endpoint` | V4L2 async / media graph | links the flash sub-device to `mtk-composite-v4l2-1` |

## Two different indexing rules — and they cross

This is the single most surprising, and fully proved, property of the stock
driver on this board.

* **`aw36515_subdev_init(flash, led_no, name)`** walks the `flash` children and
  binds the one whose **`reg` equals `led_no`**.  Therefore
  `subdev_led[0].fwnode` ← `flash@0` (`ct = 0`) and
  `subdev_led[1].fwnode` ← `flash@1` (`ct = 1`).
* **The MediaTek flashlight registration loop in probe** iterates children in
  **device-tree order** with a running index `i`, and names each entry from
  `subdev_led[i].name`.  In this DTB the children are emitted `flash@1` first,
  then `flash@0`.

Consequently the MediaTek flashlight device ids are:

| loop index `i` | DT child | `type` | `ct` | `part` | `channel` | `decouple` | registered name |
|---|---|---|---|---|---|---|---|
| 0 | `flash@1` | 0 | **1** | 0 | 0 | 0 | `aw36515-led0` |
| 1 | `flash@0` | 0 | **0** | 0 | 1 | 0 | `aw36515-led1` |

while the V4L2/media graph binding is:

| sub-device | fwnode | media link |
|---|---|---|
| `subdev_led[0]` (`aw36515-led0`) | `flash@0` (`ct = 0`) | `mtk-composite-v4l2-1` port 0 |
| `subdev_led[1]` (`aw36515-led1`) | `flash@1` (`ct = 1`) | `mtk-composite-v4l2-1` port 1 |

So `ct` as seen through `/dev/flashlight` is the **opposite** of `ct` as seen
through the media graph for the same physical channel.  This is stock
behaviour, it is reproduced exactly, and it must not be "fixed" in LieppOS
without a deliberate, separately documented decision.

Both `reg` values do match a `led_no`, so unlike AW36518/AW36518_V2 (whose
single child has `reg = 2` and therefore never matches) the AW36515
sub-devices **do** get a firmware node and **do** take part in the media
graph.

## Media graph

```
mtk-composite-v4l2-1 {
	compatible = "mediatek,mtk_composite_v4l2_1";
	port@0 { reg = <0>; endpoint { remote-endpoint = <&aw36515_flash0_ep>; }; };
	port@1 { reg = <1>; endpoint { remote-endpoint = <&aw36515_flash1_ep>; }; };
};
```

Aliases in the stock DT name these links explicitly:

```
flashlight_0 = "/mtk-composite-v4l2-1/port@0/endpoint"
flashlight_1 = "/mtk-composite-v4l2-1/port@1/endpoint"
fl_core_0    = "/soc/i2c@11e01000/aw36515@63/flash@0/port@0/endpoint"
fl_core_1    = "/soc/i2c@11e01000/aw36515@63/flash@1/port@1/endpoint"
aw36515      = "/soc/i2c@11e01000/aw36515@63"
```

Each sub-device registers with `media_entity_pads_init(&sd->entity, 0, NULL)`
(**zero pads**) and `entity.function = MEDIA_ENT_F_FLASH (0x20002)`, then
`v4l2_async_register_subdev()`.  The stock driver never calls
`media_entity_cleanup()` on removal — a vendor leak that is reproduced as-is.

## Position in the flash family

| | AW36515 | AW36518 | AW36518_V2 |
|---|---|---|---|
| node | `i2c@11e01000/aw36515@63` | `i2c@11e03000/aw36518@63` | `i2c@11d72000/aw36518_i2c13@63` |
| live device | `6-0063` | `8-0063` | `12-0063` |
| channels | **2** | 1 | 1 |
| `part` | **0** | 1 | 1 |
| `ct` | 0 and 1 | 0 | 1 |
| `flash-externel` | **present** (pin 116) | absent | absent |
| media links | **yes** (ports 0/1) | none (`reg = 2` never matches) | none (`reg = 3` never matches) |

`part = 0` with both colour temperatures present, plus the only external
strobe GPIO and the only real media-graph links on the board, identifies
AW36515 as the **primary camera flash pair**; the AW36518 pair (`part = 1`) is
the secondary assembly.
