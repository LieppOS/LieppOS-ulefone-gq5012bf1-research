# Source lineage

Maintained source: `../android_kernel_modules_display_backlight_ulefone_gq5012bf1` @
`c0b39b61bf23f18d30c25f8cdb7ec8cb6b7b2c7f` (tree `f892960f…`).

- It is a history-preserving fork of the MET instrumentation engine (7839af7c), whose NKM root is needed for
  `met_backlight_api`.
- It owns only the 8 frozen identities.

## Immutable inputs

| Input | Commit | Role |
|---|---|---|
| MediaTek ALPS (NothingOSS mirror) | `5e415e059253ce0d2e61c97108e5f5785d71f06f`, tree `9c61acc3…` | C/H/Kbuild for the 7 KDM targets and all KDM witness providers |
| NothingOSS device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | Kconfig + `mgk_64_k61_defconfig` |
| NothingOSS kernel_modules | `5f75a3b13e8135d45b4b0b70ec893345144f70df`, tree `286db3d3…` | `met_drv_v3` core (witness) and `met_api/met_backlight_api` (target) |
| GKI kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | headers, Kbuild/modpost; GKI 12901745 vmlinux.symvers |
| clang | `7775eb113f960bc69a780b621d03a715914d4bca` | r487747c |
| GQ5012BF1 config fragments | `reference/gq5012bf1-audio.config` (3 ODM audio toggles) + `reference/gq5012bf1-tee.config` (Microtrust disabled) | vendor `.config` `67f85473…` |

## Source deltas

| Patch | Origin | Effect |
|---|---|---|
| `0001`–`0010` | Unchanged copy of the certified shared DRM series (`audio_shared_infrastructure` @ 4697eac3, from historical MEDIATEK-DRM) | Patches the `mediatek_v2` tree and shared headers that mediatek-drm-panel-drv and mtk_disp_sec compile against. Required so that their witnesses (mediatek-drm, mtk_panel_ext) give stock CRCs |
| `0011-pwm-mtk-disp-GQ5012BF1-mt6878-disp-pwm0-1-probe-logs.patch` | Historical LieppOS BACKLIGHT-DISPLAY-GLUE commit 5326ad70 (2026-10-04), rebased onto ALPS 5e415e05 | Adds 2 of_match entries and 2 probe `pr_notice` lines. Post-image blob `6459e7e2…`. **A reconstruction proven by byte-identical output**, corroborated by the stock modalias strings, the probe printk strings and the stock DT nodes; not verbatim OEM text |

### pwm-mtk-disp lineage detail

- The ALPS 5e415e05 blob `2a65802d` equals the public MTK commit e46af0f79a1a ("disp_pwm: fix backlight flicker
  issue when lk bootup").
- Historical LieppOS applied the GQ5012BF1 hunks on top of the older 957dac blob `3c313edc`. Rebased onto
  5e415e05, it needs only the three GQ5012BF1 hunks, and the result equals historical post-image `6459e7e2`
  byte for byte.

## Unmodified public source

- mtk-pwm: `drivers/misc/mediatek/pwm` (`mtk_pwm.c` + `pwm_v2`).
- rt4831a_drv: `drivers/misc/mediatek/gate_ic/rt4831a_drv.c`.
- mediatek-drm-gateic: `drivers/gpu/drm/panel/mtk_drm_panel_i2c.c`, `mtk_drm_gateic_rt4801h.c`,
  `mtk_drm_gateic_rt4831a.c` and `mtk_drm_gateic.c`.
- mediatek-drm-panel-drv: `drivers/gpu/drm/panel/mtk_drm_panel_drv*.c` and helpers.
- leds-mtk-disp: `drivers/leds/leds-mtk-disp.c`.
- mtk_disp_sec: `drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_sec.c`.
- met_backlight_api: `met_drv_v3/met_api/met_backlight_api`.

## Configuration finding (new)

A first build with the plain audio-only vendor config (`b826d842`) compiled everything. However, 3 of the 31
provider boundaries (`cmdq_sec_mbox_stop`, `cmdq_sec_pkt_set_data`, `cmdq_sec_pkt_set_mtee`) gave non-stock
CRCs: genksyms pulls Microtrust `teei_client_main.h` into the cmdq-sec type graph. With the GQ5012BF1 TEE
fragment, which the cmdq repository had already established, all 31 match. The stock device ships TrustKernel,
not Microtrust. The failed run is preserved in `evidence/development/D1-*`.

## Prior historical work used only as lineage

`Reverse Engineer - DONE/BACKLIGHT-DISPLAY-GLUE` and `MEDIATEK-DRM` (2026-10-04) had byte-identical isolated
rebuilds, but with provider CRCs taken from stock `__kcrctab` and no pinned bootstrap. Here every provider CRC
comes from natural compilation of pinned source, and the build is reproduced from fresh bundle clones.
