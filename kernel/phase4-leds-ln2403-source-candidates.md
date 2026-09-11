# LN2403 source-candidate audit

## Result

`NO_PUBLIC_DONOR_FOUND` / `NO_USEFUL_SOURCE` reconfirmed.

No candidate containing the stock driver identity, compatible, sysfs ABI, named
functions, mode strings, or state machine was found. The reconstruction therefore
uses the frozen stock ELF as its behavioral oracle; no generic LED/PWM driver is
claimed as lineage.

## Searches

Exact and case-varied searches covered:

- `leds_ln2403`, `leds-ln2403`, `ln2403`, `LN2403`, `Module For PWM LN2403`;
- `mediatek,yft_camplight`, `yft_camplight`, `camplight_mode`,
  `camplight_set_brightness`, `leds_ctl`;
- `redblue_led_timer_func`, `ln2403_gpio_ctrl_apply`, `ln2403_pwm_work`,
  `gpio_ctrl_timer_handler`, `set_leds`, `ln2403_get_gpio`;
- all three pinctrl state names.

The bounded search covered the local Nothing MT6878 source mirror, local
MediaTek/Motorola/MiCode/OnePlus/OPPO/realme/Transsion/Sony trees and indexes,
plus GitHub and general public web indexes. Previous `NO_EXACT_HIT` results in
`unknown-exact-audit.md` were rechecked. Public hits were generic Linux LED/PWM
material, unrelated flashlight code, LN2403 component references, or stock
binary inventories only.

## Classification

| candidate | classification | reason |
|---|---|---|
| mainline generic PWM LED drivers | `STRUCTURAL_DONOR_ONLY` | wrong ABI, DT, provider API and mode state machines |
| Nothing MT6878 MediaTek PWM tree | `EXACT_SOURCE` **for provider only** | reproduces both provider functions byte-for-byte and both CRCs; not an LN2403 consumer donor |
| public/local vendor trees searched | `NO_USEFUL_SOURCE` | no stock identifiers or matching implementation |

The exact provider source is pinned separately in
`phase4-leds-ln2403-provider-abi.md` and must not be confused with target-driver
source provenance.
