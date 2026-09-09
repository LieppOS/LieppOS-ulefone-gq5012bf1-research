# SH366003 userspace and vendor integration

## Kernel-facing integration

- `3rd-gauge` is consumed directly by `mt6375-battery.ko` update/property/daemon-handler paths.
- `mtk_charger_framework.ko:get_uisoc` also obtains `3rd-gauge` and requests a property.
- MT6375 republishes stock SH366003 values through the main `battery` supply, multiplying voltage mV→uV and FCC mAh→uAh.
- Android's normal BatteryService-facing endpoint is therefore the republished `battery` supply, not a direct hardcoded `3rd-gauge` userspace lookup.

## YFT integration

Probe publishes device-used state as `sh366003` through stock `yft_devinfo.ko`. It writes the provider's global `fuelgauge_fw_version[30]`, which the provider exposes in vendor device-information surfaces. The exact consumer import CRCs are in `phase4-sh366003-yft-devinfo-boundary.md`.

## Driver class ABI

Stock creates class `sh_fg` and attributes:

| Attribute | Mode | Meaning |
|---|---:|---|
| `chipid` | 0664 | show device ID; store is a no-op |
| `force_upgrade` | 0664 | show/store manual AFI trigger |
| `fw_version` | 0664 | show YFT firmware string; store is a no-op |
| `manufacturing_date` | 0664 | show raw date; stock store can unseal/write profile date (**dangerous**) |
| `manufacturing_year` | 0444 | decoded year |
| `manufacturing_month` | 0444 | decoded month |
| `manufacturing_day` | 0444 | decoded day |
| `manufacturename` | 0444 | seven-byte MAC 0x004c name |
| `serialnum` | 0444 | MAC 0x004e serial |
| `soh` | 0444 | synthetic cycle-derived display value |

The reconstruction safety gate rejects dangerous `force_upgrade` and manufacturing-date programming by default while preserving read-only telemetry and the recovered code path.

## Stock partition search

No init `.rc`, SELinux policy, HAL, app, daemon, or external firmware file contains an SH366003-specific programming contract. Vendor `fuelgauged` services/configuration belong to the MediaTek/NVRAM primary gauge path; no stock evidence links them to the embedded SH366003 AFI interpreter.
