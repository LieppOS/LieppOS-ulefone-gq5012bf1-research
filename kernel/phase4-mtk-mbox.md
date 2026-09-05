# mtk-mbox — Ulefone GQ5012BF1

Status: donor/source validation

## Stock modules discovered

The Ulefone image contains a MediaTek mailbox stack consisting of distinct
modules:

- `mtk-mbox.ko`
- `mtk-mbox-mailbox.ko`
- `mtk_rpmsg_mbox.ko`

`mtk-mbox.ko` appears in both vendor_dlkm and the vendor_boot platform ramdisk.

## Public NothingOSS MT6878 source mapping

Core mailbox library:

`device_modules/drivers/soc/mediatek/mtk-mbox.c`

Public API header:

`device_modules/include/linux/soc/mediatek/mtk-mbox.h`

Linux mailbox-controller layer:

`device_modules/drivers/mailbox/mtk-mbox-mailbox.c`

RPMSG mailbox layer:

`device_modules/drivers/rpmsg/mtk_rpmsg_mbox.c`

These are separate modules and must not have their ABI/symbol contracts mixed
during comparison.

## Order

Validate `mtk-mbox.ko` first because it provides the common MediaTek mailbox
API used by higher layers.

Then validate:

1. `mtk_rpmsg_mbox.ko`
2. `mtk-mbox-mailbox.ko`
3. `mtk_tinysys_ipi.ko`

No reverse engineering is justified until the public `mtk-mbox.c` donor has
been compared against the stock binary.

## Initial stock-vs-public-source evidence

The vendor_dlkm and vendor_boot copies of `mtk-mbox.ko` are byte-identical:

`SHA256 95e3aa8d68b69504ae273bbd1979ea6d8b9c958b57a97b423cc696218ebfbe7c`

Therefore one stock binary is sufficient as the oracle.

The stock module exports the same major API present in the NothingOSS
`drivers/soc/mediatek/mtk-mbox.c` donor, including:

- mtk_mbox_write_hd
- mtk_mbox_read_hd
- mtk_mbox_write
- mtk_mbox_read
- mtk_mbox_clr_irq
- mtk_mbox_trigger_irq
- mtk_mbox_check_send_irq
- mtk_mbox_read_recv_irq
- mtk_mbox_set_base_reg
- mtk_mbox_set_base_addr
- mtk_mbox_cb_register
- mtk_mbox_polling
- mtk_smem_init
- mtk_mbox_probe
- mtk_mbox_clr_index_record
- mtk_mbox_get_index_record
- mtk_mbox_print_recv
- mtk_mbox_print_send
- mtk_mbox_print_minfo
- mtk_mbox_dump_all
- mtk_mbox_dump_recv
- mtk_mbox_dump_recv_pin
- mtk_mbox_dump_send
- mtk_mbox_dump
- mtk_mbox_log_enable
- mtk_mbox_reset_record

The stock module also embeds the source path:

`../kernel_device_modules-6.1/drivers/soc/mediatek/mtk-mbox.c`

and contains the expected MediaTek mailbox tracepoints:

- mtk_mbox_isr_entry
- mtk_mbox_isr_exit
- mtk_mbox_polling

Current classification:

`LIKELY_DIRECT_SOURCE_MATCH`

Do not reverse-engineer unless an unchanged donor build against exact GKI
12901745 demonstrates a substantive source difference.

## Standalone Kleaf include-path finding

The first unchanged-source standalone build reached compilation but failed to
resolve:

`<linux/soc/mediatek/mtk-mbox.h>`

Kbuild diagnostics showed:

- `src=../lieppos/mtk-mbox-direct`
- `obj=../lieppos/mtk-mbox-direct`
- `M=../lieppos/mtk-mbox-direct`
- `CURDIR=.../out/android14-6.1/common`

Therefore:

`ccflags-y += -I$(src)/include`

was being resolved relative to the kernel output-tree working directory rather
than the Bazel execroot external-module source directory.

The standalone wrapper was changed to:

`ccflags-y += -I$(KERNEL_SRC)/$(M)/include`

which resolves the include directory from the actual kernel source root plus
the external-module path.

This is standalone Kleaf build plumbing only. No NothingOSS donor source or
header content was modified.

## Final exact-GKI validation

The unchanged NothingOSS MT6878 `drivers/soc/mediatek/mtk-mbox.c`
source was successfully built against exact Google GKI build 12901745.

Results:

- build: success
- donor source SHA256: unchanged
- public `mtk-mbox.h`: unchanged
- public trace/events/mbox.h: unchanged
- imported kernel symbols: exact
- imported MODVERSION contract: exact
- exported CRC table: exact
- exported global MediaTek function sizes: exact
- raw `.text` SHA256: exact
- raw `.text` comparison: `TEXT_CMP_RC=0`

Stock and reconstructed `.text` are byte-identical.

### Final classification

`mtk-mbox.ko`: **DIRECT_SOURCE_MATCH**

Primary donor:

`NothingOSS/device_modules/drivers/soc/mediatek/mtk-mbox.c`

Source reconstruction required: **NONE**

The only standalone-build adaptations were Kleaf/Kbuild wrapper and include-path
plumbing. MediaTek source and public headers were not modified.

The stock vendor_dlkm and vendor_boot copies are also byte-identical, so one
oracle is sufficient.

## Current final status

**Classification:** `DIRECT_SOURCE_MATCH`

The NothingOSS MT6878 source was built against exact GKI 12901745 and matches
the GQ5012BF1 stock module at the required implementation boundary.

Final raw `.text` SHA256:

    3bacf0f5b6efb58059f2b75c17f9b7a45602ec07c04eb387de720e06bb156fb9

This module is frozen for initial LieppOS custom-kernel integration.
