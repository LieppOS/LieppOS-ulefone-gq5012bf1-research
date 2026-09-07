# Phase 4 — `panel_ky_vtdr6115_dphy_cmd.ko` reconstruction

Authoritative report for the Ulefone Armor 29 Pro Thermal (`GQ5012BF1`, MT6878/T) main-display panel module.

## Verdict

This is a precise ABI-boundary block, not an analysis failure. The panel's hardware behavior is reconstructed to high confidence, including exact command payloads and byte-identical panel parameter objects. A source-built module cannot yet replace stock because the exact Ulefone MediaTek display provider header/type graph is missing and all seven intermodule MODVERSION CRCs fail against stock. A completion/source-match label would imply a deployable replacement and is therefore rejected. Do not hand-patch CRCs.

## Deliverables

Complete source and wiring:

- `phase4-panel-vtdr6115-recon/panel-ky-vtdr6115-dphy-cmd.c`
- `phase4-panel-vtdr6115-recon/mtk_panel_ext_stock_abi.h`
- `phase4-panel-vtdr6115-recon/{Makefile,BUILD.bazel}`
- `phase4-panel-vtdr6115-recon/provider-harness/` (comparison only; never ship)

Evidence:

- `phase4-panel-vtdr6115-stock-inventory.md` / `-stock-oracle.txt`
- `phase4-panel-vtdr6115-source-candidates.md`
- `phase4-panel-vtdr6115-RED.md`
- `phase4-panel-vtdr6115-hardware-contract.md`
- `phase4-panel-vtdr6115-dt-contract.md`
- `phase4-panel-vtdr6115-provider-contract.md`
- `phase4-panel-vtdr6115-build-verification.md`
- machine-readable `-functions.tsv`, `-objects.tsv`, `-imports.tsv`, `-modversions.tsv`, `-provider-boundary.tsv`, `-consumer-boundary.tsv`, `-command-table.tsv`
- `phase4-panel-vtdr6115-donor-to-recon.diff`
- `phase4-panel-vtdr6115-verify-recon-vs-stock.txt`

## What is proved exact

1. **Identity and binding:** module name, author, description, license, aliases, OF compatible, driver name, and provider names.
2. **Function/object inventory:** 24/24 functions and all observed initialized objects reconstructed; no exports.
3. **Panel parameter data:** entire 199,816-byte `.data` section is byte-identical. This includes three 66,328-byte `mtk_panel_params` objects, operation tables, class attribute mode 0664, RC arrays and global defaults.
4. **Strings:** entire 1,955-byte `.rodata.str1.1` is byte-identical.
5. **Commands:** all 46 static init payload objects match stock byte-for-byte. Runtime init is 45 writes/287 bytes for each FPS choice; the exact 95-byte DSC PPS, suspend writes, backlight, HBM and fingerprint paths are tabulated.
6. **Modes/link:** 1080×2400 at 60/90/120 Hz, 120 preferred, four-lane RGB888, 870 Mbit/s/lane, PLL 435 MHz, video/sync-pulse/LPM/noncontinuous/no-EOT flags.
7. **Lifecycle:** exact GPIO order and 15/15/15/20 ms reset, 120/50 ms sleep-out/display-on delays, and 20/200/10/10/10 ms suspend/power-off delays.
8. **GKI ABI:** all 38 GKI MODVERSION CRCs match stock exactly under artifact 12901745.
9. **Compile/link quality:** exact-GKI Kleaf build passes with 0 warnings, 0 errors, and 0 unresolved symbols when linked to the source-built inert comparison harness.

## Residual code-generation differences

Stock `.text` is 6,424 bytes versus 6,416; 19/24 functions are byte-identical and 22/24 are size-identical. The five remaining functions differ only in observable compiler/source-shape residue already bounded by constants, references, branches and payload data: `lcm_probe`, `lcm_panel_init`, `lcm_setbacklight_cmdq`, `sethbm_cmdq`, and `set_hbm_backlight_store`. `.rodata` differs by a three-byte local brightness initializer placement/order. Local vermagic SCM suffix also differs.

These are not known hardware-affecting discrepancies. Nevertheless the provider CRC blocker independently prevents a deployable completion claim.

## Exact missing evidence

Required evidence is one coherent source/header revision that generates these seven stock CRCs:

```text
mtk_panel_ext_create       ea18945b
mtk_panel_tch_handle_reg   5adffa30
find_panel_ext             aa9afc3e
find_panel_ctx             5ba935bb
mtk_panel_detach           deb133c5
mtk_panel_remove           5d406eb0
ddic_dsi_send_cmd_for_fp   14818502
```

Public NothingOSS and Motorola type graphs fail this test. The missing material is specifically the Ulefone/MediaTek-patched `mtk_panel_ext.h`, related DRM definitions (including `struct drm_panel` reachability), and the matching provider implementation/build configuration. A stock provider binary alone does not produce source-build symvers.

## Deployment / replacement plan

Current disposition remains:

```text
YES_WITH_STOCK_PROVIDER_CHAIN — retain the stock panel module itself
```

Keep these as one stock ABI island, in stock load order:

1. `panel-ky-vtdr6115-dphy-cmd.ko`
2. `mtk_panel_ext.ko`
3. `mediatek-drm.ko`

The committed reconstruction is ready for immediate rebuild once the exact provider type graph is obtained. At that point require: seven CRC matches, stock dependency names, clean exact-GKI build, no unresolved symbols, and then hardware validation under a separately authorized test plan. No live hardware testing or write operation was performed in this task.

## Confidence tiers

- **Tier A (binary/DT proved):** identity, imports/CRCs, command bytes/order, modes, panel-param bytes, GPIO/timing paths, DSI flags, callbacks, sysfs ABI, absent features.
- **Tier B (strong semantic reconstruction):** C source shape for five non-byte-identical functions; all observable hardware effects are accounted for.
- **Tier C (blocked):** exact vendor header type spelling/layout reachability needed by genksyms and therefore deployable stock-provider linkage.

## Next experiment

Do not test on hardware. Search vendor GPL drops/build servers for the exact display source revision corresponding to stock SCM `g945dff7bc1bf`, then compile only the two provider modules to obtain generated `Module.symvers`. Compare the seven CRCs before rebuilding or packaging this panel.

## Final classification

`BLOCKED_WITH_EXACT_MISSING_EVIDENCE`
