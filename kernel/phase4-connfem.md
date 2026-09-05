# Phase 4 — connfem

## Initial stock classification

Stock module:

`vendor_dlkm/lib/modules/connfem.ko`

SHA256:

`6373afa19d09289400c8a1ae3ab8bf1edb1ba354fa92d16003285e4b79771710`

Metadata:

- name: `connfem`
- license: GPL
- description: `Connsys FEM (Front-End-Module) Driver`
- authors:
  - Dennis Lin <dennis.lin@mediatek.com>
  - Brad Chou <brad.chou@mediatek.com>

Module parameters:

- `hw_name`
- `config_file`
- `hwid`
- `epa_elna_hwid`
- `connfem_major`

The stock module has no vendor-module dependencies. Its imports are entirely
kernel/GKI interfaces such as OF/device-tree, pinctrl, GPIO, IIO, firmware
loading, character-device and memory/string APIs.

Stock exports eight public ConnFem interfaces:

- `connfem_epaelna_get_bt_fem_info`
- `connfem_epaelna_get_fem_info`
- `connfem_epaelna_get_flags`
- `connfem_epaelna_get_pin_info`
- `connfem_epaelna_laa_get_pin_info`
- `connfem_is_available`
- `connfem_sku_data`
- `connfem_sku_flag_u8`

NothingOSS MT6878 contains the complete MediaTek source tree under:

`kernel_modules/connectivity/connfem/`

including API, configuration, container, DT parsing, ePA/eLNA, SKU, Bluetooth
and Wi-Fi subsystem support.

NothingOSS also contains:

`device_modules/arch/arm64/boot/dts/mediatek/cust_mt6878_connfem.dtsi`

The stock binary's function and string surface includes the same major
MediaTek ConnFem concepts:

- SKU parsing
- ePA/eLNA
- FEM info/layout
- truth tables
- Wi-Fi and Bluetooth flags
- LAA pins
- pinctrl/GPIO
- IIO/PMIC HWID probing
- firmware/config-file loading
- DT parsing
- character-device ioctl interface

No Ulefone-specific implementation has yet been identified.

Initial classification:

`LIKELY_DIRECT_SOURCE_MATCH`

Next:

1. compare donor build/config matrix;
2. compare export and function-name surfaces;
3. build NothingOSS connfem unchanged against exact GKI 12901745;
4. compare imports, MODVERSIONs, functions, sections and `.text` against stock;
5. only consider reconstruction if a real binary/source delta remains.

## Donor revision mismatch discovered

The initial NothingOSS MT6878 ConnFem tree is not an exact source revision
match for the Ulefone stock module.

Stock exports eight ConnFem APIs, while the NothingOSS donor exports six.

Stock-only exports:

- `connfem_sku_data`
- `connfem_sku_flag_u8`

Stock also contains a substantial SKU implementation family that is absent
from the initial NothingOSS function surface, including:

- `cfm_dt_sku_parse`
- `cfm_dt_sku_data_reset`
- `cfm_sku_generic_layout_hdl`
- `cfm_sku_fem_layout_populate`
- `cfm_sku_fem_ctrl_pin_populate`
- `cfm_sku_fem_info_populate`
- `cfm_sku_fem_ttbl_populate`
- `cfm_sku_fem_ttbl_usg_populate`
- `cfm_sku_ttbl_usg_hdl`
- `cfm_sku_prop_val_get`
- `cfm_sku_data_dump`

Therefore the previous `LIKELY_DIRECT_SOURCE_MATCH` classification is
superseded.

Current classification:

`SOURCE_REVISION_MISMATCH / STOCK_HAS_NEWER_SKU_FRAMEWORK`

It is not yet known whether this is a generic later MediaTek ConnFem revision
or a Ulefone-specific fork.

The module remains attractive for reconstruction because it has no external
vendor-module dependencies; all stock imports are kernel/GKI interfaces.

Next step:

Search all available MediaTek/public vendor source trees and git refs for the
two stock-only exports and distinctive `cfm_sku_*` functions before beginning
binary reconstruction.

## Public SKU source search exhausted

The stock-only ConnFem SKU subsystem was searched across the locally available
kernel/vendor reference trees.

Search roots:

- `$BASE/kernel-research`
- `$HOME/kernel-work/vendor-reference`

No source matches were found for:

- `connfem_sku_data`
- `connfem_sku_flag_u8`
- `cfm_sku_generic_layout_hdl`
- `cfm_sku_fem_ttbl_populate`
- `cfm_cfg_copy_sku_hdl`
- `cfm_sku_data_dump`
- `cfm_sku_fem_layout_populate`
- `cfm_sku_fem_ctrl_pin_populate`
- `cfm_sku_ttbl_usg_hdl`
- `cfm_sku_prop_val_get`
- `cfm_dt_sku_parse`

Every locally available NothingOSS git revision was also searched.

The local NothingOSS kernel_modules repository contains only one available
commit/ref:

`5f75a3b13e8135d45b4b0b70ec893345144f70df`

The donor contains effectively no SKU/truth-table subsystem.

Exact public-web symbol searches also produced no indexed source copy.

Therefore ConnFem is now classified as:

`PUBLIC_OLDER_BASE + UNPUBLISHED_OR_UNLOCATED_NEWER_SKU_SUBSYSTEM`

Reverse engineering/reconstruction is justified, but should be limited to the
stock revision delta and SKU layer rather than recreating the entire driver.

Next:

Codex targeted reconstruction using the NothingOSS source as donor and stock
`connfem.ko` as binary oracle.

## Superseded by final reconstruction report

This file records the original ConnFem source-discovery and revision-mismatch
investigation.

Its intermediate classifications are historical and must not be treated as the
current integration verdict.

Authoritative current report:

    kernel/phase4-connfem-reconstruction.md

Final classification:

    STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION

The final investigation additionally proved that the stock GQ5012BF1 runtime
does not enter its `epa-elna-mtk` subtree because `connfem_internal` is absent.
Stock `cfm_dt_epa_parse()` therefore returns `-EINVAL`, leaving the ConnFem
platform device unbound while retaining the character-device context.

Keep this file as provenance for donor discovery and the original SKU revision
mismatch only.
