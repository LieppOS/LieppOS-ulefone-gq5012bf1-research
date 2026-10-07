# SH366003 ↔ YFT-DEVINFO boundary (consumer side only)

Provider: stock `yft_devinfo.ko` (vendor_boot and vendor_dlkm copies identical, sha256
`0d5e547e…21fe`); first-stage insertion 145, immediately before `sh366003_fg` (146), loaded as
its `modules.dep` hard dependency. YFT-DEVINFO itself was **not modified** and its unfinished
reconstruction is **not used**: the consumer is built against `source/stock-yft-devinfo.symvers`,
three lines taken from the stock provider's `__kcrctab`/`__kcrctab_gpl`.

| symbol | kind | provider export | modversion CRC (stock `__versions` = rebuild) | KCFI | consumer call site (stock = rebuild, byte-exact) | return use | purpose |
|---|---|---|---|---|---|---|---|
| `yft_fuelgauge_device_add` | function | `EXPORT_SYMBOL` | **0xf5752941** | provider entry `0x076247bd` = `_ZTSFiP10i2c_driver<?>E` (2nd parameter is a named type not yet recovered in YFT-DEVINFO). **Irrelevant to the consumer:** called by direct `bl`, no KCFI check is emitted at the call site | `init_module`: `x0 = &sh_fg_driver` (`.data+0x10`), `w1 = wzr` (0), `bl`, then `i2c_register_driver(THIS_MODULE, &sh_fg_driver)` | ignored (`w0` overwritten) | registers the driver with YFT's device-info list before I2C registration |
| `yft_set_fuelgauge_device_used` | function | `EXPORT_SYMBOL` | **0x82093a2e** | provider entry `0x4d9b0091` = `_ZTSFiPciE` → `int (char *, int)` (PROVEN) | `sh_fg_probe` after scheduling the works: `x0 = "sh366003"`, `w1 = 1` | ignored | marks the fuel-gauge slot as used/identified |
| `fuelgauge_fw_version` | data | `EXPORT_SYMBOL_GPL` | **0x8c280260** | n/a (object, 30 bytes in provider `.data`) | probe: `sprintf(fuelgauge_fw_version, "Vno:0x%02x-%s(%02d%02d)\n", date, ascii, month, day)`; `show_fw_version`: `sprintf(buf, "%s\n", …)` | — | firmware/profile string shown by YFT devinfo and `/sys/class/3rd-gauge/fw_version` |

Calling convention: AAPCS64; pointer in `x0`, 32-bit integer in `w1`. The consumer declares
`int yft_fuelgauge_device_add(struct i2c_driver *, int)`; because the second argument is passed as
an `int`-width constant 0 and the return value is discarded, **any** int-sized enum/typedef in the
provider's real prototype yields identical consumer code and the identical CRC (the CRC comes from
the provider export, not from the consumer's declaration). Maximum formatted `fw_version` length
is 23 bytes incl. NUL (6+4+1+4+1+4+1+1+1) ≤ 30 — no overflow.

Proof that the boundary is exact: all three `__versions` entries equal stock; `.rela.init.text`
(21) and the probe call-site relocations are identical; consumer `init_module` and the
`yft_set_fuelgauge_device_used` call sequence are byte-identical. The provider's unresolved
parameter-type spelling is a YFT-DEVINFO question and does not affect SH366003 closure.
