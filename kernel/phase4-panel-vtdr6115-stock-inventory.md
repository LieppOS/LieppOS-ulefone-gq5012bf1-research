# Phase 4 — VTDR6115 stock inventory

Target: `panel_ky_vtdr6115_dphy_cmd.ko`, the main 1080×2400 AMOLED panel driver in the Ulefone Armor 29 Pro Thermal (`GQ5012BF1`, MT6878/T).

## Canonical artifact

| Property | Value |
|---|---|
| Path | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/panel-ky-vtdr6115-dphy-cmd.ko` |
| Preserved oracle | `workspace/phase4-panel-vtdr6115/stock-panel-ky-vtdr6115-dphy-cmd.ko` |
| Stock copies found | 1 |
| Size | 246,288 bytes |
| SHA-256 | `1e5778f3612378dd6fc3ba96ca461d8ba0661fc6617290a7c64245ede3f3af07` |
| Build ID | `c86ee66361fe30b7b27e0c1a11edb1b81eafd2b0` |
| Compiler | Android clang 17.0.2, `r487747c` |
| Vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| Module name | `panel_ky_vtdr6115_dphy_cmd` |
| Description | `vtdr6115 VDO 120HZ AMOLED Panel Driver` |
| Depends | `mtk_panel_ext,mediatek-drm` |
| OF compatible | `hx,vtdr6115,cmd,120hz,ky` |
| Exports | 0 |
| Functions | 24 (22 `.text`, init, exit) |
| Undefined imports | 44: 37 GKI and 7 vendor-module symbols |
| MODVERSION entries | 45 including `module_layout` |

Stock placement/load order is boot-critical for UI: platform `modules.load` index 76 and recovery index 74. It is a leaf consumer of six `mtk_panel_ext` symbols and one `mediatek-drm` symbol.

Machine-readable detail: `phase4-panel-vtdr6115-{functions,objects,imports,modversions,provider-boundary,consumer-boundary}.tsv`. Raw oracle metadata/disassembly is preserved under `workspace/phase4-panel-vtdr6115/`.
