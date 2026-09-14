# GQ5012BF1 Proprietary Kernel Module Replacement Plan

## Objective

Reduce dependence on stock Ulefone binary kernel modules while preserving a
bootable and debuggable system throughout development.

Current hard ULEFONE_ONLY kernel ABI:

- 17 binary modules
- 304 unique kernel symbol/CRC requirements

Current transitional ULEFONE_ONLY + NEEDS_ULEFONE_PORT ABI:

- 354 unique kernel symbol/CRC requirements

## Priority 1 — yft_gpio_keys — COMPLETE

Classification: `SOURCE_DELTA_RECONSTRUCTION_EXACT`; `SOURCE_RECONSTRUCTED`;
`SOURCE_NOW`; FROZEN FOR RE.

- exact-GKI donor frozen and mandatory RED recorded;
- exact `/yft-gpio-keys` contract: active-low GPIO13/F1 and GPIO8/F2, 16-ms
  debounce, wake capable;
- exact YFT IRQ mask/re-enable/next-edge-rearm and logging delta recovered;
- 23/23 functions byte-identical, 65/65 import/MODVERSION entries exact;
- clean exact-GKI build and 40/40 fail-closed verifier;
- zero exports and no provider-ABI risk.

This module is removed from the active RE queue. Public source alone was not
accepted; closure is against the frozen stock oracle.

## Priority 2 — Touch gesture / FT3680

Treat together:

- yft_tpd_gesture
- focaltech_touch_spi_ft3680

Known yft_tpd_gesture exports include:

- tpgesture_hander
- tpgesture_status
- tpgesture_value

The FT3680 driver imports these APIs in addition to yft_devinfo and
mtk_disp_notify APIs.

The objective is to eliminate the stock touch binary while preserving the
existing DT and userspace-facing behavior.

## Priority 3 — Rear display stack

Provider-first status:

- `hynitron` — **STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**, SOURCE_NOW,
  FROZEN FOR RE; exact stock-yft provider imports and exact two downstream
  export CRCs; 34/34 verifier
- `spi_tiny_co5300_lcd` — **NO_PUBLIC_SOURCE_FOUND /
  STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**, SOURCE_RECONSTRUCTED, SOURCE_NOW,
  FROZEN FOR RE; exact 25-function and 58-MODVERSION sets, byte-identical
  command/image/driver/fops/misc objects, clean exact-GKI build, 30/30 verifier

The rear-display consumer now links to the real source-built frozen Hynitron
provider and the permitted stock `yft_devinfo` ABI witness for its two historical
`*_device_add()`-family gaps. Hynitron was not reopened. The complete rear
TinyLCD kernel stack is source-ready except for the intentionally retained stock
`yft_devinfo` provider policy.

## Priority 4 — yft_devinfo ecosystem

yft_devinfo is the largest Ulefone-specific inter-module ABI hub:

- 23 consumed exported symbols
- 7 consumer modules
- 5 binary-class consumers

Do not replace yft_devinfo without either:

1. preserving its exported module ABI required by remaining stock binaries, or
2. migrating those consumers in the same development phase.

## Priority 5 — Power / charging stack

Candidate modules:

- sh366003_fg — reconstructed from stock oracle with documented residuals; exact 35-import/36-MODVERSION/8-KCFI maps, byte-exact AFI image, exact-GKI build and 527-check verifier PASS; keep stock yft_devinfo and default AFI programming gate
- sc8571_charger
- sc851x_charger — reconstructed from the stock oracle; exact-GKI build clean
- yft_tiny2c_usb — `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`, `SOURCE_RECONSTRUCTED`, `SOURCE_NOW`, FROZEN FOR RE; exact MT6375 flag edge and complete thermal/USB/uSmart contract; clean exact-GKI build and 68/68 verifier
- custom_ldo — reconstructed exactly at the consumer ABI/function level
- custom_ldo_wl2868 — `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`, FROZEN FOR RE; camera-power provider source-ready

These modules require careful staged testing because failures can affect
charging, battery reporting and power stability.

## Priority 6 — Main panel

Module:

- panel_ky_vtdr6115_dphy_cmd

