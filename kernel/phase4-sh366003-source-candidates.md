# SH366003 source-candidate search

## Result

`NO_PUBLIC_DONOR_FOUND`

The frozen GQ5012BF1 ELF remains the only exact implementation available in the local corpus or public search results. The stock string table identifies the lost source path as:

`../kernel_device_modules-6.1/drivers/power/supply/sh366003/sh366003_fg.c`

but that source file is not present in the exact GKI workspace, NothingOSS MT6878 research tree, MiCode MTK device-module reference tree, proprietary extraction, backups, or stock partitions.

## Searches performed

Local, filename, content, and public searches covered:

- `sh366003`, `SH366003`, `sh,sh366003`, `sh366003_fg`
- `fuelgauge_fw_version`, `fg_monitor_workfunc`
- `sinofs_afi_data`, `file_decode_process`, `CMD_AFI_STATIC_SUM`
- `AFI`, `afi_update`, `afi_upgrade`, Sino Wealth/Sinowealth fuel gauge
- GitHub, Gitee, Android BSP mirrors and search-indexed vendor trees
- local NothingOSS MT6878 and MiCode/MediaTek device-module trees

Public results establish only that SH366003 is a Sino Wealth multi-cell fuel-gauge family part. They do not expose a Linux driver, register reference, or matching AFI parser.

## Candidate classification

| Candidate | Classification | Reason |
|---|---|---|
| Frozen GQ5012BF1 `sh366003_fg.ko` | `EXACT_SOURCE` behavioral oracle only | Exact board binary, symbols, relocations and embedded AFI image; no C source |
| Lost path named by stock ELF | `EXACT_SOURCE` path evidence | Exact source pathname string, file unavailable |
| Sino Wealth public product pages | `REGISTER_MAP_DONOR` identity only | Confirms vendor/family, no usable register map or Linux source |
| Smart Battery / TI-style ManufacturerAccess conventions | `STRUCTURAL_DONOR_ONLY` | Helps name standard SBS commands; stock code remains authoritative |
| NothingOSS/MiCode/other Android gauge drivers | `NO_USEFUL_SOURCE` | No SH366003 identifiers, AFI format, command table, or matching ABI |

A generic SBS gauge is deliberately not substituted: stock has a custom MAC transport, embedded 2,142-byte AFI program, YFT registration, nonstandard public units, writable class controls, and board-specific update gating.
