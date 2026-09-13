# ffa_v10 source search

**Result: `EXACT_SOURCE`.** The shipped module is built from source that is
present, verbatim, in the pinned Nothing MT6878 vendor tree.

## Winning candidate

| | |
|---|---|
| path | `nothing-mt6878/device_modules/drivers/misc/mediatek/trusted_mem/ffa_v10/` |
| pinned revision | `device_modules` `957dac185efe46cbf6336b0fff9516d84c8cd78f` |
| files | `bus.c`, `driver.c`, `smccc.c`, `common.h`, `Kconfig` |
| classification | **`EXACT_SOURCE`** |
| proof | the four compiled sources build **34/34 byte-identical functions** and **5/5 natural export CRCs** against exact GKI 12901745 |

```
3cda7cc57a774e1b0c138acd8a5fc8fb12e4255fd81b0e96675a290be40bf8a6  bus.c
6b14f18ee44e4966810d55b00eaa3d32163da1c82b8290e78cd30f3fb66306c5  driver.c
3701a267eaad251847e25fefa80ba1a6495e57c3af3bc095ac73e50288cd49a3  smccc.c
84883f2fefa4d64c51f5491e37388ac29e75925e138acc1a3fac51d3baf196f5  common.h
c47ebe5ba1b43a6e1225c59ea48812a5a0821f2b2e2b87afc04fb8f913e8c78c  Kconfig
```

The vendor build rule, also recovered verbatim, is in the parent
`trusted_mem/Makefile`:

```make
ifeq ($(CONFIG_ARM_FFA_TRANSPORT),...)
obj-m += ffa_v10.o
ffa_v10-y += ffa_v10/bus.o
ffa_v10-y += ffa_v10/driver.o
ffa_v10-y += ffa_v10/smccc.o
endif # CONFIG_ARM_FFA_TRANSPORT
```

and the module is listed for packaging in
`device_modules/kernel/kleaf/mgk_64_k61.bzl:467` as
`"drivers/misc/mediatek/trusted_mem/ffa_v10.ko"`.

## How it was found

The search was run identifier-first, which is what located it: the module's
own strings (`ARM FF-A: Driver version %d.%d`, `MODALIAS=arm_ffa:%04x:%pUb`,
`arm-ffa-%d`), its `MODULE_AUTHOR("Sudeep Holla")`, and its 34 function names
are verbatim upstream `drivers/firmware/arm_ffa/`. A tree-wide
`grep -rl ffa_driver_register` then produced four hits, two of them providers:

| hit | role |
|---|---|
| `kernel/drivers/firmware/arm_ffa/bus.c` | the in-tree GKI copy (not the shipped module) |
| `device_modules/.../trusted_mem/ffa_v10/bus.c` | **the shipped module's source** |
| `device_modules/.../geniezone/gz_main.c` | consumer (`gz_main_mod.ko`) |
| `kernel/include/linux/arm_ffa.h` | the shared header |

MediaTek did not modify the driver's logic at all; they copied a snapshot of
the in-tree driver into their device-modules tree so it could ship as a vendor
module, added a `Copyright (c) 2023 MediaTek Inc.` line to each file, and
reflowed one line in `driver.c`. That is the entire vendor delta.

## Other candidates evaluated

| candidate | classification | why |
|---|---|---|
| GKI `common/drivers/firmware/arm_ffa/` @ 6b18f0b574ab (6.1.115) | **`SOURCE_DELTA_REQUIRED`** | same driver, three stable commits newer than the vendor snapshot; builds 30/34 byte-identical. Kept as the RED baseline - see `phase4-ffa-v10-RED.md` |
| upstream mainline `arm_ffa` (v6.5+) | `STRUCTURAL_DONOR_ONLY` | FF-A v1.1 notifier/rework series makes it structurally different |
| MicroTrust/TEEI, other MTK FF-A shims | `NO_USEFUL_SOURCE` | unrelated code bases |

`CONFIG_ARM_FFA_TRANSPORT` is **not** set in GKI's `gki_defconfig`, which is
why this driver ships as a vendor module in the `vendor_boot` platform ramdisk
rather than as part of GKI/`system_dlkm`.