The panel logic is now reconstructed from the stock oracle, including exact
command bytes and byte-identical panel parameter blobs. Replacement remains
`BLOCKED_WITH_EXACT_MISSING_EVIDENCE`: its seven MediaTek display-provider CRCs
cannot be source-reproduced without the exact vendor type graph. Retain the
stock panel + `mtk_panel_ext` + `mediatek-drm` ABI island meanwhile.

## Priority 7 — Auxiliary LEDs / regulators

Modules include:

- leds_ln2403 (**completed**; `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`)
- custom LDO glue (**completed**; retained here as historical priority)

Both leaves are source-reconstructed. `leds_ln2403` has its full GPIO/pinctrl,
legacy PWM3, six camping-light modes, seven warning-light modes, two timer state
machines, sysfs/userspace ABI and stock defects closed. Its exact source-built
`mtk-pwm` provider reproduces both consumed functions and CRCs byte-for-byte;
target build is warning-free with 32/32 MODVERSION parity and a 50/50 verifier.
It is `SOURCE_NOW` and FROZEN FOR RE.

## Priority 8 — TrustKernel / fingerprint

Treat as one late-stage security subsystem:

- tkcore — still stock, untouched; island reconstruction reached Phase 3P
  (lifecycle prerequisites closed, Phase-3A core dependencies READY)
  (`PROVIDER_ABI_PARTIAL / NOT RECONSTRUCTED /
  STOCK RUNTIME PROVIDER`, blocked on original TrustKernel private headers)
- tkcore_drv — **SOURCE_RECONSTRUCTED / SOURCE_NOW_WITH_PROVIDER_WITNESSES /
  FROZEN FOR RE** (2026-09-13, updated 2026-09-13 after the ffa_v10 closure:
  provenance split is now 8 NATURAL/5 STOCK_PROVIDER_WITNESS, was 6/7). Ship
  only the `-stockabi` target; keep the stock load order
  `ffa_v10 -> teeperf -> tkcore -> tkcore_drv`. Replacing it does **not** make
  `tkcore` replaceable.
- ffa_v10 — **DIRECT_SOURCE_MATCH / FROZEN FOR RE** (2026-09-13). Exact
  MediaTek vendor source (Nothing MT6878 `device_modules@957dac185efe`),
  unmodified, builds 34/34 byte-identical with all 5 export CRCs natural
  (`kernel/phase4-ffa-v10-reconstruction.md`). Ship `//lieppos/ffa-v10`.
- microarray_fp_tee — **completed** at
  `BEHAVIORALLY-COMPLETE, LOAD-COMPATIBLE, WITH DECLARED ABI PROVENANCE SPLIT`
- fingerprint — **completed** at `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`,
  FROZEN FOR RE; source-ready provider with all 10 export CRCs exact

The remaining sensor/TEE group has high kernel-KMI impact and the highest likely
reverse-engineering and integration difficulty because it crosses:

- GlobalPlatform TEE interfaces
- TrustKernel-specific behavior
- fingerprint transport/glue
- secure-world interaction

It should not block earlier custom-kernel development. The completed
`fingerprint` board-glue provider and the completed `microarray_fp_tee`
consumer can both be source-built while `tkcore` remains stock. `tkcore_drv`
and `ffa_v10` are **no longer** stock — both closed 2026-09-13
(`SOURCE_RECONSTRUCTED / FROZEN FOR RE` and `DIRECT_SOURCE_MATCH / FROZEN FOR
RE` respectively) — but that closure is orthogonal to `microarray_fp_tee`:
`ffa_v10` is not a direct `microarray_fp_tee` provider (its only consumers are
`tkcore_drv`, `tmem_ffa`, `gz_main_mod`), and `microarray_fp_tee`'s remaining runtime stock dependency is now only
`tkcore`. `spi-mt65xx` closed separately as `DIRECT_SOURCE_MATCH / FROZEN FOR
RE`: both SPI CRCs are natural and the frozen MicroArray acceptance build is
66/66 exact with 65 natural ABI edges. `tee_spi_transfer` remains the one
stock-runtime witness because tkcore is not reconstructed.

