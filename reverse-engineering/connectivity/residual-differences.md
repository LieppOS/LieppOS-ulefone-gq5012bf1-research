# Residual differences

**None at module level.** All 22 connectivity modules in the inventory (plus 7 power_throttling
dependency modules) are function-exact, data-exact and ABI-exact. ABI covers imports, exports,
import/export modversion CRCs, modinfo, vermagic and section sizes, and KCFI hashes are inside
the compared function bytes. Full log: `binary-analysis/rebuild-all-parity.txt`.

## Build-environment facts needed for exactness (not source differences)

| item | requirement | why |
|---|---|---|
| tree location | `../vendor/mediatek/kernel_modules/connectivity` relative to `common/` | `__FILE__` in `pr_*`/`WARN` strings (conninfra 3 functions differed with an absolute path) |
| `TARGET_BUILD_VARIANT` | unset/empty | conninfra debug ops + BUILD_MODE 0, BT FW log/QA flags |
| `DRIVER_BUILD_DATE` | `20251022145214` | wlan `priv_driver_get_version` string |
| wlan make vars | `MODULE_NAME=wlan_drv_gen4m_6878 SEGMENT=SP` | selects `Kbuild.6878` |
| GKI-tree modules | `intree=Y`, `scmversion=g945dff7bc1bf` modinfo | vendor built them in-tree; `M=` builds omit both |
| KDM | power_throttling @6df320423600 | `LOW_BATTERY_LEVEL_NUM` = 6 in connadp |

## Things deliberately not claimed

* No proprietary firmware (connsys WF/BT/GNSS images, FM DSP patches), HAL or daemon is
  reconstructed.
* MLO hunks in `ais_fsm.c` are compiled out (`CFG_SUPPORT_802_11BE_MLO=0`). Their presence is
  proven only through `__LINE__` values, which pins the line count but not the exact text of
  the compiled-out lines. They are taken verbatim from ALPS V11.24.
* GPIO 92/131/132 levels are inferred (`hardware/mt6637.md`), not read.
