# YFT / Ulefone NFC deltas

Donor baseline: NothingOSS MT6878 `device_modules`
`957dac185efe46cbf6336b0fff9516d84c8cd78f`,
`drivers/misc/mediatek/nfc/st21nfc/st21nfc.c`
(sha256 `5a9dee31d3c69dae50a0b93f3aff1a06395cfa6749b7cac81386db758062522f`).

Oracle: shipped GQ5012BF1 `st21nfc.ko` v2.2.0.19 from the **vendor ramdisk**,
sha256 `5c5945457f8e3f37744c95a98075278134a328590d27e00d38dd8de8261078e8`.

Against that donor the unmodified rebuild is only **7/24 functions byte-exact**;
after the deltas below it is **22/24 byte-exact with the remaining two
semantically equivalent** (`kernel/parity/st21nfc.parity.txt`).

## 1. Source-code deltas (confirmed by byte-identical rebuild)

| # | donor behaviour | GQ5012BF1 behaviour | evidence | confidence |
|---|---|---|---|---|
| D1 | 24 error-path messages use `pr_info` (`\x016` KERN_INFO) | the same 24 messages use `pr_err` (`\x013` KERN_ERR) | `.rodata.str1.1` string set: stock carries only the `\x013` variants; after the change `.rodata.str1.1` matches stock in size (3214 B) and string multiset | PROVEN |
| D2 | the two `[OPTIONAL] pidle_active_low (not) set` messages use `pr_debug` (`\x017`) | they use `pr_info` (`\x016`) | same string-set comparison | PROVEN |
| D3 | `st21nfc_power_stats_idle_signal()` writes `is_active = pidle_active_low ? !is_active : is_active;` (compiles to `eor`) | writes `value = gpiod_get_value(...); is_active = pidle_active_low ? (value == 0) : (value != 0);` (compiles to `cset eq` + `cset ne` + `csel`) | `st21nfc_pstate_wq` becomes byte-identical | PROVEN |
| D4 | `st21nfc_pstate_wq()` is a global symbol | it is `static` | stock `nm` shows `t st21nfc_pstate_wq`; making it static also restores stock's `.text` function order for the first five functions | PROVEN |
| D5 | probe cleanup: `err_pidle_workqueue:` tests `!IS_ERR_OR_NULL(gpiod_pidle)` | tests `!IS_ERR(gpiod_pidle)`, which lets the three error `goto`s branch straight at the label instead of re-testing for NULL | `st21nfc_probe` goes from +20 bytes to byte-identical | PROVEN |

There is **no functional Ulefone feature delta** in the driver: no added ioctl,
no changed GPIO sequence, no changed NCI handling, no YFT-specific hook (unlike
`hf_manager`, which gained `yft_devinfo` calls). The deltas are a different ST
source revision/log-level profile plus one cleanup-path refactor.

## 2. Build-configuration facts recovered

| fact | value |
|---|---|
| driver version string | `2.2.0.19` (`MODULE_VERSION`) |
| `ST54J_PWRSTATS` | **not defined** — the power-statistics filter, `power_stats` sysfs and the NCI header state machine payload counting are compiled out |
| `KRNMTKLEGACY_I2C` | **not defined** — plain `i2c_master_recv/send`, no MTK DMA buffer path |
| `CONFIG_NFC_DEBUG` | off (no `-DDEBUG`) |
| `CONFIG_NFC_ST54_SPI` | `=m` in the defconfig, but `st54spi.ko` is **not shipped** |
| placement | vendor **ramdisk** (`platform.cpio`, `modules.load` line 181), not `vendor_dlkm` — NFC is brought up in first stage |
| exported symbols | none (`st21nfc_register_st54spi_cb`/`_unregister` are plain globals) |

## 3. Board-configuration deltas (not source)

| # | item | GQ5012BF1 value | why it matters |
|---|---|---|---|
| B1 | no `pidle-gpios` in DT | the whole power-state/idle-signal/`power_stats` path is inert; `gpiod_pidle` stays `ERR_PTR` | explains why D3/D5 are only observable through codegen |
| B2 | `irq-gpios` = GPIO 2 (EINT 2, level), `reset-gpios` = GPIO 40, `clkreq-gpios` = GPIO 151 | board wiring | see `hardware/topology.md` |
| B3 | I²C6 `@0x11e01000`, slave `0x08` | board wiring | |
| B4 | CLF clock from SRCLKEN-RC `nfc` node, `xo-buf = "BBCK4"`, `sub-id = 0x0b` | no Linux clock/regulator for NFC | |
| B5 | `st21nfc_conf.txt` CustomA/CustomB/DPC/antenna blocks, CRC `0x4646` | board-specific RF tuning for this antenna (differential, EMI filter) | must be shipped unchanged, see `configuration/analysis.md` |
| B6 | `STNFC_FW_BIN_NAME="st21nfc_fw7.bin"` | selects the fw7 patch image; `st21nfc_fw.bin` is present but unused | |
| B7 | `NDEF_NFCEE_ENABLE=0` | the controller-resident Type-4 NDEF NFCEE (0x10) is disabled in stock even though the silicon and HAL support it | |
| B8 | AIDL NFC HAL is **V1** while the Mainline NFC module expects the newer `getConfig` layout | proven cause of `t4tNfceeEnable` always reading 0 | |
| B9 | `/data/nfc` ships labelled `system_data_file` with no file-context rule for `nfc_data_file` | stock SELinux bug; NFA persistent storage writes fail with EACCES | |

## 4. Explicit "no delta" statements

- `st21nfc.h` is **byte-identical** to the donor header — the ioctl numbering,
  magic `0xEA`, ST54-SPI callback codes and `ACCESS_OK` shim are unchanged.
- `Makefile` is unchanged.
- The ioctl surface, reset timings and recovery GPIO sequence are **pure ST
  reference behaviour**; Ulefone changed none of them.
