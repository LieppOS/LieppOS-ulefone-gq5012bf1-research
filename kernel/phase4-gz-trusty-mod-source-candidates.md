# GQ5012BF1 `gz_trusty_mod` source candidates

## Result

**`EXACT_SOURCE`** at the already-pinned MediaTek/Nothing MT6878 revision:

- repository: `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`
- revision: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- directory: `drivers/misc/mediatek/geniezone/gz-trusty/`
- C objects: `trusty.c`, `smcnr-table.c`
- public headers: `drivers/misc/mediatek/geniezone/public/gz-trusty/`
- Kconfig selector: `CONFIG_MTK_ENABLE_GENIEZONE=m`
- output: `gz_trusty_mod.ko`

The vendor Makefile says:

```make
obj-$(CONFIG_MTK_ENABLE_GENIEZONE) += gz_trusty_mod.o
gz_trusty_mod-objs += trusty.o smcnr-table.o
ifeq ($(CONFIG_MT_GZ_TRUSTY_DEBUGFS),y)
gz_trusty_mod-objs += trusty-debugfs.o
endif
```

Stock proves the debugfs branch off: `trusty-debugfs.o` functions and debugfs imports are absent, while the `Not MT_GZ_TRUSTY_DEBUGFS` string is present.

## Identification proof

The candidate reproduces the complete stock identity without a C-source change:

- 33/33 function bodies byte-identical
- 33/33 KCFI IDs exact
- 59/59 imports exact
- 60/60 MODVERSION entries exact
- 14/14 exports and natural CRCs exact
- 63/63 string inventory rows after reproducing vendor source layout
- both DT compatibles and both platform-driver objects exact

The stock `.rodata.str` source paths identify the same files under `../kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty/`.

No broader donor search was needed after exact closure. File hashes are frozen in `phase4-gz-transport-source-hashes.tsv`.
