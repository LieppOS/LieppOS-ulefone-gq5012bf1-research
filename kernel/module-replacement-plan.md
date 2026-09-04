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
- custom_ldo
- custom_ldo_wl2868

These modules require careful staged testing because failures can affect
charging, battery reporting and power stability.

## Priority 6 — Main panel

Module:

- panel_ky_vtdr6115_dphy_cmd

The module has high immediate KMI reduction potential but display bring-up is
high impact. It should be attempted after a stable kernel/module test workflow
exists.

## Priority 7 — Auxiliary LEDs / regulators

Modules include:

- leds_ln2403
- remaining custom LDO glue

These are relatively contained but should follow reconstruction of their
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

