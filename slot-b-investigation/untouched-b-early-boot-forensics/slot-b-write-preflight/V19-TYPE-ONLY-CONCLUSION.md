# V19 property-type-only isolation conclusion

V19 retained:

- V16-exact module-loader/runtime files
- no init_insmod_sh domain
- no init_insmod_sh_exec type
- no init.insmod.sh file-context mapping
- V17/V15-exact vendor_property_contexts
- no vendor.all.modules.ready -> vendor_mtk_device_prop mapping

V19 added only the compiled vendor_mtk_device_prop property type/attributes
relative to the V17 SELinux baseline.

Runtime result:

- v15-mtkgki-early-init remained 0 at its exact seed timestamp
- every other seeded Android-init marker also remained 0
- pstore was empty
- vendor_b remained the exact V19 image
- system_b remained the frozen V12 image
- vbmeta_vendor_b, vbmeta_system_b and root vbmeta_b remained unchanged

Therefore removing the property-context mapping did not restore early init.

The common policy change between failing V18 and V19 is the compiled
vendor_mtk_device_prop type/attributes.

This strongly shifts the investigation from property-context serialization
to the compiled/precompiled SELinux policy itself.

A dummy-type control is required next to distinguish:

1. vendor_mtk_device_prop-specific incompatibility
2. any modification/addition to the vendor precompiled policy

CAPTURE_PHONE_MODIFIED=0
EXPERIMENT_PHONE_MODIFIED=1
