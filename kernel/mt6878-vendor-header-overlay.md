# MT6878 vendor header overlay on exact Google GKI

## Conclusion

LieppOS should use exact Google GKI build 12901745 as the kernel core while
overlaying the matching MediaTek MT6878 vendor header API where vendor modules
expect extensions that are absent from Google common.

This is not a kernel-core fork requirement. It is a vendor-module build API
requirement.

## Proven namespace collisions

### linux/rpmsg/mtk_rpmsg.h

Google common provides a generic/older MediaTek RPMSG API.

NothingOSS MT6878 extends the same header namespace with the concrete TinySys
mailbox RPMSG types required by:

- `mtk_rpmsg_mbox`
- `mtk_tinysys_ipi`

Using the MT6878 vendor header produced exact stock `.text`.

### linux/soc/mediatek/mtk_sip_svc.h

Google common does not contain the full MediaTek vendor SMC command set.

NothingOSS MT6878 contains additional commands including:

`MTK_SIP_TINYSYS_SSPM_CONTROL = MTK_SIP_SMC_CMD(0x53C)`

This definition is required by `mtk-mbox-mailbox`.

Using the unchanged MT6878 vendor header produced exact stock `.text`.

## Build policy

For reconstructed LieppOS MT6878 vendor modules:

1. use exact Google GKI 12901745 as kernel core;
2. use matching MediaTek/MT6878 vendor headers for vendor-facing APIs;
3. prioritize the vendor header tree where namespaces collide;
4. never patch donor C merely to compensate for the wrong common header;
5. validate every module against stock ABI, function topology, and `.text`.

The following modules now prove this strategy:

- `mtk-mbox`
- `mtk_rpmsg_mbox`
- `mtk_tinysys_ipi`
- `mtk-mbox-mailbox`
