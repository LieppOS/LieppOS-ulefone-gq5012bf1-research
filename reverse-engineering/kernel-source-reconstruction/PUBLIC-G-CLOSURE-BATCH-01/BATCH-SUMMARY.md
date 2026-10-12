# PUBLIC-G-CLOSURE-BATCH-01 — empty manifest

**Result:** zero eligible identities. The manifest is frozen with a header and no rows (sha256
`531834a19449ef0e0f24f821f9b43302f38cb066c53a245e5c82e0fc2b8c908b`). No source was modified, no audit delta was
produced, and canonical was not touched.

## Baseline

Canonical `4e47a5b9` (after DISPLAY-INTEGRATION-01): A420 B1 C11 D3 G23 = 421/458. All 23 G identities are in
`G-ELIGIBILITY.tsv`, keyed by module_id and stock sha256.

## Ownership

- Codex `codex/g-source-recovery-batch-02` (`128677b6`, manifest `6f78615b…`, frozen 2026-10-12 23:13) owns 12:
  - **board_io:** extdev_io_class, rt5133-regulator, spi-mt65xx, leds-rgb-aw2013, yft_gpio_keys;
  - **camera_aux:** aw36515, aw36518, aw36518_v2, camera_eeprom_v4l2;
  - **biometric_transport:** fingerprint, microarray_fp_tee, tkcore_drv.
- All three priority candidates (`extdev_io_class`, `rt5133-regulator`, `spi-mt65xx`) are therefore Codex's and are
  excluded.
- Other branches (`codex/all-c-to-a-closure`, `codex/usb-typec-closure`, `codex/next-dg-source-batch`,
  `codex/audio-dependencies-batch-02`) are merged into master and idle.

## The 11 unowned G rows have no authentic public source

Each row was checked against its historical package and source-candidate notes, plus one new bounded search for
SC8571.

| Finding | Modules |
|---|---|
| NO_PUBLIC_DONOR_FOUND | custom-ldo, leds-ln2403, panel-ky-vtdr6115-dphy-cmd, sc851x_charger, sh366003_fg, spi_tiny_co5300_lcd, yft_tiny2c_usb, yft_tpd_gesture |
| STRUCTURAL_DONORS_ONLY | custom-ldo-wl2868: Sony, OnePlus, MiCode and Motorola WL286x drivers have a different ABI |
| PUBLIC_FAMILY_DONOR_PLUS_FIRMWARE_BOUNDARY | hynitron: the build needs CST firmware arrays extracted from the stock binary |
| PUBLIC_DIFFERENT_CHIP_TEMPLATE_ONLY | sc8571_charger: the SouthChip SC8541 LKML template plus an OPLUS register map; there is no public text for the 14 stock-only `mtk_sc8571_*` operations |

All 11 historical sources are stock-oracle reconstructions:

- they were written from disassembly and stock `.data` (panel command tables, timings, register maps);
- several have byte-level `#line` anchors;
- several have recorded function residuals: VTDR6115 20/24, SH366003 38/39, CO5300 24/25, tiny2c 11/12.

Promoting them would certify reconstruction of stock bytes, not recovered source. That is outside this stage's
mandate, which is authentic public source, and against the rule not to fabricate source parity. They stay G and
are carried into OEM-SOURCE-GAP-CLOSURE-01 as `MISSING_SOURCE_IMPLEMENTATION` source-request items.

## New search evidence (2026-10-12)

The four web queries were:

- `"sc-cp-standalone" sc8571 charger_class`
- `"SC SC8571 Driver" southchip`
- `"Aiden-yu@southchip.com" sc8571_charger.c`
- `sc8571_charger.c mediatek "charger_device_register" southchip github`

They returned only:

- the SC8541 LKML/LWN posting (2025-10-13, wangwenqiang, verified on Qualcomm QCS615), already the historical
  template;
- SouthChip product and datasheet pages;
- unrelated bq2560x and charger_class sources.

No MTK SC8571 driver text was found.
