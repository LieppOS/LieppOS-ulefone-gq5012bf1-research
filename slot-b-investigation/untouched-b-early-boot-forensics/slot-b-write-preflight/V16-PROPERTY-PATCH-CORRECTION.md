# V16 property patch correction

The first property-type insertion accidentally wrote a literal `\n` prefix:

    \nvendor_restricted_prop(vendor_mtk_device_prop)

so the source gate correctly rejected it.

It was corrected to:

    vendor_restricted_prop(vendor_mtk_device_prop)

The exact working-A property mapping remains:

    vendor.all.modules.ready u:object_r:vendor_mtk_device_prop:s0

PHONE_MODIFIED=0
