# Backlight + display glue (GQ5012BF1) — static closure, 2026-10-04

A = shipped stock `.ko`. B = isolated `M=` rebuild against GKI
`6.1.115-android14-11-g945dff7bc1bf` (ab12901745), clang r487747c,
`CONFIG_LTO_NONE`, `KCFLAGS=-faddrsig`, `__FILE__` prefix-mapped to
`../kernel_device_modules-6.1/`, `llvm-strip --strip-debug`. Provider CRCs come
from the stock `__kcrctab` (`scripts/glue.py`). Comparator:
`../rear-display-input/scripts/ko-parity-tsv.py` + section byte compare.

| module | functions | data | imports | exports | modinfo | sections | B1==B2 | source |
|---|---|---|---|---|---|---|---|---|
| `mtk-pwm` | **87/87** | 30/30 | 27/27 | 5/5 | 6/6 | 44/45 (build-id) | yes | KDM baseline, no delta |
| `pwm-mtk-disp` | **10/10** | 44/44 | 21/21 | 0 | 30/30 | 39/40 | yes | MTK e46af0f + 3 GQ5012BF1 hunks |
| `leds-mtk` | **25/25** | 27/27 | 33/33 | 10/10 | 6/6 | 48/49 | yes | MTK 164442952094, no delta |
| `leds-mtk-disp` | **9/9** | 23/23 | 19/19 | 0 | 14/14 | 37/38 | yes | unchanged |
| `backlight_cooling` | **8/8** | 18/18 | 12/12 | 0 | 8/8 | 39/40 | yes | unchanged |
| `rt4831a_drv` | **14/14** | 19/19 | 16/16 | 7/7 | 6/6 | 41/42 | yes | unchanged |
| `mediatek-drm-gateic` | **39/39** | 47/47 | 29/29 | 12/12 | 19/19 | 45/46 | yes | unchanged |
| `mtk_disp_sec` | **11/11** | 19/19 | 21/21 | 0 | 6/6 | 38/39 | yes | unchanged |
| `met_backlight_api` | **2/2** | 12/12 | 8/8 | 0 | 6/6 | 31/32 | — | nkm met_drv_v3, unchanged |
| `mtk_irtx_pwm` | **6/6** | 16/16 | 23/23 | 0 | 6/6 | 37/38 | yes | KDM + `dma-mask-bit` delta |
| `regulator-vibrator` | **9/9** | 15/15 | 18/18 | 0 | 6/6 | 37/38 | yes | MTK 4d63add + line layout |
| `aw36518` | 22/23 (+1 sched) | 32/32 | 47/47 | 0 | 9/9 | `.text`,`.data` order | yes | Phase-4 recon + 5 fixes |
| `aw36518_v2` | 22/23 (+1 sched) | 32/32 | 46/46 | 0 | 9/9 | same | yes | same |
| `mediatek-drm-panel-drv` (unused) | **123/123** | 43/43 | 71/71 | 53/53 | 30/30 | 42/43 (build-id) | yes | KDM baseline + ALPS `5e415e059253` `mtk_panel_ext.h` (see `../mediatek-drm/`) |

KCFI type ids are equal for every function in every row. Modversion CRCs are
equal for every import and export. Sections are compared after debug-stripping.
`.note.gnu.build-id` hashes the pre-strip DWARF and is the only differing
section for the eleven exact rows.

## AW36518 residual (both variants)

1. `aw36518*_probe`: `sub x24, x25, #0x20` (= `to_i2c_client(flash->dev)`)
   is scheduled 5 instructions later. The instruction multiset, size and
   relocations are equal.
2. `.data` holds `dev_attr_reg`, `cooling_ops` and `flash_ops` in a different
   order. The objects are byte-identical, so only relocation addends follow.
   Moving, forward-declaring or `DEVICE_ATTR_RW`-ing the attribute does not
   change Clang's emission order. The source trigger is not identified.

## Files

| file | content |
|---|---|
| `module-inventory.tsv` | per-module role, DT binding, ACTIVE/UNUSED/PLATFORM/STALE class, parity |
| `source-map.tsv` | stock source path, donor repo/commit, delta, location |
| `brightness-path.md` | main panel brightness: framework -> DCS 0x51 |
| `rear-brightness-path.md` | CO5300 brightness; backlight GPIO absent in DT |
| `../yft-display-glue-deltas.md` | all GQ5012BF1 deltas with evidence |
| `haptics.md`, `flash-aw36518.md`, `irtx.md` | lighting/haptics/IR closures |
| `parity/<module>/` | function/data/ABI/relocation TSVs + SUMMARY |
| `source/kdm-patches/` | KDM commits 5326ad7, 3b99537, ef13d89 |
| `source/aw36518*/` | exact AW36518/V2 sources + diffs vs Phase-4 recon |
| `scripts/glue.py` | isolated-build + parity harness (`fd.sh`, `secdiff.py`) |

Safety: offline only. No brightness, PWM, GPIO, vibrator, flash or IR action
was performed.
