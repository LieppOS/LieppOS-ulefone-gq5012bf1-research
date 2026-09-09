# GQ5012BF1 SC8571 source candidates

## Result

No exact or strong stock-framework source was found locally or in the public
search performed for this reconstruction. The best public material is useful
for SC8571 register names and broad silicon semantics only; it is not a source
match for the Ulefone/MediaTek module.

| candidate | location | classification | basis |
|---|---|---|---|
| GQ5012BF1 stock ELF | `workspace/phase4-sc8571/oracle/sc8571_charger.stock.ko` | **EXACT_SOURCE: no; behavioral oracle only** | 34 functions, regmap/regmap_field, MediaTek `charger_class`, one driver handling both roles |
| LineageOS/OnePlus SM8550 OPLUS SC8571 master | `workspace/phase4-sc8571/source-search/oneplus-sm8550-lineage-22.2/oplus_sc8571_master.c` | **REGISTER_MAP_DONOR** | same silicon; OPLUS PPS framework, raw SMBus, global master singleton, separate source files, no `charger_device_register`, no regmap |
| OPLUS SC8571 slave A/B | adjacent frozen files in the same directory | **REGISTER_MAP_DONOR** | role-specific OPLUS implementation, not the stock master/slave architecture |
| SouthChip SC8571 product page | <https://www.southchip.com/en/product/SC8571> | **REGISTER_MAP_DONOR** | confirms 2-cell switched-capacitor direct-charger product class; no Linux source contract |
| OnePlus/Oppo/realme/MiCode/Motorola/Nothing/Transsion/MediaTek public and local searches | exact-name/function/compatible queries preserved in `workspace/phase4-sc8571/source-search/` | **NO_USEFUL_SOURCE** for exact implementation | no hit for stock-only `mtk_sc8571_*`, `sc8571_charger_match_table`, or exact compatible/framework combination |

## Frozen donor provenance

Upstream branch:

`LineageOS/android_kernel_oneplus_sm8550-modules`, `lineage-22.2`

Raw source base:

`https://raw.githubusercontent.com/LineageOS/android_kernel_oneplus_sm8550-modules/lineage-22.2/oplus/kernel/charger/chargepump_ic/`

| file | bytes | SHA256 |
|---|---:|---|
| `oplus_sc8571_master.c` | 33,859 | `7b56d7cca64a12d32552f9464bb606ce0b08041ef9d938cab0b9a4206db8224b` |
| `oplus_sc8571_slave_a.c` | 17,101 | `b7718ccc890d6209eb560e4796031f39ab5ae196e0023e58c0a564818c610656` |
| `oplus_sc8571_slave_b.c` | 16,960 | `2728b72d7857374560f47be8958300b0ddaf9b052fb2aafb8edcfef45e0445be` |
| `oplus_sc8571.h` | 24,675 | `ef7ba2a559b9a1617a6335c8738f88b1ab485afe8d8d305fdaea02ca6fc0dd3f` |
| `Makefile` | 266 | `6c150ab48dc1340d288076a111818a1efadb815504dc7b5b07dda667aa58c9b6` |

The frozen files are not edited. Reconstruction changes are made in a separate
workspace and are justified by stock ELF evidence, not by OPLUS policy.

## Why the donor is not stock-equivalent

* Stock: one I2C driver and one code path branches through OF match data for
  master/slave. OPLUS: separate master/slave translation units and global role
  singletons.
* Stock imports `charger_device_register` and supplies a 648-byte MediaTek
  `charger_ops`; OPLUS has no `charger_device_register` reference.
* Stock imports regmap initialization, regmap fields, bulk read, power-supply
  registration/change, and PM IRQ helpers. OPLUS master uses SMBus helpers,
  OPLUS PPS globals, debugfs tracking, and OPLUS error upload machinery.
* Only three function names overlap (`sc8571_parse_dt`,
  `sc8571_show_registers`, `sc8571_store_register`): stock has 34 ELF
  functions; the donor master contains 44 detected function definitions.
* Stock-only callback family includes fourteen `mtk_sc8571_*` operations.
* DT property names, GPIO names, charger registration, IRQ semantics, ADC API,
  initialization policy, and shutdown path differ.

## Allowed donor use

Donor register names/formulas may label a field only after stock register-field
entries, disassembly, table data, or transformations independently confirm the
same register and encoding. OPLUS initialization values and PPS state-machine
logic are never adopted as stock defaults.

## Search evidence

* `workspace/phase4-sc8571/source-search/local-hits.txt`
* frozen OPLUS donor directory listed above
* exact web queries: `oplus_sc8571_master.c`, `sc8571_charger
  charger_device_register`, `sc,sc8571-master`, `mtk_sc8571_get_adc_accuracy`,
  `sc8571_charger_match_table`, and `SC8571_ADC_CH`
