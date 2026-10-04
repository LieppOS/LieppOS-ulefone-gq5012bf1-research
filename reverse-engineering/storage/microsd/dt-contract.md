# MSDC1 (microSD) DT contract (live stock DT vs donor)

Node `soc/mmc@11240000`, `compatible = "mediatek,mt6878-mmc"`, `status = "okay"`.

| property | live stock (GQ5012BF1) | donor ALPS `mt6878.dts` + `cust_mt6878_msdc.dtsi` | driver use |
|---|---|---|---|
| `reg` | `0x11240000/0x1000`, `0x11d80000/0x1000` | same | MSDC base + top (pad/tune) base |
| `interrupts` | GIC SPI 388, level-high | same | `msdc_irq` |
| clocks | `source`=TOP MSDC30_1_SEL, `bus_clk`=TOP MSDC30_1_HCLK_SEL, `source_cg`/`macro`/`hclk`/`pclk_cg`/`axi_cg` = PERAO MSDC1, MSDC0_H, MSDC1_H, MSDC1_SLV_H, MSDC1_MST_F | same | no `crypto_clk` |
| `host-index` | 1 | 1 | `host->id` |
| `bus-width` | 4 | 4 | |
| `max-frequency` | 200 000 000 | same | `f_max`; `f_min` = src/(4·4095) (12-bit divider) |
| `cap-sd-highspeed`, `sd-uhs-sdr12/25/50/104`, `sd-uhs-ddr50` | yes | yes | UHS-I up to SDR104 |
| `no-mmc`, `no-sdio` | yes | yes | SD-only |
| `ocr-voltage` | `0x30000` (MMC_VDD_28_29 \| 29_30) | same | `mmc->ocr_avail = host->ocr_volt` |
| `cd-gpios` | **`<&pio 14 0>` (GPIO_ACTIVE_HIGH)** | `<&pio 14 GPIO_ACTIVE_LOW>` | `mmc_gpiod_request_cd` |
| `cd-debounce-delay-ms` | 0 | 0 | |
| `vmmc-supply` | **MT6369 `vmch-eint-low`** (`mt6369_vmch_eint_low`, 1.2–3.5 V) | MT6369 `vmch_eint_high` | card VDD (3.0 V class). The PMIC VMCH EINT variant follows CD polarity |
| `vqmmc-supply` | MT6369 `vmc` (1.2–3.5 V) | same | I/O voltage 3.3 V ↔ 1.8 V switch |
| `pinctrl-names` | `default`, `state_uhs` | same | `msdc_ops_switch_volt` selects `state_uhs` at 1.8 V |
| pins | GPIO77 CLK, 78 CMD, 79–82 DAT0–3 (func 1); drive-strength 3; CMD/DAT pull-up R1R0=01 (`0x65`); CLK pull-down R1R0=10 (`0x66`); both states identical | same | |
| write-protect | none (`wp-gpios` absent) | none | |
| `supports-cqe` | absent | absent | CQHCI not used for SD |

MSDC0 (`soc/mmc@11230000`, eMMC, HS400, CQE, `crypto_clk`) is `status = "disabled"` on this UFS board.

## Card-detect polarity

The donor declares CD active-low; GQ5012BF1 declares active-high. This is a board hardware difference in the card-socket switch (normally-closed vs normally-open), and the VMCH regulator variant is switched consistently (`vmch-eint-low` instead of `vmch-eint-high`). Both are proven from the live DT. Runtime insert/remove was **not** tested, by rule.
