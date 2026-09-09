# `fingerprint.ko` pinctrl contract

## Acquisition and lookup order

`yft_finger_get_gpio_info(pdev)` calls
`devm_pinctrl_get(&pdev->dev)` once, stores the result in global
`yft_finger_pinctrl`, and then performs this exact required lookup order:

| order | lookup string | global field | used by |
|---:|---|---|---|
| 1 | `finger_reset_en1` | `yft_finger_reset_high` | `set_reset(1)` |
| 2 | `finger_reset_en0` | `yft_finger_reset_low` | `set_reset(0)` |
| 3 | `finger_spi0_mi_as_spi0_mi` | `yft_finger_spi0_mi_as_spi0_mi` | `set_spi_mode(1)` |
| 4 | `finger_spi0_mi_as_gpio` | `yft_finger_spi0_mi_as_gpio` | `set_spi_mode(0)` |
| 5 | `finger_spi0_mo_as_spi0_mo` | `yft_finger_spi0_mo_as_spi0_mo` | `set_spi_mode(1)` |
| 6 | `finger_spi0_mo_as_gpio` | `yft_finger_spi0_mo_as_gpio` | `set_spi_mode(0)` |
| 7 | `finger_spi0_clk_as_spi0_clk` | `yft_finger_spi0_clk_as_spi0_clk` | `set_spi_mode(1)` |
| 8 | `finger_spi0_clk_as_gpio` | `yft_finger_spi0_clk_as_gpio` | `set_spi_mode(0)` |
| 9 | `finger_spi0_cs_as_spi0_cs` | `yft_finger_spi0_cs_as_spi0_cs` | `set_spi_mode(1)` |
| 10 | `finger_spi0_cs_as_gpio` | `yft_finger_spi0_cs_as_gpio` | `set_spi_mode(0)` |
| 11 | `finger_eint_pull_down` | `yft_finger_eint_pull_down` | `set_irq(0)` |
| 12 | `finger_eint_pull_up` | `yft_finger_eint_pull_up` | `set_irq(1)` |
| 13 | `finger_eint_pull_dis` | `yft_finger_eint_pull_dis` | `set_irq(2)` |

Every lookup is required by the parser. The result is stored before `IS_ERR`
is tested. On the first failure it logs with `dev_err` and returns that
`PTR_ERR` value; it leaves prior state pointers and the pinctrl handle intact.
The platform probe ignores this return and still returns success.

`default`, `finger_power_en0`, and `finger_power_en1` occur in stock DT but are
not looked up by this module. No pinctrl state is explicitly selected during
probe.

## Hardware mapping from merged DT

| state | MT6878 pinmux and electrical data |
|---|---|
| reset low | GPIO30 mode 0 (`0x1e00`), slew 1, output-low |
| reset high | GPIO30 mode 0, slew 1, output-high |
| MI SPI | pin63 mode 2 (`0x3f02`), slew 0, bias-disable, output-low, Schmitt 0 |
| MI GPIO | pin63 mode 0 (`0x3f00`), slew 0, output-low, Schmitt 0 |
| MO SPI | pin62 mode 2 (`0x3e02`), slew 1, bias-disable, output-low, Schmitt 0 |
| MO GPIO | pin62 mode 0 (`0x3e00`), slew 1, output-low, Schmitt 0 |
| CLK SPI | pin60 mode 2 (`0x3c02`), slew 1, bias-disable, output-low, Schmitt 0 |
| CLK GPIO | pin60 mode 0 (`0x3c00`), slew 1, output-low, Schmitt 0 |
| CS SPI | pin61 mode 2 (`0x3d02`), slew 1, bias-disable, output-low, Schmitt 0 |
| CS GPIO | pin61 mode 0 (`0x3d00`), slew 1, output-low, Schmitt 0 |
| EINT pull-down | pin3 mode 0 (`0x0300`), slew 0, pull-down |
| EINT pull-up | pin3 mode 0, slew 0, pull-up |
| EINT disabled bias | pin3 mode 0, slew 0, bias-disable |

The unusual `output-low` declarations on SPI states are stock DT evidence and
are not normalized away.

## Selection error behavior

All setter functions prevalidate every state in their category. Missing state
means literal return `-1`. Once validation passes, each
`pinctrl_select_state()` result is discarded; later selections continue even
if an earlier selection fails, and the export returns 0.

No mutex protects global state or multi-state SPI transitions.