`tmem_ffa` closed 2026-09-13 as **`DIRECT_SOURCE_MATCH / SOURCE_NOW / FROZEN
FOR RE`**: exact pinned MediaTek vendor source
(`device_modules@957dac18`, `drivers/misc/mediatek/trusted_mem/` — the same
revision and parent directory as `ffa_v10`), 141/141 functions byte-identical,
141/141 KCFI, 76/76 imports, 77/77 MODVERSIONs, **15/15 export CRCs natural**,
76/76 verifier. Its FF-A edge is served by the real source-built `ffa_v10`;
its 7 `TEEC_*` edges (tkcore) remain stock-runtime, while all 9 `KREE_*`
edges are natural from the source-built `gz_tz_system`.

`gz_tz_system` closed 2026-09-13 as **`SOURCE_DELTA_RECONSTRUCTION_EXACT /
FROZEN FOR RE`**, which retires that second boundary: the MediaTek GenieZone
KREE provider comes from the same pinned revision (`device_modules@957dac18`,
`drivers/misc/mediatek/geniezone/`), rebuilds **61/61 functions
byte-identically** with 50/50 imports, 51/51 MODVERSIONs and **27/27 export
CRCs natural**, and all 5 stock consumers (`gz_main_mod`, `tmem_ffa`,
`cmdq-sec-drv`, `sapu`, `mtk-cam-isp7sp`) keep every one of their 35 edges
natural. 120/120 verifier.

Consequence for `tmem_ffa`: its 9 `KREE_*` edges were rebuilt against the
**real source-built provider** and resolve 9/9 NATURAL, with the module itself
byte-identical to its frozen baseline apart from the GNU build-id. `tmem_ffa`
provider provenance is now 59 GKI / 1 ffa_v10 / **9 gz_tz_system natural** /
7 tkcore stock-runtime. The only remaining stock-runtime provider in the
trusted-memory path is therefore `tkcore`.

The two transport boundaries introduced by that closure are now retired:
`gz_trusty_mod` and `gz_ipc_mod` are both **DIRECT_SOURCE_MATCH / FROZEN FOR
RE** from the same pinned revision. Trusty is the lower provider (59 GKI
imports); IPC consumes exactly 3 natural Trusty edges. A witness-free
`gz_tz_system` acceptance build resolves its 5 IPC + 2 Trusty edges naturally
while retaining 61/61 byte/KCFI and 1082/1082 relocation parity. All 40 direct
stock-consumer edges across both providers accept the natural CRCs. See
`phase4-gz-transport-stack-closure.md`. `tmem_ffa`'s own 15 exports are
consumed by `mtk_sec_heap`, `gz_main_mod` and `mali_kbase_mt6878_r44`, all of
which accept the source-built module unchanged.

`gz_main_mod`, the top of the GenieZone Linux stack and the owner of the
higher-level KREE userspace ABI, is now also **DIRECT_SOURCE_MATCH / FROZEN
FOR RE** from the same pinned revision, built in the vendor directory layout
for `__FILE__` parity. The pinned donor reproduced stock with **zero source
delta**: 42/42 functions byte-identical, 42/42 KCFI, 76/76 imports, 77/77
MODVERSIONs, 2817/2817 relocations. It exports nothing and has **no kernel
consumers at all** (proven across all 471 stock placements), so its
compatibility contract is purely the userspace ioctl ABI, which is reproduced
exactly. 75 of its 76 provider edges are natural; the sole exception,
`dmabuf_to_secure_handle`, is a declared stock `mtk_sec_heap` runtime
provider. See `phase4-gz-main-mod-reconstruction.md` and
`phase4-geniezone-main-stack-acceptance.md`.

## Strategy

Development should initially retain the stock Ulefone kernel and progressively
replace vendor modules.

The eventual custom kernel should target Linux 6.1.115 / Android14-11
compatibility and be validated against the stock CONFIG_MODVERSIONS CRC
requirements.

A replacement module is not considered independent merely because its
kernel-facing KMI is known. Module-to-module ABI dependencies must also be
preserved or migrated.

