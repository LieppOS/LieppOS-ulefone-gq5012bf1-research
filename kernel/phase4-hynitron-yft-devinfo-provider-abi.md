# Hynitron → stock yft_devinfo provider ABI

The provider is the frozen stock `yft_devinfo.ko` (SHA256
`0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe`),
not the reconstructed provider. Its three exact entries are frozen in
`workspace/phase4-hynitron/oracle/stock-yft-devinfo.symvers`.

| Symbol | Stock CRC | Prototype/type | Provider KCFI | Stock Hynitron call/use | Return handling / purpose |
|---|---:|---|---:|---|---|
| `second_touch_fw_version` | `0x7198d58d` | `extern char second_touch_fw_version[30]` | N/A (object) | `cst8xx_firmware_info` at `.text+0x36cc` passes it to `sprintf` after successful register `0xA6` six-byte read | Stores `Vno: %x. %x. %x. %x.\n` using running-chip fields in order firmware, checksum, module ID, project ID; provider exposes it in device-info output. It reflects the running controller, not packaged firmware. |
| `yft_touchpanel_device_add` | `0xf5ba4446` | `int yft_touchpanel_device_add(struct i2c_driver *driver, int used)` | `0x076247bd` | `init_module` `.init.text+0x4c`: `(&hynitron_i2c_driver, 0)` immediately before `i2c_register_driver` | Return is ignored. Adds the I2C driver identity to YFT's touch registry as initially unused. The historical stock CRC is not reproducible from the reconstructed provider/type graph, so final modpost uses the frozen stock witness. |
| `yft_set_touch_device_used` | `0x0a0f3b69` | `int yft_set_touch_device_used(char *name, int used)` | `0x4d9b0091` | `hyn_probe` `.text+0x230c`: `("hyn_ts", 1)` only after input/IRQ/update/sysfs/gesture/reset success | Return is ignored. Marks this registered touch candidate active for YFT device/factory reporting. No failure-path or remove call exists. |

The call sites are direct relocations; no alternate provider edge exists. The
stock module has exactly these three yft_devinfo imports. No CRC patching or
manual `__versions` editing is permitted or used.
