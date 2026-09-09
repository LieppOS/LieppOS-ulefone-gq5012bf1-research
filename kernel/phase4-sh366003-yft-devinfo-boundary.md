# SH366003 ↔ stock yft_devinfo boundary

Stock `yft_devinfo.ko` is authoritative. The reconstruction does not use or ship the incomplete reconstructed provider.

| Symbol | Stock CRC | Recovered declaration | KCFI | Stock call site and purpose |
|---|---:|---|---:|---|
| `fuelgauge_fw_version` | `0x8c280260` | `extern char fuelgauge_fw_version[30];` | not applicable (data) | Probe writes `Vno:0x%02x-%s(%02d%02d)\n`, combining profile/date word, two-byte MAC 0x40d9 response, month and day; `fw_version` class attribute reads it |
| `yft_fuelgauge_device_add` | `0xf5752941` | `int yft_fuelgauge_device_add(struct i2c_driver *driver, int used);` | `0x076247bd` at stock provider entry | Module init calls `yft_fuelgauge_device_add(&sh_fg_driver, 0)` before `i2c_register_driver` |
| `yft_set_fuelgauge_device_used` | `0x82093a2e` | `int yft_set_fuelgauge_device_used(char *name, int used);` | `0x4d9b0091` at stock provider entry | Successful probe calls `yft_set_fuelgauge_device_used("sh366003", 1)` |

Calling convention is the standard AArch64 PCS. Both functions receive arguments in `x0`/`w1` and return `int` in `w0`; stock consumer ignores both return values.

## Build rule

`stock-yft-devinfo.symvers` supplies these exact CRCs to modpost through `KBUILD_EXTRA_SYMBOLS`. They are generated naturally in the consumer `__versions` section. There is no CRC patching, fake provider, ELF editing, or `KBUILD_MODPOST_WARN`.

The stock provider remains in the eventual test stack. This work does not attempt to close the historical 17/27 reconstructed-provider CRC gap.
