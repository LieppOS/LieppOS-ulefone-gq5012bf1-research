# Security boundaries

## Scope

This batch reconstructs only the **normal-world Linux host modules** that ship on GQ5012BF1. The following were
not read, extracted, recreated or exercised:

- Widevine keys and provisioning;
- trusted applications (TAs) or TEE/GenieZone firmware;
- secure-memory contents;
- PMIC efuse contents.

Matching source does **not** mean that any of the following has been recreated or verified:

- Widevine L1, DRM attestation or Play Integrity;
- trusted-UI isolation;
- secure-memory isolation;
- efuse confidentiality.

## Per-module boundary

| Module | Normal-world role (source) | Boundary crossed | Not claimed |
|---|---|---|---|
| mtk_sec_heap | DMA-BUF heap `mtk-dma-heap-secure` family (page and region heaps per stock DT). Exports 3 symbols (`is_mtk_sec_heap_dmabuf`, `is_support_secure_handle`, `dmabuf_to_secure_handle`); stock importers: sapu, widevine_driver, mtk_heap_debug, gz_main_mod, mali_kbase_mt6878_r44, mtk-cam-isp7sp, mtk_disp_sec | calls into **tmem_ffa** (trusted-memory FF-A; 11 imports; Codex G target) to obtain secure handles | that secure regions are actually protected or isolated on this device |
| widevine_driver | `mediatek,drm_wv` platform driver ("Widevine Drm Driver"); converts DMA-BUFs to secure handles via mtk_sec_heap | none directly; the secure pipeline is in the TEE | Widevine level, keybox, L1 status |
| sapu | Secure APU bridge: misc device `/dev/apusys_sapu` + `apusys_sapu_internal_ioctl`. Attaches/maps DMA-BUFs, converts them to secure handles, opens **GenieZone KREE** sessions (`KREE_CreateSession` / `KREE_TeeServiceCall` / `KREE_CloseSession` from gz_tz_system; trusty calls from gz_trusty_mod, both Codex G targets), and handles an APU power lock over rpmsg (`apu-lock-rv-rpmsg`) | normal world to GenieZone through KREE; normal world to the APU microprocessor through rpmsg | any secure-APU workload, model protection or firmware behaviour |
| tui-common | 3 exported hooks only: `register_tpd_tui_request`, `tpd_enter_tui`, `tpd_exit_tui` (touch-panel hand-over to a trusted UI). No device node, no DT | none itself; a touch driver and a TUI driver would call these | that any trusted UI exists or works on GQ5012BF1 (`CONFIG_TRUSTONIC_TRUSTED_UI=m`, but no TUI TA is reconstructed) |
| nvmem-mt635x-efuse | read-only NVMEM provider over the PMIC regmap | none (PMIC efuse, not SoC secure OTP) | efuse values; no read was performed |

## Codex G providers

`tmem_ffa`, `gz_trusty_mod` and `gz_tz_system` belong to Codex's G-SOURCE-RECOVERY-BATCH-01, and `mtk-pwm` is G.

- They were compiled from pinned ALPS **only inside this batch's own workspace**, solely to confirm the import ABI:
  CRC, licence, namespace and KCFI. All 18 slots match.
- Their audit rows, repositories and workspaces are untouched.
- The consumers certified here (mtk_sec_heap, sapu, mtk_irtx_pwm) depend on providers that are still G. Their own
  source certification does not certify those providers.
