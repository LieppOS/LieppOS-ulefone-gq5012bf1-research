# mtk_rpmsg_mbox — Ulefone GQ5012BF1

Status: source/donor validation

## Dependency role

`mtk_rpmsg_mbox` provides RPMSG mailbox glue used directly by
`mtk_tinysys_ipi`.

The stock `mtk_tinysys_ipi.ko` imports:

- mtk_rpmsg_create_channel
- mtk_rpmsg_create_device

from this module.

NothingOSS provides:

`device_modules/drivers/rpmsg/mtk_rpmsg_mbox.c`

## Objective

Compare stock and public source before attempting any reconstruction.

If the public source contract matches, build it unchanged against exact Google
GKI build 12901745, using the already-solved `mtk-mbox` module as its MediaTek
mailbox dependency where required.

## Initial stock-vs-public-source evidence

Stock SHA256:

`cc2c852907b94c27da4d4478e315fd823fc7fab6849b71a76893e7087a513814`

The vendor_dlkm and vendor_boot copies are byte-identical.

NothingOSS donor:

`device_modules/drivers/rpmsg/mtk_rpmsg_mbox.c`

Donor SHA256:

`557089af2c471cef8a61e417a7106ab87e177cf6359bb1f384c1a2b3cbc288a0`

The stock binary embeds:

`../kernel_device_modules-6.1/drivers/rpmsg/mtk_rpmsg_mbox.c`

Stock and donor expose the same three GPL exports:

- mtk_mbox_send
- mtk_rpmsg_create_channel
- mtk_rpmsg_create_device

Stock imports exactly three MediaTek mailbox functions:

- mtk_mbox_check_send_irq
- mtk_mbox_trigger_irq
- mtk_mbox_write

All three are provided by the already source-solved `mtk-mbox`.

Stock export CRC contract:

- `mtk_mbox_send`              `0x84d5423c`
- `mtk_rpmsg_create_channel`   `0xb1fef50a`
- `mtk_rpmsg_create_device`    `0x639753b0`

The latter two exactly match the MODVERSION CRCs imported by the stock
`mtk_tinysys_ipi.ko`.

Current classification:

`LIKELY_DIRECT_SOURCE_MATCH`

Next step is an unchanged-source exact-GKI build.

## First exact-GKI build blocker

An unchanged-source combined `mtk-mbox + mtk_rpmsg_mbox` build reached
compilation of `mtk_rpmsg_mbox.c`.

The build failed because the RPMSG header environment did not provide complete
definitions for:

- `struct mtk_rpmsg_endpoint`
- `struct mtk_rpmsg_channel_info`
- `struct mtk_rpmsg_operations`

This caused cascading incomplete-type errors throughout
`mtk_rpmsg_mbox.c`.

The MediaTek source itself has not been modified.

Current interpretation:

This is a header/configuration/build-environment problem until proven
otherwise, not evidence that the public donor source differs from Ulefone
stock.

Next step: identify the exact NothingOSS header/config source of those RPMSG
type definitions before changing any source code.

## Exact-GKI header namespace collision

NothingOSS's public:

`device_modules/include/linux/rpmsg/mtk_rpmsg.h`

contains the concrete MediaTek mailbox-RPMSG types required by
`mtk_rpmsg_mbox.c`, including:

- `struct mtk_rpmsg_channel_info`
- `struct mtk_rpmsg_endpoint`
- `struct mtk_rpmsg_operations`
- `struct mtk_rpmsg_device`

There are no CONFIG conditionals hiding these definitions.

The exact Google GKI 12901745 tree independently contains:

`common/include/linux/rpmsg/mtk_rpmsg.h`

The original standalone external-module include path was supplied via
`ccflags-y`. Kernel include paths take precedence over that external include,
so compilation resolved the GKI header instead of the NothingOSS vendor header.

This explains the incomplete MediaTek RPMSG structure errors without requiring
any modification to `mtk_rpmsg_mbox.c`.

The standalone build is being adjusted so the NothingOSS vendor include tree
precedes the kernel include namespace. This is build/header-environment
plumbing, not source reconstruction.

## Final exact-GKI validation

The unchanged NothingOSS `drivers/rpmsg/mtk_rpmsg_mbox.c` source was built
against exact Google GKI build 12901745.

The build also included the already-proven `mtk-mbox.c` as a dependency.

Validation:

- build: success
- NothingOSS `mtk_rpmsg_mbox.c`: unchanged
- NothingOSS `mtk_rpmsg.h`: unchanged
- exact-GKI `rpmsg_internal.h`: unchanged build dependency
- `mtk-mbox` control `.text`: exact (`MBOX_CONTROL_TEXT_RC=0`)
- imported symbol MODVERSION contract: exact
- GPL export CRC table: exact
- function sizes: exact
- raw `.text`: exact
- `RPMSG_TEXT_CMP_RC=0`

Stock and rebuilt `mtk_rpmsg_mbox.ko` contain byte-identical `.text`.

### Final classification

`mtk_rpmsg_mbox.ko`: **DIRECT_SOURCE_MATCH**

Primary donor:

`NothingOSS/device_modules/drivers/rpmsg/mtk_rpmsg_mbox.c`

Source reconstruction required: **NONE**

### Build environment note

Google GKI and NothingOSS both provide:

`include/linux/rpmsg/mtk_rpmsg.h`

but the Google GKI version only contains the older/common RPMSG declarations,
while the NothingOSS vendor version extends that header with the TinySys
mailbox-RPMSG structures required by `mtk_rpmsg_mbox.c`.

Because both headers use the same include guard, the vendor include tree must
precede the kernel include tree for this external-module build.

Using `NOSTDINC_FLAGS` to prioritize the unchanged NothingOSS vendor header
resolved the issue. This was build/header plumbing only.

## Current final status

**Classification:** `DIRECT_SOURCE_MATCH`

The NothingOSS MT6878 source was built against exact GKI 12901745 and matches
the GQ5012BF1 stock RPMSG mailbox implementation at the required boundary.

Final raw `.text` SHA256:

    b1341db5d61c8ddbdccbc899dab05f27fa40c26d6780255f8a7a8752bda80b73

This module is frozen for initial LieppOS custom-kernel integration.
