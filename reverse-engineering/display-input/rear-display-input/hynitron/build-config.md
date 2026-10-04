# Hynitron stock build configuration (proven)

Every gate below is proven by the exact build. Changing any one changes
function bytes, strings, `__COUNTER__` IDs, or the section set, and breaks the
65/65 result.

## Toolchain / kernel

| item | value | evidence |
|---|---|---|
| kernel tree | CI-12901745 GKI (`android14-6.1`), MTK `kernel_device_modules-6.1` | vermagic + 54/54 import CRCs |
| compiler | clang r487747c (`.comment` equal) | `.comment` byte-equal |
| LTO | `CONFIG_LTO_NONE` | ThinLTO build: 57/65 functions, renamed `.rela.text.*` sections |
| KCFI | `CONFIG_CFI_CLANG=y` | 59 preambles equal; 6 direct-only statics have none |
| extra flag | global `KCFLAGS=-faddrsig` | stock `.llvm_addrsig` (65 B) present; covers `hynitron.mod.o` too, so `ccflags-y` is insufficient |
| debug info | stock stripped (`--strip-debug`) | no `.debug_*` in stock |
| module deps | `yft_devinfo` (`yft_set_touch_device_used`) | `depends=` modinfo |

## Source/file layout

`hynitron-y := core i2c esd_check tool_debug update_firmware gesture proximity`
(link order proven by `.text` order and `__versions` order). `esd_check.c`
and `proximity.c` compile to empty objects but are linked.
`MODULE_LICENSE("GPL v2")` exists only in `hynitron_core.c`; the stray
`MODULE_LICENSE("GPL")` in donor esd/proximity files is removed (stock has
exactly one `license=`). `hynitron_core.c` includes `<linux/pm_runtime.h>`
after the local headers. This consumes exactly one extra `__COUNTER__`, so
the `__UNIQUE_ID_*` suffixes match (466/467/468/469/470).

## Feature gates (`hynitron_config.h`, `hynitron_core.h`, `hynitron_gesture.c`)

| define | value | evidence |
|---|---|---|
| `HYN_DEBUG_EN` | 1, `HYN_DEBUG_LEVEL` 1 | all logs present as `KERN_ERR "[HYN]..."` without `__func__`; no buffer dump |
| `HYN_MT_PROTOCOL_B_EN` | 0 | `input_mt_sync`/`BTN_TOUCH`, no `input_mt_*slot` imports |
| `HYN_REPORT_PRESSURE_EN` | 0 | no `ABS_MT_PRESSURE` setup |
| `HYN_GESTURE_EN` | 1 | gesture functions + sysfs group |
| `HYN_GESTURE_CAP_CST8XX` | 0 | gesture header read 8 B from 0x01, not 0xD3 table |
| `HYN_PSENSOR_EN` | 0 | proximity object empty |
| `HYN_ESDCHECK_EN` | 0 | esd object empty |
| `HYN_AUTO_FACTORY_TEST_EN` | 0 | `hyntpfactorytest_*` are stubs (40/52 B) |
| `HYN_EN_AUTO_UPDATE*` (all) | 0 | no `cst*_boot_update_fw` / erase / program code; probe never calls `hyn_boot_update_fw` |
| `HYN_SYS_AUTO_SEARCH_FIRMWARE` | 0 | no `/data`/`/sdcard` file I/O imports |
| `HYN_EN_AUTO_UPDATE_WORKQUEUE` | 0 | struct size 584 without fw work |
| `ANDROID_TOOL_SURPORT` | 0 | no proc-fs / tool functions (65-function surface) |
| `HYN_SYSFS_NODE_EN` | 1 | 7 `dev_attr_*` objects |
| `HYN_RESET_SOFTWARE` | 0 | `hyn_reset_watchdog_proc` is 4 B (`ret`) |
| `HYN_IIC_TRANSFER_LIMIT` | 0 | single-message `i2c_transfer` paths |
| `HYN_UPDATE_FIRMWARE_FORCE` | 0 | absent code |
| `HYN_CHIP_TYPE_CONFIG` | `CST820` (0xB7) | `hyn_ts_data_init` immediate |
| `HYN_IRQ_TRIGGER_RISING_CONFIG` | 0 (falling + ONESHOT) | `hyn_irq_init` flags 0x2002 |
| `HYN_MAIN_IIC_ADDR_CONFIG` | 0x15 | `hyn_ts_data_init` |
| `HYN_X/Y_DISPLAY_DEFAULT` | 340/340 | `hyn_ts_data_init` immediates |
| `HYN_MAX_POINTS` / `HYN_MAX_KEYS` | 1 / 0 | `POINT_READ_BUF`=9, `touch_info` size 20 |
| `HYN_DRIVER_VERSION` | `Hynitron TouchScreen Qualcomm Driver V2.1 20201222` | string |
| `CONFIG_HAS_EARLYSUSPEND`, `CONFIG_FB` paths | off | no notifier imports |

## `#line` anchors

41 `HYN_FUNC_EXIT()` sites carry `#line N` with the stock `__LINE__`
immediate. Stock line numbers match no public donor (PA13 V2.1 median offset
184 lines, V2.2/V3.x 67–178). This proves the original file was a private
YFT revision. The anchors are the minimum-assumption reproduction.
