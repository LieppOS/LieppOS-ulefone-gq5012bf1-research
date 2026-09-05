# mtk_disp_notify — Ulefone GQ5012BF1 reconstruction

Status: discovery / donor validation

## Stock module

Stock module:

`vendor_boot platform ramdisk / lib/modules/mtk_disp_notify.ko`

## Public source candidates

NothingOSS MT6878 contains two implementations:

- `device_modules/drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.c`
- `device_modules/drivers/gpu/drm/mediatek/dummy_drm/mtk_disp_notify.c`

The Nothing MT6878 Kleaf module manifest explicitly builds:

`drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.ko`

Therefore `mediatek_v2` is the primary source donor candidate.

This is a preliminary source-selection result only. Binary/ABI equivalence with
the Ulefone stock module has not yet been established.

## Next verification

1. Compare dummy vs mediatek_v2 source.
2. Inspect stock metadata, imports, exports, strings, symbols and sections.
3. Compare source-visible API against the stock module.
4. Build the mediatek_v2 source unchanged against exact GKI build 12901745.
5. Compare MODVERSION/import contract.
6. Only reconstruct/patch if actual differences are found.

## Stock-vs-source verification

Result: **VERY HIGH CONFIDENCE DIRECT SOURCE MATCH**

The Ulefone stock module matches the NothingOSS `mediatek_v2`
implementation extremely closely.

### Exported API

Stock exports exactly six symbols:

- `mtk_disp_notifier_register`
- `mtk_disp_notifier_unregister`
- `mtk_disp_notifier_call_chain`
- `mtk_disp_sub_notifier_register`
- `mtk_disp_sub_notifier_unregister`
- `mtk_disp_sub_notifier_call_chain`

These are exactly the six functions provided by the NothingOSS
`mediatek_v2/mtk_disp_notify.c`.

The `dummy_drm` implementation only provides the first three and therefore
cannot be the stock source.

### Internal state

Stock contains:

- `disp_notifier_list`, size 72
- `disp_sub_notifier_list`, size 72

at `.data` offsets 0x00 and 0x48 respectively.

This exactly corresponds to the two `BLOCKING_NOTIFIER_HEAD()` declarations
in the `mediatek_v2` source.

### Imports

Stock imports only:

- `_printk`
- `blocking_notifier_chain_register`
- `blocking_notifier_chain_unregister`
- `blocking_notifier_call_chain`

plus `module_layout` in the MODVERSION contract.

This is exactly consistent with the public source.

### Function topology and sizes

Stock:

- `mtk_disp_notifier_register`             0x5c / 92 bytes
- `mtk_disp_notifier_unregister`           0x28 / 40 bytes
- `mtk_disp_notifier_call_chain`           0x2c / 44 bytes
- `mtk_disp_sub_notifier_register`         0x5c / 92 bytes
- `mtk_disp_sub_notifier_unregister`       0x28 / 40 bytes
- `mtk_disp_sub_notifier_call_chain`       0x2c / 44 bytes

The two notifier families have identical compiled topology, exactly as expected
from the source.

### Strong source-line evidence

The stock module logging format is:

`[DISP][%s line:%d]:%s`

In `mtk_disp_notifier_register`, stock loads line number 18 before `_printk`.

The NothingOSS `mediatek_v2` source has the corresponding `DDPFUNC()` call
at source line 18.

In `mtk_disp_sub_notifier_register`, stock loads line number 41 before
`_printk`.

The NothingOSS `mediatek_v2` source has the corresponding `DDPFUNC()` call
at source line 41.

This is particularly strong evidence that the Ulefone module was compiled
from the same or effectively identical source layout.

### Stock import MODVERSION contract

- `blocking_notifier_call_chain`       `0x8317ad7c`
- `_printk`                            `0x92997ed8`
- `blocking_notifier_chain_unregister` `0x963aa2a9`
- `blocking_notifier_chain_register`   `0xbb0c86a5`
- `module_layout`                      `0xea759d7f`

### Current conclusion

Classification:

`DIRECT_SOURCE_MATCH`

Primary donor:

`NothingOSS device_modules/drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.c`

No reconstruction should be attempted unless an exact-GKI rebuild disproves
the source match.

Next step: build this source unchanged against exact Google GKI build 12901745
and compare its import/export MODVERSION contract and generated code against
stock.

## Stock exported symbol CRC contract

Decoded from `__kcrctab_gpl` using the offsets of the corresponding
`__crc_*` symbols:

- `mtk_disp_notifier_call_chain`       `0x4b7239d2`
- `mtk_disp_notifier_register`         `0x4c353ac0`
- `mtk_disp_notifier_unregister`       `0xa11ab00a`
- `mtk_disp_sub_notifier_call_chain`   `0x00b8425f`
- `mtk_disp_sub_notifier_register`     `0x0e7966d3`
- `mtk_disp_sub_notifier_unregister`   `0x17803751`

These six CRCs define the stock inter-module ABI exported by
`mtk_disp_notify.ko`.

## Exact-GKI standalone build note

The first standalone Kleaf build failed before compilation with:

`make: *** No targets. Stop.`

Root cause was the standalone external-module Makefile containing only:

`obj-m += mtk_disp_notify.o`

Kleaf invokes the external module directory directly with `make -C <module>`,
so the standalone package requires an outer Makefile target that recursively
invokes the kernel build system with `$(KERNEL_SRC)` and `M=$(M)`.

The wrapper pattern already proven by the ST21 reconstruction was reused.
No MediaTek donor source files were modified to resolve this build-system issue.

## Final validation

The unchanged NothingOSS `mediatek_v2` source was successfully built against
the exact GQ5012BF1 Google GKI 12901745 workspace.

Build result:

`BUILD_RC=0`

Validation results:

- donor `.c` SHA256 unchanged: exact
- donor `.h` SHA256 unchanged: exact
- donor `mtk_log.h` SHA256 unchanged: exact
- imported MODVERSION contract: exact
- imported kernel symbols: exact
- six exported symbol CRCs: exact
- six exported function sizes: exact
- six exported function addresses/topology: exact
- logging/source-line behavior: exact
- relevant strings: exact
- `.text` disassembly: identical to stock

The disassembly diff contained only the different objdump input pathname.

### Final classification

`mtk_disp_notify`: **DIRECT_SOURCE_MATCH**

Source reconstruction required: **NONE**

Primary source:

`NothingOSS/device_modules/drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.c`

This module is source-solved.

### Vermagic note

The standalone reconstructed build currently reports:

`6.1.115-android14-11-maybe-dirty`

where the Ulefone stock module reports:

`6.1.115-android14-11-g945dff7bc1bf`

This is a kernel build/version-string provenance difference, not a source or
ABI discrepancy. It must be normalized if this standalone artifact is ever
intended for direct loading into the untouched stock kernel. A coherent custom
kernel + module build naturally needs matching kernel/module vermagic.

## Current final status

**Classification:** `DIRECT_SOURCE_MATCH`

The NothingOSS MT6878 `mediatek_v2` implementation was built against exact
GKI 12901745 and validated against the GQ5012BF1 stock module.

Final raw `.text` SHA256:

    4ba2ed5b7d79501595c618870fb8c7e47935e3f9f916bc7222c8f77d31c2a48a

The reconstructed/public-source build is accepted and frozen for LieppOS
custom-kernel integration.
