# Consumer and camera-power contract

`custom_ldo.ko` is preserved as `workspace/phase4-custom-ldo-wl2868/stock-custom-ldo.ko` and was only statically analyzed. Its two text wrappers pass their incoming registers directly to undefined `will_ldo_vout` and `will_ldo_en`; relocations are `R_AARCH64_CALL26`. The consumer therefore requires the two exported symbols with two integer arguments and integer return values.

Stock dependency chain: `imgsensor.ko` → `custom_ldo.ko` → `custom_ldo_wl2868.ko`. The provider has zero intermodule imports and exports exactly the two symbols. Historical task boundary: no `custom_ldo` rebuild or execution was started during the WL2868 phase.

Subsequent dedicated `custom_ldo` work reconstructed both wrappers byte-identically and traced all four stock `imgsensor` call relocations. The stock Ulefone DT (not a Nothing donor) maps AVDD/DVDD/DOVDD/AFVDD to WL2868 channels for sensor slots 0, 1, 2, and 4. Compiled power sequences pass 1,100,000, 1,200,000, 1,800,000, and 2,800,000 unchanged through the shim. Because the same `ent->val` field is alternatively supplied as `min_uV=max_uV` to stock `regulator_set_voltage`, the public `will_ldo_vout` value unit is now **PROVEN_FROM_STOCK: microvolts**. See `phase4-custom-ldo-imgsensor-consumer-analysis.md` and `phase4-custom-ldo-imgsensor-custom-stages.tsv`.
