# flashlight.ko (D): OEM flashlight-core.c gap

| | |
|---|---|
| Identity | `flashlight.ko`, vendor_dlkm, sha256 `87b18cde1f47…` (full hash in MISSING-SOURCE-MATRIX.tsv) |
| modinfo | `license=GPL`, `author=Simon Wang <Simon-TCH.Wang@mediatek.com>`, `description=MTK Flashlight Core Driver` |
| Expected path | `drivers/misc/mediatek/flashlight/flashlight-core.c`, plus its Kconfig/Makefile and the defconfig fragment |
| Best source build | 32/51 functions byte-identical (KDM-MEDIA-SECURITY-BATCH-01 experiment, ALPS 5e415e05) |

## Proven differences (from stock, read-only, in earlier research)

- **Power-throttling configuration:** stock needs `CONFIG_MTK_FLASHLIGHT_PT=y` with strict mode.
  - `.data` shows `pt_strict=1` and levels 2/1/1.
  - The NothingOSS defconfig leaves PT unset; with PT unset, the public source fails to compile (`pt_low_bat_level`
    and others are undeclared).
- **Three extra functions** exist in no available revision: `flashlight_drvctrl`, `flashlight_sw_ctrl_show` and
  `flashlight_sw_ctrl_store`, plus an "ignore pt" path.
- **Missing callback:** stock drops the battery-OC callback that the public variants register. The stock DT
  nevertheless sets `battery-oc-level = <2>`.
- **Remaining functions:** the other 19 differ as a consequence of the above.

## Sources already searched (not repeated)

ALPS 5e415e05, NothingOSS device_modules 957dac18, MiCode trees and local vendor trees. No new authentic revision
was identified this session, so no search was repeated.

## Dependants

`aw36515`, `aw36518` and `aw36518_v2` (Codex batch-02) register with flashlight-core.

## Request

Covered in `ULEFONE-SOURCE-REQUEST.md` §2.1: the exact `flashlight-core.c` and flashlight Kconfig/defconfig as
built for GQ5012BF1. The module is GPL, so this is a distributed GPL component.