## Phase 4 custom_ldo_wl2868 closure

`custom_ldo_wl2868` is `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE` and FROZEN
FOR RE. The stock oracle closes the 112-byte static state, exact probe/GPIO and
error order, hardcoded 0x82 selector/forced 0x2f transfer address, both voltage
families, enable bit map/global-bit rule, raw-I2C and misc-device ABIs, and
lifecycle. Source reproduces the exact 15-function/KCFI/call sets, exact 27
MODVERSIONs and `will_ldo_vout`/`will_ldo_en` CRCs. Provider and downstream
`custom_ldo` exact-GKI builds are clean and the fail-closed verifier passes
50/50. The chain `custom_ldo_wl2868 → custom_ldo` is source-ready. Runtime rail
or GPIO testing remains prohibited by this closure task and is not an RE
residual.

## Phase 4 custom_ldo update (2026-09-08)

`custom_ldo` is complete at `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`. Its two
28-byte forwarding functions are byte-identical to stock; exact KCFI, three
import CRCs, two export CRCs, module dependency metadata, and all relocations
are reproduced. Exact-GKI build succeeds with zero compiler/modpost warnings
and zero unresolved symbols against the reconstructed WL2868 provider's real
`Module.symvers`. Only generated srcversion/vermagic provenance differs. It is
removed from the remaining reverse-engineering queue.

## Phase 4 microarray_fp_tee closure (2026-09-12)

`microarray_fp_tee` is complete at
`BEHAVIORALLY-COMPLETE, LOAD-COMPATIBLE, WITH DECLARED ABI PROVENANCE SPLIT`
and is removed from the active RE queue.

No donor source exists (`NO_USEFUL_SOURCE`, `EMPTY-SOURCE RED`). The
reconstruction is clean-room against the frozen oracle
`8e1449cea5d07ef663d368ce5eea27e8c879a9cd70d39f8fc2b5b25445c2cf33`.

Closed: all 27 functions with stock-matching static/global linkage, the
complete 24-command ioctl table including its holes and its return-value
quirks, the `/dev/madev0` character-device ABI (six-member `file_operations`,
no `open`/`release`/`poll`), the 0xc000 read/write clamps, the `mmap`
`pgprot_noncached` mapping, the input/IRQ/workqueue/regulator/probe ordering,
the sysfs `chip_id` attribute, and the exact `tee_spi_transfer` TEEC ABI
(TrustKernel SPI proxy TA `966d3f7c-04ef-1beb-08b7-57f37a6d87f9`, command 0,
`paramTypes 0x75`) with the five-step chip-identification sequence and the
byte-exact 80-byte secure-world configuration blob.

The data path is hybrid and preserved exactly: probe-time identification uses
TrustKernel `tee_spi_transfer` only; runtime `read`/`write` uses normal-world
`spi_sync` under `dev_lock`. `tee_spi_transfer` was never replaced by a generic
TEE call or a direct SPI transfer, and `tkcore`/`tkcore_drv` were not touched.

Two historical closure targets were produced from a single source file:

- `//lieppos/microarray-fp-tee-recon` — **pre-`spi-mt65xx` closure evidence
  target**: 63/66 MODVERSION edges naturally regenerated; the 3
  vendor-provider edges were reported as declared `PROVIDER_ABI_GAP`.
- `//lieppos/microarray-fp-tee-recon-stockabi` — the original closure's 66/66
  exact target. The current post-SPI acceptance build keeps the same exact
  `depends = fingerprint,spi-mt65xx,tkcore` while taking both SPI edges from
  the real source-built provider and only `tee_spi_transfer` from stock tkcore.

**Historical closure state:** 63/66 natural and 3/66 stock-provider
witnesses. **Current post-`spi-mt65xx` acceptance:** 65/66 natural ABI edges,
including both real source-built SPI edges, plus one stock-runtime tkcore
witness; 66/66 exact. `spi-mt65xx` is source-closed; `tkcore` remains stock.

