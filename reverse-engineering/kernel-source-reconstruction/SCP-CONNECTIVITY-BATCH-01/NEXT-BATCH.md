# Recommended next independent work

Remaining uncertified groups after Batch04 (30), AUDIO-BATCH-01 (21) and this batch (20), on the frozen baseline:

| Group | Uncertified | Notes |
|---|---:|---|
| PRESERVE:MODEM | 16 | ccci_*, c2k_*, ccmni, mddp, mdpm. `ccci_md_all` and `mddp` export CRCs are already reproduced from ALPS here and in audio |
| met_drv_v3 | 10 | debug-only |
| PRESERVE:DISPLAY-GLUE + MEDIATEK-DRM + MTK-DISP-NOTIFY | 12 | `mtk_disp_notify` is a provider for sensorhub, uarthub and bt_drv; its CRCs are already witnessed from ALPS |
| vendor in-tree split-BTF modules | 11 (3 here are C) | one shared blocker, see below |

**Recommendation A, highest leverage: the BTF-BASE experiment.** It is one experiment, not a batch,
and it would close 11 identities: cfg80211, mac80211, bluetooth, Batch03 thermal-generic-adc, arm_dsu_pmu,
drm_display_helper, drm_dma_helper, industrialio-triggered-buffer, kfifo_buf, reboot-mode and
syscon-reboot-mode.
- **Target.** All 11 stock modules imply the same base (`evidence/btf-residual/oem-base-census.txt`). It needs a base with **130 366 types and a 2 300 745-byte string table**
  (public 12901745 has 130 351 types and 2 300 356 bytes; shift +15/+389, measured here).
- **Candidates.** Public android14-6.1 commits after `6b18f0b5` that still report 6.1.115-android14-11.
  Take the CI `vmlinux` artifacts, or build `vmlinux` from those commits with the pinned clang and pahole 1.23.
- **Acceptance.** A base counts only if it is public, verified and makes `.BTF` byte-identical
  without any edit.

**Recommendation B, a normal batch: DISPLAY-GLUE-BATCH-01.** It covers mtk_disp_notify, mediatek-drm,
mtk_panel_ext, mediatek-drm-panel-drv, leds-mtk(+disp), pwm-mtk-disp, mtk-pwm, rt4831a_drv,
mediatek-drm-gateic and met_backlight_api: 12 modules (DISPLAY-GLUE 8 + MEDIATEK-DRM 3 + MTK-DISP-NOTIFY 1). They are mostly ALPS KDM, which this engine
already handles. `mtk_disp_notify` is a provider for 4 certified-or-pending modules. The batch does not
overlap charging/USB, audio or connectivity.

Run MODEM later. It needs separate care for CCCI/MD firmware boundaries.
