# Stock boot image geometry

Produced by `unpack_bootimg --format=mkbootimg` against the stock
`GQ5012BF1_EEA_V15` images. These arguments are the provenance of the boot
header values in the device tree's `BoardConfig.mk` — in particular the four
offsets that `build/make` does not emit from board variables and that must be
passed through `BOARD_MKBOOTIMG_ARGS` explicitly:

```text
--header_version 4
--pagesize        0x00001000
--base            0x00000000
--kernel_offset   0x40000000
--ramdisk_offset  0x66f00000
--tags_offset     0x47c80000
--dtb_offset      0x47c80000
--vendor_cmdline  bootopt=64S3,32N2,64N2
```

`vendor_boot` carries two ramdisk fragments, which is the layout every rescue
and OrangeFox image had to preserve:

```text
--ramdisk_type 1 --ramdisk_name ''         -> vendor_ramdisk00  (PLATFORM)
--ramdisk_type 2 --ramdisk_name recovery   -> vendor_ramdisk01  (RECOVERY)
```

The unpacked payloads themselves are not kept: they are reproducible from the
stock firmware in `../../workspace/gq5012bf1/stock/firmware/`.
