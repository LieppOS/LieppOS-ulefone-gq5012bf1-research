# VTDR6115 main panel — hardware / DT contract

All values PROVEN from the merged stock device tree
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`) and from
the shipped `panel-ky-vtdr6115-dphy-cmd.ko` unless marked otherwise.

## Fitted part

| item | value | evidence |
|---|---|---|
| DDIC | Samsung/Visionox **VTDR6115** AMOLED driver IC | module name, `MODULE_DESCRIPTION("vtdr6115 VDO 120HZ AMOLED Panel Driver")`, DT compatible |
| module vendor tag | `ky` (panel-module maker), `hx` prefix | DT compatible `hx,vtdr6115,cmd,120hz,ky` |
| Ulefone driver string | `yft-lcm-vtdr6115-drv` | 11 distinct log strings in `.rodata.str1.1` |
| resolution | **1080 × 2400** | `dsc_params.pic_width/pic_height`, all three `drm_display_mode` |
| colour depth | 8 bits per component | `dsc_params.bit_per_channel = 8` |
| physical size | **not encoded** — `physical_width_um`/`physical_height_um` are zero in all three 66328-byte `ext_params` blobs | stock `.data` |

## DSI host and link

| item | value | evidence |
|---|---|---|
| DSI host | **dsi0** (`dsi1@1401b000` is `status = "disabled"`) | DT |
| node | `panel1@0`, `reg = <0>`, child of the dsi0 port/endpoint graph | DT |
| compatible | `hx,vtdr6115,cmd,120hz,ky` | DT + both module `alias=of:N*T*Chx,vtdr6115,cmd,120hz,ky` entries |
| PHY | **D-PHY** (`phy-names = "dphy"`; `ext_params.is_cphy = 0`) | DT + stock `.data` |
| mode | DSI **video mode** at runtime despite the `cmd` in the compatible string — `MODULE_DESCRIPTION` says *VDO*, the probe log prints `lcm,vtdr6115,vdo,120hz`, and `vdo_per_frame_lp_enable = 1` | module strings + `.data` |
| lanes | 4 (MT6878 dsi0 default; `lane_swap_en = 0`, `pn_swap` all zero) | `.data` |
| PLL clock | **435 MHz** (`pll_clk = 435`) | `.data` |
| data rate | **870 Mbps/lane** (`data_rate = 870`) | `.data` |
| output mode | `MTK_PANEL_DSC_SINGLE_PORT` | `.data` |
| TE | `dsi-te` node, `interrupts = <0x59 0x01>` → **EINT 89**, `mediatek, dsi_te-eint` | DT |

## Board power / control lines

| function | DT property | GPIO | note |
|---|---|---|---|
| reset | `reset-gpios = <&pio 0x5a 0>` | **GPIO 90** | active high in DT cell, driven by the driver with explicit levels |
| VCI | `vci-gpios = <&pio 0x27 0>` | **GPIO 39** | load-switch enable, not a Linux regulator |
| DVDD | `dvdd-gpios = <&pio 0x26 0>` | **GPIO 38** | load-switch enable, not a Linux regulator |
| power-domain | `powerdm-gpios = <&pio 0xc2 0>` | **GPIO 194** | present in DT, **never requested by the driver** |
| gate IC | `gate-ic = <0x00>` | none | the other two panels on the same host use `<0x12df>` |
| pinctrl | `pinctrl-names = "default"` only, **no `pinctrl-0`** | — | nothing to apply |
| regulators | **none** | — | there is no `regulator-*` property and no `devm_regulator_get` in the driver |

Both rails are driven as plain GPIOs through `devm_gpiod_get(dev, "vci"/"dvdd",
GPIOD_OUT_HIGH)` followed by `gpiod_set_value()` and an immediate
`devm_gpiod_put()` — the descriptor is acquired and released around every
transition, which is a Ulefone/YFT idiom, not MediaTek's.

## Backlight

- `backlight = <...>` phandle is read in `lcm_probe` via
  `of_parse_phandle(dev->of_node, "backlight", 0)` and attached with
  `of_find_backlight_by_node()`; brightness is nevertheless driven in-band over
  DSI (DCS `0x51`, 12-bit) by `lcm_setbacklight_cmdq`.
- `ext_params.hbm_en_time` / `hbm_dis_time` are **0** — there is no timed HBM
  ramp.

## Bootloader handoff

`lcm_probe` sets `ctx->prepared = true; ctx->enabled = true;` and logs
`"vtdr6115,120hz dsi_node:%s set prepared = enabled = false"` — the driver
assumes the bootloader (LK) has already powered and initialised the panel, so
the first `lcm_prepare()` is a no-op and no re-initialisation happens on the
boot path.

## Other panels on the same DSI host (not fitted)

`panel2@1` = `jdi,nt36672e,vdo,60hz`, `panel3@2` = `truly,td4330,cmd` — both
have `gate-ic = <0x12df>` and `reset-gpios = <&pio 0x5a>`; neither has
`vci-gpios`/`dvdd-gpios`. The driver's probe explicitly rejects a non-matching
remote node (`"%s+ skip probe due to not current lcm"`).
