# mt6369-accdet — falsifiable source-layout experiments

Stock `e4a9fd98…` (109720 B). Every variant compiles the full module in the Codex
dev tree with identical pins/config; `try-accdet.sh` records residual bytes vs stock.
Diffs are against the historical research source (`reverse-engineering/audio/mt6369/source/mt6369-accdet.c`).

| Variant | Change | Content sections exact | `.bss` order | `__key` suffix | Differing bytes |
|---|---|---:|---|---|---:|
| base | historical source (extern decl at 184; tentative def before yft function) | 33/35 (`.rela.text`, `.rodata.str1.1`) | g_gpio at 72 (stock 0) | .73 vs .74 | 814 |
| v1 | `int g_gpio_accdet_fm_switch = 0;` at former extern line | 33/35 (string order) | exact | .73 | 328 |
| v2 | v1 + static helper `yft_parse_dts2()` with `__func__` | **35/35** | exact | .72 | 269 |
| v5/v6 | definition moved before `MODULE_DEVICE_TABLE` (adjacent to `accdet`) | 35/35 | exact; local symbol order exact | .72 | 258 |
| c3 | v6 + caller literal "yft_accdet_fm_switch" after first `__func__` | 35/35 | exact | .72 (no effect) | 258 |
| c1/c4 | v6 + helper printk passes literal `"yft_parse_dts2"` | 35/35 | exact | .73 | 145 |
| **c5** | v6 + helper literal + first caller printk literal `"yft_accdet_fm_switch"` | **35/35** | exact | **.74** | **20 = GNU build ID only** |
| c6 | c5 with tentative `int g_gpio_accdet_fm_switch;` | 34/35 | — | — | 517 (falsified) |

Mechanism (verified, not assumed): clang deduplicates identical string contents across
literals and `__func__`; the first creator decides whether the IR global is `.str.N` (advances
the module-wide unique-name counter) or `__func__.<fn>` (does not). Lock-class key names
(`fn.__key.N`) share that counter, so the stock suffix fixes how many first-created literal
strings precede `mt6369_accdet_probe`. Deferred static helpers emit their strings after the
non-static caller, which reproduces the stock string-pool order. A real initializer is
emitted at its definition; `MODULE_DEVICE_TABLE`'s alias forces `of_match` emission at line 137,
so the definition must precede it.

Evidence of ODM style: the LN2403 camplight driver (exact reconstruction) passes literal
parse-function names (`"ln2403_parse_dts"`) as `%s` arguments, and other YFT drivers use
`yft_*parse_dts*` helpers (`leds-rgb-aw2013`, `extcon-mtk-usb`). The literal/`__func__`
choice for strings with identical contents is binary-invisible except for this counter;
c5 is the source form that reproduces stock byte-for-byte. No code, data, CRC or symbol
was patched in any object.
