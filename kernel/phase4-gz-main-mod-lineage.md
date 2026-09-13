# gz_main_mod — exact source lineage

## 1. Upstream revision

| item | value |
|---|---|
| repository | `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` |
| revision | `957dac185efe46cbf6336b0fff9516d84c8cd78f` |
| subtree | `drivers/misc/mediatek/geniezone/` |
| donor state | clean; identical revision that closed `ffa_v10`, `tmem_ffa`, `gz_tz_system`, `gz_trusty_mod`, `gz_ipc_mod` |

## 2. Build location (vendor layout, for `__FILE__` parity)

```
/home/armol/kernel-work/gki-12901745-workspace/
  kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/
      gz_main.c  gz_main.h  gz_ffa.c  gz_ffa.h
      include/unittest.h
      mtee_ut/{gz_ut,gz_chmem_ut,gz_shmem_ut,gz_vreg_ut}.{c,h}
      public/            <- gz-trusty, kree, tz_cross headers (pre-existing)
      Makefile           <- LieppOS build plumbing (new, no driver code)
      Makefile.vendor    <- upstream vendor Makefile, verbatim
      Kconfig            <- upstream, verbatim
      BUILD.bazel        <- LieppOS build plumbing (new)
      stock-provider.symvers / .provenance.json  <- mtk_sec_heap record
```

External vendor headers reached through the vendor `-I` list, byte-identical
from the same revision:

```
kernel_device_modules-6.1/drivers/dma-buf/heaps/mtk_heap.h
kernel_device_modules-6.1/drivers/misc/mediatek/trusted_mem/public/mtee_regions.h
kernel_device_modules-6.1/drivers/misc/mediatek/trusted_mem/ssmr/memory_ssmr.h
kernel_device_modules-6.1/drivers/misc/mediatek/trusted_mem/private/*.h
```

`trusted_mem/private/*.h` is required only because the vendor
`ssmr/memory_ssmr.h` itself does `#include "../private/tmem_device.h"`.

Per-file SHA256 values are recorded in
`kernel/phase4-gz-main-mod-source-hashes.tsv`. Every source file is
byte-identical to the pinned donor; the LieppOS-authored files are limited to
`Makefile`, `BUILD.bazel` and the declared stock-provider record.

## 3. Build target

```
//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone:gz_main_mod
kernel_build = //common:kernel_aarch64        (exact GKI ab/12901745)
```

Dependencies, all REAL source-built modules:

```
//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport
//lieppos/gz-tz-system-accept:gz_tz_system_accept
//lieppos/ffa-v10:ffa_v10
//lieppos/tmem-ffa-gzaccept:tmem_ffa_gzaccept
```

`gz-tz-system-accept` is deliberately chosen over `gz-tz-system`: it is the
witness-free acceptance build of the KREE provider, so no gz_tz_system,
gz_ipc_mod or gz_trusty_mod witness record participates in this build.

## 4. Object list

Reproduced unchanged from `Makefile.vendor`:

```make
gz_main_mod-y += gz_main.o
gz_main_mod-y += mtee_ut/gz_ut.o
gz_main_mod-y += mtee_ut/gz_chmem_ut.o
gz_main_mod-y += mtee_ut/gz_shmem_ut.o
gz_main_mod-y += mtee_ut/gz_vreg_ut.o
gz_main_mod-y += gz_ffa.o
```

## 5. Lineage verdict

`EXACT_SOURCE` at the pinned revision, built in the vendor directory layout,
against exact GKI and a fully source-built GenieZone provider stack. The only
non-source input in the entire build is the single declared `mtk_sec_heap`
provider ABI record.
