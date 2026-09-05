# mtk-mbox-mailbox — Ulefone GQ5012BF1

Status: source/donor discovery

## Role

This is the MediaTek Linux mailbox-controller layer and is distinct from the
already source-solved `mtk-mbox.ko` TinySys mailbox core library.

NothingOSS source candidate:

`device_modules/drivers/mailbox/mtk-mbox-mailbox.c`

## Objective

Compare stock against the public MT6878 source and perform an unchanged-source
exact-GKI build before considering any reconstruction.

## Initial stock-vs-public-source evidence

Stock SHA256:

`b36bb207c82813060afbae809b6505bb96bdb1a77e4b17677a4b8b84b71b1f09`

NothingOSS donor:

`device_modules/drivers/mailbox/mtk-mbox-mailbox.c`

Donor SHA256:

`77d81c8a9e33c2d795c7d4700e00bbec0bb7c2f61e58a02eda41fb149ab3106a`

Stock has no inter-module module dependencies.

The stock function topology contains:

- tinysys_mbox_probe
- tinysys_mbox_remove
- tinysys_mbox_send_data
- tinysys_mbox_startup
- tinysys_mbox_shutdown
- tinysys_mbox_last_tx_done
- tinysys_mbox_rx_interrupt

Stock strings identify:

- `mediatek,tinysys_mbox`
- `mtk_tinysys_mbox`
- `MTK MBOX Mailbox registered`
- `secure-sspm-mbox-clr`
- secure mailbox-clear SMC support
- IRQ acquisition/registration paths

The imported kernel APIs are consistent with the NothingOSS donor's mailbox,
DT, MMIO, IRQ and ARM-SMCCC implementation.

Current classification:

`LIKELY_DIRECT_SOURCE_MATCH`

No reverse engineering is justified unless an unchanged-source exact-GKI build
shows substantive differences.

## First exact-GKI build blocker: MediaTek SIP header

The unchanged NothingOSS `mtk-mbox-mailbox.c` reached compilation against
exact GKI 12901745 but failed on:

`MTK_SIP_TINYSYS_SSPM_CONTROL`

NothingOSS and Google GKI both provide:

`include/linux/soc/mediatek/mtk_sip_svc.h`

but the two headers are not byte-identical.

NothingOSS header SHA256:

`2788fd7eaac2c95ebe99847f6b064b8e7ac7457896f9bd73ab83341b2ee1e978`

Google exact-GKI header SHA256:

`6503a32b9a3be0018e92494b943a30cb821fb05649bde97fb89bf6b74582a6f9`

The build error is therefore being investigated as another vendor/common
header namespace mismatch, analogous to the previously proven
`linux/rpmsg/mtk_rpmsg.h` collision.

No MediaTek C source has been modified and there is currently no evidence that
binary reconstruction is required.

## Vendor SIP-header resolution

The NothingOSS MediaTek SIP header contains:

`MTK_SIP_TINYSYS_SSPM_CONTROL`

defined as:

`MTK_SIP_SMC_CMD(0x53C)`

The exact Google GKI 12901745 version of
`include/linux/soc/mediatek/mtk_sip_svc.h` does not contain this vendor SMC
definition.

The unchanged NothingOSS vendor header was therefore staged into the standalone
external-module build and prioritized ahead of the Google common header using
the external vendor include tree.

No modification to `mtk-mbox-mailbox.c` was required.

## Final exact-GKI validation

The unchanged NothingOSS:

`device_modules/drivers/mailbox/mtk-mbox-mailbox.c`

was successfully built against exact Google GKI build 12901745 using the
unchanged NothingOSS MediaTek SIP header.

Validation:

- build: success
- donor `mtk-mbox-mailbox.c`: unchanged
- donor `mtk_sip_svc.h`: unchanged
- imported symbols: exact
- imported MODVERSION contract: exact
- function topology/sizes: exact
- raw `.text`: exact
- stock `.text` SHA256:
  `286a6b997c1c25086db43d2e20a33c35e0a3d23f26c4c06cf333482d506d1c58`
- rebuilt `.text` SHA256:
  `286a6b997c1c25086db43d2e20a33c35e0a3d23f26c4c06cf333482d506d1c58`
- `MAILBOX_TEXT_CMP_RC=0`

Stock and rebuilt `mtk-mbox-mailbox.ko` contain byte-identical `.text`.

### Final classification

`mtk-mbox-mailbox.ko`: **DIRECT_SOURCE_MATCH**

Primary donor:

`NothingOSS/device_modules/drivers/mailbox/mtk-mbox-mailbox.c`

Required vendor API header:

`NothingOSS/device_modules/include/linux/soc/mediatek/mtk_sip_svc.h`

Source reconstruction required: **NONE**

### Important integration lesson

Exact Google GKI is the correct kernel core, but it does not necessarily carry
the complete MediaTek vendor header namespace expected by MT6878 vendor
modules.

At least two confirmed examples now exist:

1. `linux/rpmsg/mtk_rpmsg.h`
2. `linux/soc/mediatek/mtk_sip_svc.h`

For LieppOS's MT6878 vendor-module build, the matching MediaTek vendor header
tree must be layered ahead of Google common headers where the namespaces
overlap.

## Current final status

**Classification:** `DIRECT_SOURCE_MATCH`

The NothingOSS MT6878 mailbox-controller source was built against exact
GKI 12901745 and validated against the GQ5012BF1 stock module.

Final raw `.text` SHA256:

    286a6b997c1c25086db43d2e20a33c35e0a3d23f26c4c06cf333482d506d1c58

This module is frozen for initial LieppOS custom-kernel integration.
