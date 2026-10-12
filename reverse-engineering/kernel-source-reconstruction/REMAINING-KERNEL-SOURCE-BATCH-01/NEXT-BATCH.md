# Remaining work after this batch

If integrated, Category D falls to 3 and the uncertified queue to 67 (10 C + 3 D + 54 G).

## Category D (3) — all blocked on source, not on build engineering

| Module | Blocker | Route |
|---|---|---|
| flashlight | OEM `flashlight-core.c` variant unavailable | GPL source request (below) |
| fpsgo | `fpsgo_cus` links `xgf_v3_ko_quark*.o_shipped` | stays D unless MediaTek publishes the xgf C source |
| msync2_frd | `msync2_frd_cus` links `mtk_disp_msync.o_shipped` | stays D unless the msync C source is published |

## flashlight GPL source-request specification (not sent)

- **Device:** Ulefone Armor 29 Pro Thermal, GQ5012BF1, MT6878T.
- **Kernel:** `6.1.115-android14-11-g945dff7bc1bf`, the shipped GKI vendor modules.
- **File:** `kernel_device_modules-6.1/drivers/misc/mediatek/flashlight/flashlight-core.c`, the exact revision
  compiled into stock `flashlight.ko` (sha256 `87b18cde1f47c857…`), plus its Kconfig/defconfig fragment.
- **Distinguishing content:** functions `flashlight_drvctrl`, `flashlight_sw_ctrl_show`, `flashlight_sw_ctrl_store`;
  format string `ignore pt(%d,%d,%d), pt strict(%d)`; no `pt_oc_callback` / `register_battery_oc_notify`.
- **Basis:** the GPL-2.0 module licence (`license=GPL` in the stock modinfo) requires corresponding source.

## Category G (54) and C (10)

- 23 G identities belong to Codex's G-SOURCE-RECOVERY-BATCH-01 and must not be selected until its result is
  integrated or abandoned.
- The remaining 31 G and the 10 C rows should be reassessed by exact identity after Codex's integration, using the
  engines now available: KDM external (KDM-MEDIA-SECURITY), native split-BTF (this batch), separate
  kernel_modules roots (this batch) and the GPU pin.
