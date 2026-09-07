# Phase 4 — VTDR6115 exact-GKI build verification

## Inputs

- GKI artifact/workspace: `12901745`
- Common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` (`android14-6.1-2024-12_r4`)
- Compiler: Android clang 17.0.2 `r487747c` (`d9f89f4d16663d5012e5c09495f3b30ece3d2362`)
- Kleaf mode: `kernel_aarch64`, LTO default, trim
- Source target: `//lieppos/panel-vtdr6115-recon:panel_vtdr6115_recon`
- Dependency: source-built inert `//lieppos/panel-vtdr6115-provider-harness:mtk_panel_ext_harness`

## Reproducible layout

Copy `kernel/phase4-panel-vtdr6115-recon/` to `$GKI_WS/lieppos/panel-vtdr6115-recon/` and its `provider-harness/` contents to `$GKI_WS/lieppos/panel-vtdr6115-provider-harness/`. Then:

```sh
cd "$GKI_WS"
tools/bazel build //lieppos/panel-vtdr6115-recon:panel_vtdr6115_recon
```

## Result

```text
BUILD_RC=0
warnings=0
errors=0
unresolved symbols=0
modpost warning suppression=none
hand-written Module.symvers=none
depends=mtk_panel_ext,mediatek-drm
output=bazel-bin/lieppos/panel-vtdr6115-recon/panel_vtdr6115_recon/panel-ky-vtdr6115-dphy-cmd.ko
```

Final comparison artifact: 245,960 bytes, SHA-256 `f29e4d2948d4f116f09e2ab83856bd4db803ffbc0dc0cb15978865cf4ca94ddb`. Treat the Bazel output as ephemeral and regenerate it; the authoritative verification is section/function/data/CRC content, not this nondeployable harness-linked file hash.

Final module metadata matches stock on author, description, license, module name, aliases and dependency names. Local vermagic is `6.1.115-android14-11-maybe-dirty ...` versus stock's SCM suffix `g945dff7bc1bf`.

## Structural comparison

- Function set: 24/24; 22/24 same size; 19/24 byte-identical.
- Entire `.data`: 199,816/199,816 byte-identical.
- All three 66,328-byte panel-ext parameter objects: byte-identical.
- `.rodata.str1.1`: 1,955/1,955 byte-identical.
- `.init.text`, `.exit.text`, `.gnu.linkonce.this_module`: byte-identical.
- `.text`: stock 6,424, reconstruction 6,416 bytes.
- All 46 static init command arrays match stock byte-for-byte; runtime stream is 45 writes/287 bytes.
- MODVERSION: 38/45 match (all GKI); seven vendor provider CRCs differ.

The five non-byte-identical functions are `lcm_probe`, `lcm_panel_init`, `lcm_setbacklight_cmdq`, `sethbm_cmdq`, and `set_hbm_backlight_store`. Deltas are compiler/source-shape effects (stack slot width/order, dead initializer retention, local constant placement, register scheduling); transmitted payloads, branch outcomes, callback calls, GPIO operations, delays, object offsets and user-visible strings are accounted for. This is not a claim of whole-module byte identity.

## Deployment verdict

The build is a valid exact-GKI compiler and modpost test, but **not deployable** because its seven harness-generated vendor CRCs do not equal the stock provider CRCs. No load test was attempted.
