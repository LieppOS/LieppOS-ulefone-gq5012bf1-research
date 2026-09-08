# GQ5012BF1 Proprietary Kernel Module Replacement Plan

## Objective

Reduce dependence on stock Ulefone binary kernel modules while preserving a
bootable and debuggable system throughout development.

Current hard ULEFONE_ONLY kernel ABI:

- 17 binary modules
- 304 unique kernel symbol/CRC requirements

Current transitional ULEFONE_ONLY + NEEDS_ULEFONE_PORT ABI:

- 354 unique kernel symbol/CRC requirements

## Priority 1 — yft_gpio_keys

Reasons:

- 65 kernel-facing imports
- 36 currently exclusive KMI requirements
- no observed stock-module consumers of its exports
- conventional GPIO/input/IRQ functionality
- relatively isolated reconstruction target

This should be the first Ulefone-specific module reconstructed from behavior,
DT data and stock binary/API evidence.

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

Treat together:

- hynitron
- spi_tiny_co5300_lcd

hynitron is a module-ABI provider for another stock module, therefore the rear
display stack should be migrated as a subsystem rather than independently.

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

- sh366003_fg
- sc8571_charger
- sc851x_charger
- yft_tiny2c_usb
- custom_ldo — reconstructed exactly at the consumer ABI/function level
- custom_ldo_wl2868 — structurally reconstructed; provider residuals remain

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

- leds_ln2403
- custom LDO glue (**completed**; retained here as historical priority)

The custom LDO shim is now reconstructed exactly at the consumer ABI/function
level. `leds_ln2403` remains relatively contained and should follow its
underlying power dependencies.

## Priority 8 — TrustKernel / fingerprint

Treat as one late-stage security subsystem:

- tkcore
- tkcore_drv
- microarray_fp_tee
- fingerprint

This group has high kernel-KMI impact but also the highest likely
reverse-engineering and integration difficulty because it crosses:

- GlobalPlatform TEE interfaces
- TrustKernel-specific behavior
- fingerprint transport/glue
- secure-world interaction

It should not block earlier custom-kernel development.

## Strategy

Development should initially retain the stock Ulefone kernel and progressively
replace vendor modules.

The eventual custom kernel should target Linux 6.1.115 / Android14-11
compatibility and be validated against the stock CONFIG_MODVERSIONS CRC
requirements.

A replacement module is not considered independent merely because its
kernel-facing KMI is known. Module-to-module ABI dependencies must also be
preserved or migrated.

## Phase 4 custom_ldo_wl2868 update (2026-09-08)

`custom_ldo_wl2868` has a raw-I2C structural reconstruction with exact `will_ldo_vout`/`will_ldo_en` export CRCs and a successful exact-GKI build. Subsequent stock `imgsensor` call-site analysis proves the camera voltage value is in microvolts, closing that residual. It is still not promoted to an independently deployable replacement because probe/data-layout and whole-function/source parity residuals remain and no live hardware validation is allowed.

## Phase 4 custom_ldo update (2026-09-08)

`custom_ldo` is complete at `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`. Its two
28-byte forwarding functions are byte-identical to stock; exact KCFI, three
import CRCs, two export CRCs, module dependency metadata, and all relocations
are reproduced. Exact-GKI build succeeds with zero compiler/modpost warnings
and zero unresolved symbols against the reconstructed WL2868 provider's real
`Module.symvers`. Only generated srcversion/vermagic provenance differs. It is
removed from the remaining reverse-engineering queue.

