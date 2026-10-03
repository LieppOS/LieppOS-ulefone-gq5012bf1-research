# SC8510 (sc851x_charger) 2S↔1S bidirectional switched-capacitor converter: DONE

## Result

| item | value |
|---|---|
| stock module | `vendor-ramdisks/platform-extracted/lib/modules/sc851x_charger.ko` |
| stock SHA256 | `b5e5f08bcfe37ac8c81525b0d4fe514902b552cc45b7f99fbeda8b80f6c2aa0c` (28,488 B) |
| modinfo | `SC SC851X Driver`, `South Chip <Aiden-yu@southchip.com>`, GPL v2, `depends=` (empty), driver version string `1.0.0_G` |
| match table | `sc,sc851x`, `sc,sc8510`, `sc,sc8517`. The board uses **`sc,sc8510`** |
| source | `source/sc851x_charger.c` (DM tree `drivers/power/supply/sc851x_charger.c`, commit `7846896`) |
| **function parity** | **11/11 exact** |
| **data parity** | **8/8 exact** |
| **ABI** | **exact**: imports 29/29, modversions 30/30, modinfo 6/6, section sizes 14/14 |

The earlier phase-4 reconstruction had a probe and `register_interrupt`
residual. Restructuring both into SouthChip's public template form closed
it:

- `if (gpio_is_valid()) {…} else {…}` with `gpio_to_irq()`;
- `err_kzalloc` label;
- `device_create_file(&client->dev)`;
- the `const struct reg_field *reg_fields` loop.

The same SouthChip template is the donor for SC8571; see
`../sc8571/README.md`.

## Hardware contract

- **Bus and address:** `/soc/i2c@11e01000` (i2c-6), `reg=<0x69>`. The node
  name `sc851x-charger@6f` is a stale unit address; the live device was
  `6-0069`.
- **IRQ:** GPIO 12, falling (`sc,sc851x,irq-gpio = <&pio 12 2>`). The
  handler only logs FLAG1–3 (0x0c–0x0e).
- **Register map:** 50 `reg_field`s (stock-exact table) are listed in
  `kernel/phase4-sc851x-register-fields.tsv`. 36 are written from DT at
  probe, after `REG_RST` (0x06 bit 3). 14 are allocated only.

DT programming:

| field | value |
|---|---|
| `v2x-ovp` | 2 |
| `v2x-uvlo` | 1 |
| `v2x-s2f` | 1 |
| `v1x-ovp` | 23 |
| `v1x-scp-dis` | 1 |
| `vac-ovp` | 15 |
| **`fwd-ocp`** | **4** |
| **`rvs-ocp`** | **15** (max) |
| `fwd-ocp-dis` / `rvs-ocp-dis` | 0 / 0 |
| `wdt` | 0 |
| `lnc-ss-timeout` | 3 |
| `audio-en` | 1 |
| `audio-into-dg` | 1 |
| `freq` | 6 |
| `ref-skip-r` | 5 |
| `skip-hyst` | 3 |
| `tshut-dis` | 1 |

Physical units for SC8510 codes are not public. Only the raw codes are
claimed.

## Exact role (answers)

| question | answer | evidence |
|---|---|---|
| Primarily reverse charging? | **No.** It is the always-present 2S-pack ↔ 1S-domain bridge. | DT field naming: V2X = 2× (pack) side, V1X = 1× side. FWD = V2X→V1X (discharge), RVS = V1X→V2X (charge). SouthChip product page: "10-A battery discharging in forward 2:1, 4-A charging in reverse 1:2, load switch, keeps 1S-equivalent downstream architecture with a 2S pack". |
| Does it participate in forward charging? | **Yes, for MT6375 (non-direct) charging.** The MT6375 buck charges a 1S "cell-equivalent" node (CV 4.45 V) and SC8510's 1:2 reverse mode lifts it into the 2S pack. Direct PE5 charging bypasses it through SC8571 into the pack. | mtk_charger `battery-cv=4450000`; PE5 `vbat-cv=8750`; YFT `cv*2` in PE5 |
| buck / boost / buck-boost? | None. It is a **switched-capacitor 2:1 / 1:2 charge pump** plus a load switch. | silicon class and field set (no inductor-mode fields) |
| OTG source? | **Not directly.** USB VBUS is sourced by the MT6375 `usb-otg-vbus` boost. SC8510 supplies the 1S rail that the boost draws from, in forward mode. | `extcon-usb vbus-supply` → MT6375 `chg/otg`; SC8510 node has no regulator or extcon edge |
| Why bidirectional? | The phone must discharge the 2S pack into 1S-rated loads (SoC PMIC, MT6375 VSYS) and must charge the pack from the 1S switching charger. | as above |
| Which software path enables it? | **None.** The stock driver never writes a mode, direction, enable or OTG bit. It programs protections at probe and clears `AUDIO_EN` at shutdown. Operation is hardware-autonomous. | exact source: `sc851x_init_device` / `sc851x_charger_shutdown` |
| Which Type-C role transition triggers it? | None in software. A source-role transition enables the MT6375 OTG boost (tcpc → extcon-mtk-usb → `usb-otg-vbus` regulator + GPIO 37). SC8510 follows load direction in hardware. | `workspace/usmart-audit/kernel/usmart-mt6375-otg-contract.md` |
| Kernel consumers | **None.** It has no exports, no `depends`, and no charger_class, power_supply, regulator, extcon or tcpc imports. A userspace sweep found no `sc851x`/`sc8510` references. | `kernel/usmart/usmart-sc851x-power-path.md` |
| "Audio power" classification | **Obsolete.** `AUDIO_EN`/`AUDIO_FREQ`/`AUDIO_INTO_DG` are switching-frequency modes for the charge pump (keeping light-load switching out of the audio band). They are not an audio rail. | field names and placement (0x06 [2:0], with `FREQ` 0x07[3:0] and `SKIP_HYST` 0x08); no audio driver consumer |

Bounded unknowns are runtime only:

- the physical code→volt/amp tables;
- which pins are wired to which board rails, which needs a schematic.

Neither unknown affects the source or ABI closure.
