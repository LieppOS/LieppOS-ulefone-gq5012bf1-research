# LN2403 final build and parity

Build target: `//lieppos/leds-ln2403-recon:leds_ln2403_recon`, against pinned
`//common:kernel_aarch64`, with the genuine source-built MT6878
`//lieppos/mtk-pwm-provider:mtk_pwm_provider` dependency.

Final result: Bazel RC 0; compiler warnings 0; modpost warnings 0; undefined
symbols 0. Rebuilt artifact SHA256
`9ba9d6fef5d1e364aae07692169cde076eb4c3db509d9032c1265e78351db526`,
size 36,976, Build ID `eff0083a51ae66750cdc35f57c4340d83f06a9d3`.

Parity summary:

- complete function set: 16/16 stock functions present, no rebuild-only function;
- function sizes: 8/16 exact; bytes: 7/16 exact;
- KCFI: 12/12 applicable address-taken/callback IDs exact; the four remaining
  raw pre-function words belong to adjacent direct-call code and are not KCFI IDs;
- imports/MODVERSION: 32/32 names exact and 32/32 CRCs exact;
- provider edges: 2/2 exact CRC/prototype; provider implementation bytes exact;
- stock exports 0; reconstruction exports 0;
- all hardware/state objects—mode tables, attributes, null-terminated sysfs
  pointer array, OF table, platform driver, state globals and provider version
  table—are exact or relocation-equivalent.

Non-byte-identical functions are explained row-by-row in the function TSV.
Differences are source factoring/branch layout and condensed diagnostics; exact
state transitions, constants, GPIO/PWM order, timings, return classes, provider
calls, sysfs ABI and preserved defects are closed. Residual ELF differences are
local `maybe-dirty` vermagic, Build ID, source paths, symbol/string placement
and link metadata. None is hardware- or ABI-significant.
