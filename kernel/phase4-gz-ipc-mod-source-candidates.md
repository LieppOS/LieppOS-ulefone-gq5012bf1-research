# GQ5012BF1 `gz_ipc_mod` source candidates

## Result

**`EXACT_SOURCE`** at the already-pinned MediaTek/Nothing MT6878 revision:

- repository: `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`
- revision: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- directory: `drivers/misc/mediatek/geniezone/gz-trusty/`
- C object: `trusty-ipc.c`
- public header: `drivers/misc/mediatek/geniezone/public/gz-trusty/trusty_ipc.h`
- Kconfig selector: `CONFIG_MTK_GZ_VIRTIO_IPC=m`
- output: `gz_ipc_mod.ko`

The vendor Makefile says:

```make
obj-$(CONFIG_MTK_GZ_VIRTIO_IPC) += gz_ipc_mod.o
gz_ipc_mod-objs += trusty-ipc.o
```

## Identification proof

The candidate, built above the real source-built `gz_trusty_mod`, reproduces stock without a C-source change:

- 43/43 function bodies byte-identical
- 43/43 KCFI IDs exact
- 81/81 imports exact, including three natural `gz_trusty_mod` edges
- 82/82 MODVERSION entries exact
- 15/15 exports and natural CRCs exact
- 88/88 string inventory rows after reproducing vendor source/header layout
- file-operations, virtio-driver, channel, and device objects exact

Stock `.rodata.str` records both exact source/header paths. No alternative revision or clean-room reconstruction is justified. File hashes are frozen in `phase4-gz-transport-source-hashes.tsv`.
