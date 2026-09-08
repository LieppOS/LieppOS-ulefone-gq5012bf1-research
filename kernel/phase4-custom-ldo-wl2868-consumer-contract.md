# Consumer and camera-power contract

`custom_ldo.ko` is preserved as `workspace/phase4-custom-ldo-wl2868/stock-custom-ldo.ko` and was only statically analyzed. Its two text wrappers pass their incoming registers directly to undefined `will_ldo_vout` and `will_ldo_en`; relocations are `R_AARCH64_CALL26`. The consumer therefore requires the two exported symbols with two integer arguments and integer return values.

Stock dependency chain: `imgsensor.ko` → `custom_ldo.ko` → `custom_ldo_wl2868.ko`. The provider has zero intermodule imports and exports exactly the two symbols. No `custom_ldo` rebuild or execution was started, per task boundary.

No local camera sensor power-table source was found. The recovered hardware-facing mapping is therefore limited to LDO1–LDO7, VOUT registers 0x03–0x09, enable bits 0–6, and the camera-driver consumer path. Camera rail names/voltages from unrelated Nothing DT donors are not attributed to this Ulefone stock image.
