# Phase 4 RED — `panel_ky_vtdr6115_dphy_cmd.ko`

## Oracle preservation

The single stock module was copied without modification to `workspace/phase4-panel-vtdr6115/stock-panel-ky-vtdr6115-dphy-cmd.ko`; SHA-256 is `1e5778f3612378dd6fc3ba96ca461d8ba0661fc6617290a7c64245ede3f3af07`. Relocation-aware disassembly, section/symbol/relocation dumps, strings, `.comment`, `.modinfo`, `.rodata`, and `.data` are preserved beside it.

## Unmodified donor RED build

The Motorola donor C was kept byte-identical (30,473 bytes, SHA-256 `14bdae…ac5b44`) in this exact-GKI layout:

```text
$GKI_WS/lieppos/panel-vtdr6115-donor-red/
  panel/dsi-panel-mot-csot-vtdr6115-655-fhdp-dphy-vdo-144hz.c
  panel/*-lhbm-alpha.h
  mediatek/mediatek_v2/{mtk_panel_ext.h,mtk_drm_graphics_base.h}
  include/drm/mediatek_drm.h
```

Command:

```sh
cd /home/armol/kernel-work/gki-12901745-workspace
tools/bazel build //lieppos/panel-vtdr6115-donor-red:donor_red
```

Result: **FAIL (expected RED)** at compile time, before modpost:

1. Four mode objects reference `panel_cellid_reg`, `panel_cellid_offset_reg`, and `panel_cellid_len`, absent from the matching commit's `struct mtk_panel_params`.
2. `MIPI_DSI_MODE_EOT_PACKET` is absent from exact GKI 6.1 headers.
3. Donor `.remove` is `int (*)(...)`; exact GKI expects `void (*)(...)`.

This is useful negative evidence: the donor is not directly buildable and cannot justify a source-match claim.

## Stock-versus-reconstruction RED observations

- Filename/compatible says `cmd`, but stock sets `mode_flags = 0x0e05`: VIDEO + VIDEO_SYNC_PULSE + LPM + CLOCK_NON_CONTINUOUS + NO_EOT. The module description's `VDO` is behaviorally correct.
- The stock init function has 45 runtime DSI calls, 44 static payloads plus one stack-built brightness payload. Three alternative `0x6c` payload objects select 60/90/120 Hz.
- Stock transmits 287 bytes per initialization. The 95-byte `0x70` DSC PPS is preserved exactly.
- `.data` is 199,816 bytes; all three 66,328-byte panel-parameter objects are byte-identical in reconstruction.
- The ATA callback returns success without a DSI read; there is no panel-ID validation.
- No AOD/doze or CABC callback/command implementation exists.
- `powerdm-gpios` exists in DT but is never requested or referenced by this module.

## Exact-GKI GREEN comparison build

The reconstruction uses GKI artifact 12901745/common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, clang `r487747c`, LTO/default trim, and source-built inert provider harness modules. Command:

```sh
tools/bazel build //lieppos/panel-vtdr6115-recon:panel_vtdr6115_recon
```

Result: **PASS**, 0 warnings, 0 errors, 0 unresolved symbols. The linked artifact depends on `mtk_panel_ext,mediatek-drm`, matching stock provider names.

The harness is deliberately nonfunctional and never shippable. It allows real `genksyms`/modpost/link verification without a hand-written `Module.symvers`; it does **not** solve the seven stock vendor CRCs. All 38 GKI MODVERSION CRCs match stock; all seven vendor-provider CRCs differ.
