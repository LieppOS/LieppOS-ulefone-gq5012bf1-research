# Source lineage

Public history: NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878`
(local mirror `/home/armol/kernel-work/public-mtk/nt6878.git`; branches
`mt6878/{Galaga,Galaxian,Tetris}/{u,v,16b}`).

## Per module

| module | compiled sources (vendor Makefile composition) | public match |
|---|---|---|
| clk-common | `clk-mtk.c clk-pll.c clk-gate.c clk-apmixed.c clk-cpumux.c reset.c clk-mux.c clkchk.c clk-fmeter.c mtk-pd-chk.c clkdbg.c` (+ headers). **There is no `clk-common.c`.** | alps5e41 unmodified |
| clk-mt6878 | `clk-mt6878.c` | alps5e41 + 0002 |
| clk-mt6878-bus | `clk-mt6878-bus.c` | alps5e41 unmodified |
| clk-mt6878-peri | `clk-mt6878-peri.c` | alps5e41 + 0002 |
| clk-mt6878-vlp | `clk-mt6878-vlp.c` | alps5e41 unmodified |
| clk-fmeter-mt6878 | `clk-fmeter-mt6878.c` (+ `clk-mt6878-fmeter.h`) | alps5e41 unmodified |

Kconfig: `CONFIG_DEVICE_MODULES_COMMON_CLK_MEDIATEK=m`, `CONFIG_COMMON_CLK_MT6878=m`,
`CONFIG_COMMON_CLK_MT6878_{BUS,PERI,VLP}=m` (from `mgk_64_k61_defconfig` @ 957dac).
`CONFIG_COMMON_CLK_MT6878` also selects `clk-bringup.o` (absent at alps5e41),
`clk-chk-mt6878`, `pd-chk-mt6878` and `clk-dbg-mt6878`; the 0001 wrapper restricts `obj-m`
to the six owned targets. `clk-fmeter-mt6878` is built under `CONFIG_COMMON_CLK_MT6878`.

## Blob history examined

| file | distinct public blobs | result against the pinned tree |
|---|---:|---|
| `clk-mt6878.c` | 8 | 5 pre-`591991d` blobs fail to compile (IDs removed from the later binding header); `c118b744` (`591991d`) differs in imports and data (pre-`7853c84` mux HWV); `433f4a89` (= alps5e41, `7853c84`) differs **only** by the DISP_PWM mux/parents/factor-parent; `b482f051` (`1f35ef8`, 2025 debug patch) lacks the same entries and changes further data — not a match |
| `clk-mt6878-peri.c` | 5 | 3 early blobs fail to compile; `630e08ca`, `7b1a6ae2` (= alps5e41) lack the two DISP_PWM gates |
| `mt6878-clk.h` (dt-bindings) | 7 commits | none defines `CLK_TOP_DISP_PWM_SEL`/`CLK_PERAOP_DISP_PWM0/1` after `0f65244` |

Upstream removal: ALPS `591991d44aad` "[ALPS08313573] clk: mediatek: mt6878: update clk data —
1. remove no owner clock node" (2023-10-31). GQ5012BF1 retains the node (it *has* an owner:
the display-PWM backlight). Patch 0002 is that commit's DISP_PWM hunk reversed, plus the
binding IDs at the end of their ranges, which is exactly what the stock tables encode.

`clk-mt6878-peri` PWM gate parents are `top_pwm_ck` in stock, i.e. ALPS `354978c` ("update pwm
clksrc", 2023-11-14) **is** present — the stock vendor tree is a post-Nov-2023 ALPS tree with the
DISP_PWM removal not taken (or reverted) for this board.