Root cause of the historical 3-edge gap, proven by control experiment: a provider's export
CRCs are computed by genksyms in the *provider's* build against MediaTek vendor
headers. MediaTek's verbatim
`void mtk_spi_set_autosuspend_delay(struct spi_device *, int)` yields
`0x063a223e` under exact GKI while stock `spi-mt65xx.ko` publishes
`0xd3e99558`. All 59 GKI CRCs and all 4 `yft_*` CRCs match exactly, so the
workspace is correct and the divergence is provider-side only.

Both builds are warning-free with zero unresolved symbols; the fail-closed
verifier returns `PASS_WITH_DECLARED_DELTAS` with an empty failure list.
Current remaining declared provider delta: stock-runtime `tee_spi_transfer`;
the two historical SPI gaps are closed naturally. Other historical-target
deltas are its witness `depends` names and the workspace-wide
`vermagic` scmversion stamp (`-maybe-dirty` vs `-g945dff7bc1bf`; GKI commit
`945dff7bc1bf` is absent from this mirror and the delta is identical for the
already-accepted `fingerprint.ko`).

Reports: `phase4-microarray-fp-tee-reconstruction.md`,
`phase4-microarray-fp-tee-abi-provenance.md`,
`phase4-microarray-fp-tee-behavior.md`,
`phase4-microarray-fp-tee-source-candidates.md`,
`phase4-microarray-fp-tee-RED.md`.

## Phase 4 spi-mt65xx provider closure (2026-09-13)

`spi-mt65xx` is `DIRECT_SOURCE_MATCH / FROZEN FOR RE`. Pinned Nothing MT6878
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f` reproduces all
31 stock function bytes/KCFI IDs, 65 imports, 66 MODVERSIONs, 545 relocations,
and all three natural export CRCs. The only whole-file differences are
vermagic/build-ID/source-path provenance. The sole stock consumer is
`microarray_fp_tee`; rebuilding its frozen source against the real provider
symvers preserves 27/27 functions, exact depends, and 66/66 edges, upgrading
the two SPI witnesses to `NATURAL_SPI_PROVIDER`. Exact-GKI build is clean and
`kernel/scripts/phase4_spi_mt65xx_verify.py` passes 82/82. Runtime `tkcore`
remains stock. See `phase4-spi-mt65xx-reconstruction.md`.

## Phase 4 fingerprint provider closure

`fingerprint` is `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE` and FROZEN FOR RE.
The stock-oracle source reproduces 16/16 function bytes, sizes and KCFI IDs,
18/18 kernel imports/MODVERSIONs, all 10 export CRCs, and the four exact CRCs
recorded by the stock MicroArray oracle. Exact-GKI build succeeds with zero
compiler/modpost warnings and zero unresolved symbols; the fail-closed verifier
passes 39/39. The provider is removed from the RE queue.

At the time of this provider-only milestone, the MicroArray sensor was
untouched. **Superseding current status:** MicroArray is now behaviorally
source-reconstructed/frozen and `spi-mt65xx` is a direct source match;
TrustKernel `tkcore` alone remains not reconstructed and required at runtime.

## Phase 4 sc851x_charger update (2026-09-08)

`sc851x_charger` is complete at `SOURCE_RECONSTRUCTED`. No public source donor
was found; mandatory no-public-source RED recovered the 11 functions, all 50
register fields, 35 required DT writes, sysfs/IRQ/PM/shutdown behavior and the
kernel-only ABI. Exact-GKI build returns 0 with zero warnings and unresolved
symbols. Function sizes/KCFI IDs, data, strings, all 30 MODVERSION records and
relocation target/type sequences match stock; 8/9 behavioral functions are
byte-identical and the inlined probe's compiler-local text delta is reported.

Hardware identity is SC8510 at `6-0069`: the DT `@6f` suffix is stale while
`reg=<0x69>` and the live device agree. The module is a converter
configuration/debug/IRQ shim, not charger policy. uSmart control/VBUS instead
maps to `extcon-mtk-usb`, MT6375 `usb-otg-vbus`, and the shared
USB0 / MTU3 / USB2 fabric; classification
`PROVEN_UNRELATED`, with no stock software support found for charging the phone
through uSmart. Runtime power testing remains intentionally unperformed.

