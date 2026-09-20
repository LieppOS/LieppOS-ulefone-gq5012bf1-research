# V16 modules-ready property reconstruction

Working Slot A maps:

    vendor.all.modules.ready
        u:object_r:vendor_mtk_device_prop:s0

Its compiled vendor policy places `vendor_mtk_device_prop` in:

- property_type
- vendor_property_type
- vendor_restricted_property_type

Therefore the custom policy reconstruction uses:

    vendor_restricted_prop(vendor_mtk_device_prop)

and restores the exact property-context mapping.

This resolves the Stage-2 build failure where `set_prop(init_insmod_sh,
vendor_mtk_device_prop)` referenced an undeclared property type.

PHONE_MODIFIED=0
