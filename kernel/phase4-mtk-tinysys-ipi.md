# mtk_tinysys_ipi — Ulefone GQ5012BF1

Status: source/donor discovery

## Dependency position

`mtk_tinysys_ipi` sits above the MediaTek mailbox layer.

The lower `mtk-mbox.ko` dependency has already been proven to be a
`DIRECT_SOURCE_MATCH` against NothingOSS MT6878 source, including exact raw
`.text` equality against stock.

## Current objective

Identify the corresponding NothingOSS/MediaTek public source for
`mtk_tinysys_ipi.ko`, then compare:

- exported API
- imported kernel symbols
- imported inter-module symbols
- MODVERSION CRCs
- function topology and sizes
- strings / logging
- source-path provenance

No reverse engineering should be attempted unless public-source comparison or
an exact-GKI unchanged-source rebuild demonstrates substantive missing behavior.

## Initial source provenance result

Stock SHA256:

`a64d819e0fde04f5c508c603d805838381550ca8012b899c5b91f8b4d7479834`

The vendor_dlkm and vendor_boot copies are byte-identical.

The stock binary embeds:

`../kernel_device_modules-6.1/drivers/soc/mediatek/mtk_tinysys_ipi.c`

NothingOSS provides the corresponding source:

`device_modules/drivers/soc/mediatek/mtk_tinysys_ipi.c`

and public API header:

`device_modules/include/linux/soc/mediatek/mtk_tinysys_ipi.h`

Stock exposes the same major API visible in the donor source:

- ipi_monitor_dump
- mtk_ipi_device_register
- mtk_ipi_device_reset
- mtk_ipi_register
- mtk_ipi_unregister
- mtk_ipi_send
- mtk_ipi_recv
- mtk_ipi_send_compl
- mtk_ipi_recv_reply
- mtk_ipi_tracking

The stock module has exactly five MediaTek inter-module dependencies:

From `mtk-mbox`:
- mtk_mbox_dump_recv_pin
- mtk_mbox_polling
- mtk_mbox_reset_record

From `mtk_rpmsg_mbox`:
- mtk_rpmsg_create_channel
- mtk_rpmsg_create_device

`mtk-mbox` has already been proven as an exact DIRECT_SOURCE_MATCH.

Current classification:

`LIKELY_DIRECT_SOURCE_MATCH`

The remaining prerequisite for a clean exact-GKI build is validation/building
of `mtk_rpmsg_mbox`.

## Public donor hashes

`mtk_tinysys_ipi.c`:

`6e2dafc6e7759fefeca1f9f91ca5304685bef8c0047003c30e0fd0a3646a0e36`

`mtk_tinysys_ipi.h`:

`7d361b562a88fb40037ee3b53a59b561f692f8b2363e2ff44b1f5e0e5cf45a8c`

The donor has the same ten non-GPL exports observed in stock.

Stock exported CRC contract:

- `ipi_monitor_dump`           `0xe9c9605c`
- `mtk_ipi_device_register`    `0xbdb7a098`
- `mtk_ipi_device_reset`       `0x4985e2ee`
- `mtk_ipi_recv`               `0x5c657a99`
- `mtk_ipi_recv_reply`         `0x35a6e1e2`
- `mtk_ipi_register`           `0x825ce65b`
- `mtk_ipi_send`               `0x19bb8852`
- `mtk_ipi_send_compl`         `0x705006af`
- `mtk_ipi_tracking`           `0x3b965be5`
- `mtk_ipi_unregister`         `0xa55a0ebf`

## Final exact-GKI validation

The unchanged NothingOSS:

`device_modules/drivers/soc/mediatek/mtk_tinysys_ipi.c`

was successfully built against exact Google GKI build 12901745 together with
its two proven MediaTek dependencies:

- `mtk-mbox`
- `mtk_rpmsg_mbox`

Validation results:

- build: success
- NothingOSS `mtk_tinysys_ipi.c`: unchanged
- NothingOSS `mtk_tinysys_ipi.h`: unchanged
- `mtk-mbox` dependency control `.text`: exact
  (`MBOX_CONTROL_RC=0`)
- `mtk_rpmsg_mbox` dependency control `.text`: exact
  (`RPMSG_CONTROL_RC=0`)
- imported kernel/inter-module symbols: exact
- imported MODVERSION contract: exact
- ten non-GPL exported symbol CRCs: exact
- function sizes: exact
- raw `.text`: exact
- `IPI_TEXT_CMP_RC=0`

Stock and rebuilt `mtk_tinysys_ipi.ko` contain byte-identical `.text`.

### Final classification

`mtk_tinysys_ipi.ko`: **DIRECT_SOURCE_MATCH**

Primary donor:

`NothingOSS/device_modules/drivers/soc/mediatek/mtk_tinysys_ipi.c`

Source reconstruction required: **NONE**

### Dependency chain proven

The following MediaTek TinySys communication stack is now source-solved:

1. `mtk-mbox.ko`
2. `mtk_rpmsg_mbox.ko`
3. `mtk_tinysys_ipi.ko`

All three reproduce the stock GQ5012BF1 `.text` exactly when built against
exact GKI 12901745 with the correct MediaTek vendor header environment.

This strongly supports using NothingOSS MT6878 as a source donor for Ulefone's
MediaTek vendor-kernel stack rather than reverse-engineering these binaries.

## Current final status

**Classification:** `DIRECT_SOURCE_MATCH`

The MT6878 public source was built and validated against exact GKI 12901745.

Final raw `.text` SHA256:

    3fe76416ed4b67907b584483849e610ab8e294cb8d90ed9a439b7666949da882

This module is frozen for initial LieppOS custom-kernel integration.
