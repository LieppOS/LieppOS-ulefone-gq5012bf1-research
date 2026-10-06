# Camera VCM — YFT / Ulefone deltas

## Kernel source: DIRECT_SOURCE_MATCH (all six modules)

| module | donor | evidence | delta | confidence |
|---|---|---|---|---|
| `main_vcm.ko` | ALPS `nt6878.git` `5e415e059253`, `main_vcm.c` blob `fb936bd6`, last change `7fe884aeb2a6` (2024-02-27) | rebuild = stock except `.note.gnu.build-id`; B1 == B2 | **DIRECT_SOURCE_MATCH** | proven |
| `main2_vcm.ko` | same tag, blob `f01771cd` | same | **DIRECT_SOURCE_MATCH** | proven |
| `main3_vcm.ko` | same tag, blob `858c29ac` | same | **DIRECT_SOURCE_MATCH** | proven |
| `main4_vcm.ko` | same tag, blob `ad5df12b` | same | **DIRECT_SOURCE_MATCH** | proven |
| `sub_vcm.ko` | same tag, blob `fa261b21` | same | **DIRECT_SOURCE_MATCH** | proven |
| `camera_af_media.ko` | same tag, `mtk-composite.c` blob `4a824a22` | same | **DIRECT_SOURCE_MATCH** | proven |

Lineage: the pre-`7fe884aeb2a6` code places `usleep_range(ctrl_delay_us)` in
`power_on`; stock has it in the ioctl path, so stock ≥ `7fe884aeb2a6`. No later
commit in any ALPS branch touches these files.

## Configuration / packaging

| item | MTK reference | GQ5012BF1 | evidence | confidence |
|---|---|---|---|---|
| lens modules built | `mgk_64_k61.bzl` lists 20 lens modules (ak7375c, ak7377a, bu64253gwz, dw9718, dw9800v, dw9800w, gt9764, gt9772a/b, lc898229, 5 generic, media, dw9781c/d, bu63169, proprietary `*af`) | ships only 5 generic `*_vcm` + `camera_af_media` + `dw9781c` | vendor_dlkm listing, `modules.load` #153–159 | proven |
| actuator driver style | chip drivers (e.g. `dw9800w.ko`) with fixed tables | generic table-driven drivers; the DW9800W protocol lives in the HAL table | `vcm_list_0` | proven |

## Board / DT

| item | GQ5012BF1 | evidence | confidence |
|---|---|---|---|
| lens nodes | `camera-af-main@a` (i2c-7), `camera-af-main-two@b` (i2c-4), `camera-af-main-four@d` (i2c-2); no supplies, no pinctrl | live FDT | proven |
| `main3_vcm`, `sub_vcm` | no DT node | live FDT | proven |
| AF power | `custom_afvdd` 5/6 on the YFT custom-LDO (WL2864C) path, switched by imgsensor | live FDT + stock imgsensor data | proven |

## HAL table (vendor customisation)

| item | GQ5012BF1 | confidence |
|---|---|---|
| sensor→subdev | 0x989/0x988/0x8e1 → `main_vcm`; 0x38e2 → `main4_vcm`; 0x566442 → `main2_vcm` | proven |
| init variant | `07 = 0x79` for the four product sensors; ALPS `dw9800w` default `0x60` kept only for the 0x8e1 alternate | proven (meaning of 0x79: resonance setting, inferred) |
| OIS table | empty (`Dummy` only) | proven |
