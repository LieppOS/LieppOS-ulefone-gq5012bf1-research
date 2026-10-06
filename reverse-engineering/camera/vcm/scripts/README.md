# scripts

| file | purpose |
|---|---|
| `sb.sh` | isolated `M=` rebuild + parity; workspace `~/kernel-work/gki-12901745-workspace/lieppos/vcm` (`trees/5e41` = shared clone of pristine ALPS base `2ae742f`). `sb.sh trees/5e41 main_vcm drivers/misc/mediatek/lens/vcm/v4l2/main_vcm main_vcm.o B1` (same for main2/3/4, sub); `sb.sh trees/5e41 camera_af_media drivers/misc/mediatek/lens/vcm/v4l2/media mtk-composite.o B1` |
| `decode-vcm-list.py` | decodes `vcm_list_0..5` of the stock `libcameracustom.lens.so` (record layout derived from the stock `GetVcmDriverName` disassembly) |
| `module-inventory.py`, `str-sec-parity.py` | inventory and string/section parity generators |

Function/data/abi/relocation parity: shared `reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py`.
