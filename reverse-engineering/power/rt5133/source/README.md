# source — exact ALPS files @ nt6878.git 5e415e059253

Every file is verbatim; `SOURCES.tsv` records git blob ids (`git hash-object`
re-verified) and sha256.

| file | role on GQ5012BF1 |
|---|---|
| `drivers/regulator/rt5133-regulator.c` | builds stock `rt5133-regulator.ko` (exact except build-id) |
| `drivers/misc/mediatek/subpmic/extdev_io_class.c`, `include/linux/extdev_io_class.h` | build stock `extdev_io_class.ko` (exact except build-id) |
| `arch/arm64/boot/dts/mediatek/mt6878.dts.rt5133-excerpt` | the DT that ships (68/68 properties equal to the live FDT) |
| `arch/arm64/boot/dts/mediatek/rt5133.dtsi` | generic include, **not** used by the stock image (kept to document the difference: GPOs 1.8 V, EINT 187 / HWEN 188) |

Kconfig: `CONFIG_REGULATOR_RT5133=m` (selects `CRC8`, `REGMAP`, `OF_GPIO`,
`REGULATOR_FIXED_VOLTAGE`, `MTK_SUBPMIC_MISC`), `CONFIG_MTK_SUBPMIC_MISC=m`.
Build: `obj-$(CONFIG_REGULATOR_RT5133) += rt5133-regulator.o`,
`obj-$(CONFIG_MTK_SUBPMIC_MISC) += extdev_io_class.o`.
