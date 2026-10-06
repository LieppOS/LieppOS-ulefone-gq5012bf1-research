# scripts

| file | purpose |
|---|---|
| `build.sh` | isolated rebuild: `~/kernel-work/gki-12901745-workspace/lieppos/eeprom/trees/mtkcam` = `git clone --shared` of the mtkcam reconstruction at `133c6c1`. The root `Kbuild` keeps the mtkcam prologue and descends only into `cam_cal/`. O = `lieppos/camera-isp/kout` (vendor config), clang r487747c, `KCFLAGS=-faddrsig`. `build.sh B1` / `build.sh B2` → `par/camera_eeprom_v4l2-B{1,2}.ko` (strip-debug) |
| `elfko.py` | dependency-free ELF64 relocatable reader (sections, symbols, RELA, pointer resolution) |
| `decode_cam_cal.py` | decodes `g_camCalList`, `cam_cal_config_list` and all 37 config records and layout tables from the **stock** `.ko` → `../binary-analysis/` |
| `eeprom_inventory.py` | function inventory (callers/callees/strings/data refs/KCFI/object), data inventory and object map (object bases solved from the rebuild's 43 input objects in `.mod` link order) |

Shared tools used, not copied:
* parity: `reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py`
* strings/sections and module inventory: `reverse-engineering/camera/vcm/scripts/str-sec-parity.py`, `module-inventory.py`
* KCFI oracle: `reverse-engineering/scripts/ko-kcfi-typeid.py`

Whole-file check: `llvm-objcopy --remove-section=.note.gnu.build-id` on stock and B1 → `cmp` equal.
