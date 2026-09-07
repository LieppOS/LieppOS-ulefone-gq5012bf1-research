# Phase 4 — VTDR6115 provider/ABI contract

The panel is a leaf module: zero exports and no stock module consumers. It imports 44 symbols; 37 are supplied by GKI/vmlinux and seven by stock vendor display modules.

| Symbol | Provider | Stock CRC | Source-built harness CRC |
|---|---|---:|---:|
| `mtk_panel_ext_create` | `mtk_panel_ext` | `0xea18945b` | `0xc2be662b` |
| `mtk_panel_tch_handle_reg` | `mtk_panel_ext` | `0x5adffa30` | `0x32f8ae50` |
| `find_panel_ext` | `mtk_panel_ext` | `0xaa9afc3e` | `0x242df3a0` |
| `find_panel_ctx` | `mtk_panel_ext` | `0x5ba935bb` | `0xc7f8a680` |
| `mtk_panel_detach` | `mtk_panel_ext` | `0xdeb133c5` | `0xa64ceb55` |
| `mtk_panel_remove` | `mtk_panel_ext` | `0x5d406eb0` | `0xd859acf8` |
| `ddic_dsi_send_cmd_for_fp` | `mediatek-drm` | `0x14818502` | `0x24f2fc08` |

All 38 non-vendor MODVERSION entries, including `module_layout`, match stock exactly under GKI artifact 12901745. All seven vendor entries differ.

## Why this is an exact evidence blocker

Linux genksyms includes reachable struct/type definitions, not only the visible pointer spelling. Public NothingOSS and Motorola declarations have the same apparent prototypes, yet compiling their real type graphs does not produce the stock CRCs. Even functions taking only `struct drm_panel *` differ, proving that Ulefone's MediaTek-patched DRM/type graph is not represented by exact GKI headers.

The stock-layout reconstruction header proves panel object offsets/sizes and allows panel logic to compile. It does not claim to recreate unseen type text. `struct mtk_panel_params` stock size is 66,328 bytes and `struct mtk_panel_funcs` is 320; NothingOSS's revision is 69,232 and 336 respectively, with material field/callback offset changes.

## Build harness versus deployable chain

`phase4-panel-vtdr6115-recon/provider-harness/` builds two inert source modules named `mtk_panel_ext.ko` and `mediatek-drm.ko`. They produce a real `Module.symvers`; no CRC file is hand-authored and no unresolved-symbol warning is suppressed. This is valid for compiler/modpost/structural verification only.

**Never load or package the harness.** Its functions intentionally return `-ENODEV`/`NULL`.

A deployable reconstructed panel requires either:

1. the exact Ulefone MediaTek display provider source/header revision, then rebuilding the panel against its generated `Module.symvers`; or
2. retention of the stock panel binary with the stock `mtk_panel_ext` and `mediatek-drm` provider chain.

Building this source against the harness yields different seven CRC entries and cannot be loaded alongside stock providers. Hand-patching CRCs is explicitly rejected as non-source reconstruction.
