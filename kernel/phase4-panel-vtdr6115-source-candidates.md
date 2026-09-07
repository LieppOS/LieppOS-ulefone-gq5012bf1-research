# Phase 4 — VTDR6115 source candidates

## Exact-source search result

No exact Ulefone/YFT/KY source was found by filename, OF compatible, log tag, or distinctive command sequence searches. Search keys included `panel_ky_vtdr6115_dphy_cmd`, `panel-ky-vtdr6115-dphy-cmd`, `hx,vtdr6115,cmd,120hz,ky`, `yft-lcm-vtdr6115-drv-`, and VTDR6115 command fragments.

## Frozen Motorola donor

- Repository: `https://github.com/MotorolaMobilityLLC/kernel-mtk`
- Commit: `0087a407394abd3ab073e1a2df164f1187959a3f`
- URL: `https://raw.githubusercontent.com/MotorolaMobilityLLC/kernel-mtk/0087a407394abd3ab073e1a2df164f1187959a3f/drivers/gpu/drm/panel/dsi-panel-mot-csot-vtdr6115-655-fhdp-dphy-vdo-144hz.c`
- Frozen file: `workspace/phase4-panel-vtdr6115/donor/donor.c`
- Size/SHA-256: 30,473 bytes / `14bdae12bd622dca1c5113bacf6bf9f3d487d4c5ea33e98d76d42c7567ac5b44`
- Matching header at commit: 16,158 bytes / `0f7ceb1457027421ff628d43e4e9d4c30b11b91704fe32099986dbe50a8bc083`

Classification: **STRUCTURAL_DONOR_ONLY**. It establishes MediaTek panel-driver organization and VTDR6115/DSC concepts, but is a Motorola CSOT 144 Hz VDO/LHBM panel. Ulefone is KY 120 Hz, has different mode timings, GPIO sequencing, HBM/fingerprint path, callback surface, and DSI command tables. Its DSC 1.1 8-bpp PPS is the only byte-level payload match of consequence.

The mandatory unmodified-donor exact-GKI RED build fails before linking. With the donor C byte-identical, clang reports missing `panel_cellid_{reg,offset_reg,len}` members in its own matching `mtk_panel_params`, removed `MIPI_DSI_MODE_EOT_PACKET`, and the 6.1 `mipi_dsi_driver.remove` signature mismatch. See `phase4-panel-vtdr6115-RED.md`.

## NothingOSS MT6878 source family

- Repository: `https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`
- Commit: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- Relevant family: `drivers/gpu/drm/panel/panel-*.c`
- Header: `drivers/gpu/drm/mediatek/mediatek_v2/mtk_panel_ext.h`
- Header SHA-256: `0ed744f07fd7cb045eb5548333a3f97871f7c59b564d8615cd650ff446cdbecd`

Classification: **SKELETON_ONLY / ABI-INCOMPATIBLE**. Compiled probes show `struct mtk_panel_params` 69,232 bytes versus stock object size 66,328, and `struct mtk_panel_funcs` 336 versus stock 320. Proven callback and field offsets differ. It cannot be substituted as the stock ABI header.

## Reconstruction basis

The committed source in `phase4-panel-vtdr6115-recon/` is therefore a clean-room oracle reconstruction: Linux/MediaTek control skeleton, exact stock strings, exact stock initialized objects, stock relocation/call order, and exact command payloads. Reserved fields in `mtk_panel_ext_stock_abi.h` model only offsets/sizes proved from the stock ELF; they are not represented as the unavailable vendor header.
