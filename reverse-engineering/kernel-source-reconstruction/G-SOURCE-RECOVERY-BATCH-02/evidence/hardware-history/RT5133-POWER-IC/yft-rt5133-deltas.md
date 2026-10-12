# RT5133 — YFT / Ulefone deltas

## Kernel source: DIRECT_SOURCE_MATCH

| artifact | donor | GQ5012BF1 | evidence | delta | confidence |
|---|---|---|---|---|---|
| `rt5133-regulator.ko` | ALPS `nt6878.git` `drivers/regulator/rt5133-regulator.c` @ `5e415e059253` (blob `047d4b2a20e4`, = latest ALPS commit `a1afca9b8e00` "rt5133 add io debug log and module param") | stock sha256 `467dcf89…07bc03` | rebuild equal to stock in every byte except `.note.gnu.build-id` (20 bytes); 13/13 functions, 34/34 data, 39/39 import CRCs in order, srcversion `3A1F23BBC7D40274DE38CDD` reproduced | **DIRECT_SOURCE_MATCH** | proven |
| `extdev_io_class.ko` | ALPS `drivers/misc/mediatek/subpmic/extdev_io_class.c` + `include/linux/extdev_io_class.h` @ `5e415e059253` | stock sha256 `60f520e3…fce3d2b4` | rebuild equal to stock except build-id; 10/10 functions, 19/19 data, 39/39 imports, 4/4 export CRCs | **DIRECT_SOURCE_MATCH** | proven |
| Kconfig | `CONFIG_REGULATOR_RT5133=m`, `CONFIG_MTK_SUBPMIC_MISC=m` | same (modules present, srcversion match) | | none | proven |

## Device tree

| item | MTK reference | GQ5012BF1 | evidence | delta | confidence |
|---|---|---|---|---|---|
| `rt5133@18` node | inline in base `mt6878.dts` | in base DTB, 68/68 properties equal | `hardware/dt-source-vs-live.tsv` | none (inherited, not edited by Ulefone) | proven |
| GPIO1 | RT5133 HWEN (`enable-gpio`) | **also** WL2864C `reset-gpios` in board DTBO | live FDT | **board delta**: GPIO1 reassigned to the substitute camera LDO; RT5133 node left in place | proven |
| camera rails | reference `cust_mt6878_camera_v4l2.dtsi` → RT5133 LDO1/2/3/6/7, GPO2/3 | board camera nodes → WL2864C (`11-0029`) and `/odm/camera-common-*` | live FDT supply scan | **board delta**: RT5133 replaced as camera LDO PMIC by WL2864C/WL2868C | proven |

## Runtime

| item | reference board | GQ5012BF1 | evidence |
|---|---|---|---|
| binding | bound, 9 regulators + 3 GPOs | probe fails at `CHIP_INFO`; 0 regulators; GPO fixed regulators stuck in deferred probe | `buses.txt`; pstore console |

No Ulefone/YFT code touches RT5133. The only GQ5012BF1-specific change is the
*absence* of the part (or of its supply) plus the GPIO1 reuse.
