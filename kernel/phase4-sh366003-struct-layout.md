# SH366003 private-state layout

Stock probe allocates **0x428 bytes** with zeroing GFP flags. Known offsets are derived from direct loads/stores; gaps retain no invented semantics.

| Offset | Size | Field / evidence | Confidence |
|---:|---:|---|---|
| 0x000 | 8 | `struct device *dev` | proven |
| 0x008 | 8 | `struct i2c_client *client` | proven |
| 0x010 | 0x20+ | I2C transaction mutex | proven |
| 0x040 | 0x20+ | SOC cache mutex | proven |
| 0x070 | 0x20+ | voltage cache mutex | proven |
| 0x0a0 | 0x20+ | current cache mutex | proven |
| 0x0d0 | 0x20+ | temperature cache mutex | proven |
| 0x100 | 1 | client I2C address | proven |
| 0x101 | 7 | manufacturer-name bytes | proven |
| 0x108 | 0x40 | 16-entry command-descriptor array copied from `sh366003_regs` | proven |
| 0x148 | 0x88 | monitor `delayed_work` | proven |
| 0x1d0 | 0x88 | AFI-update `delayed_work` | proven |
| 0x258 | 4 | cached SOC | proven |
| 0x25c | 4 | cached voltage | proven |
| 0x260 | 4 | cached absolute current in uA | proven |
| 0x264 | 4 | cached external temperature | proven |
| 0x268 | 4 | fallback/update SOC | proven |
| 0x26c | 4 | fallback/update voltage | proven |
| 0x270 | 4 | fallback/update current | proven |
| 0x274 | 4 | fallback/update temperature | proven |
| 0x278 | 4 | select fallback quartet when equal to 1 | proven |
| 0x27c..0x287 | 0x0c | unknown/padding | unknown |
| 0x288 | 4 | manual force-upgrade request; initialized -1, sysfs-written, cleared after attempt | proven |
| 0x290 | 8 | registered `struct power_supply *` | proven |
| 0x298 | 0x68 | embedded `power_supply_desc` and adjacent zeroed fields | proven |
| 0x300 | 0x18 | `power_supply_config`; drv_data at 0x310 | proven |
| 0x318..0x347 | 0x30 | unknown/padding | unknown |
| 0x348 | 1 | adapter state from `primary_chg` online (0 or 2) | proven |
| 0x34c | 4 | gauge SOH register 0x2e | proven |
| 0x350 | 4 | synthetic displayed SOH, initialized 100 | proven |
| 0x354 | 4 | cycle count | proven |
| 0x358 | 4 | remaining capacity | proven |
| 0x35c | 4 | FCC | proven |
| 0x360 | 4 | unknown | unknown |
| 0x364 | 4 | VCHG | proven |
| 0x368 | 4 | ICHG | proven |
| 0x36c | 4 | BatteryStatus | proven |
| 0x370 | 4 | serial number | proven |
| 0x374 | 4 | sum of first two u16 words from MAC 0x0060 | proven |
| 0x378 | 4 | raw manufacture/profile date | proven |
| 0x37c | 4 | decoded day | proven |
| 0x380 | 4 | decoded month | proven |
| 0x384 | 4 | decoded year | proven |
| 0x388 | 4 | automatic AFI mismatch/status trigger | proven |
| 0x38c..0x427 | 0x9c | unused/unknown tail in observed code | unknown |

Globals hold `g_sm`, `gauge_interface`, `fg_sh366003_log`, `device2str`, `fuelgauge_id`, `cmp_buff`, I2C message scratch space and AFI scratch buffers. The parser is non-reentrant and relies on those global buffers.
