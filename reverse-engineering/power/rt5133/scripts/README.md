# scripts

| file | purpose |
|---|---|
| `sb.sh` | `sb.sh <kdm-root> <module> <subdir> "<objs>" [tag]` — isolated `M=` rebuild of one kernel_device_modules module against exact GKI 12901745 (`lieppos/nfc/kout`), strip, parity vs `stock/<module>.ko`. Used as `sb.sh trees/5e41 rt5133-regulator drivers/regulator rt5133-regulator.o B1` and `sb.sh trees/5e41 extdev_io_class drivers/misc/mediatek/subpmic extdev_io_class.o B1`. Workspace: `~/kernel-work/gki-12901745-workspace/lieppos/power` (own `git clone --shared` of the pristine 5e41 tree). |
| `secdiff.py` | per-section byte comparison of two `.ko` |
| `module-inventory.py` | `kernel/module-inventory.tsv` generator |
| `str-sec-parity.py` | `parity/*/string-parity.tsv` + `section-parity.tsv` |

Parity TSVs (function/data/abi/relocation) come from the shared
`reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py`.
