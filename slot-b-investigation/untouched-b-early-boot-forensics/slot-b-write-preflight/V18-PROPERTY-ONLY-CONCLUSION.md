# V18 property-only isolation conclusion

V18 retained the V16 module-loader/runtime files while adding only the
vendor_mtk_device_prop property type and the vendor.all.modules.ready
property-context mapping. It deliberately contained no init_insmod_sh
domain, no init_insmod_sh_exec type, and no init.insmod.sh file-context
mapping.

V18 boot attempt result:

- all seeded markers remained value 0
- all marker mtimes remained exactly:
  2026-09-21 13:53:28.204000219 +0300
- this includes v15-mtkgki-early-init
- pstore was empty
- vendor_b remained the exact V18 image
- frozen V12 system_b remained unchanged
- vbmeta_vendor_b, vbmeta_system_b, and root vbmeta_b remained unchanged

V17, with V15-exact SELinux policy and V16-exact runtime files, had reached
v15-mtkgki-early-init and progressed deep into post-fs-data.

Therefore the V18 experiment strongly narrows the V16 pre-early-init
regression to the vendor_mtk_device_prop property-policy half.

V18 still changed two coupled pieces:
1. declaration/attributes of vendor_mtk_device_prop in compiled SELinux policy
2. mapping vendor.all.modules.ready to that type in vendor_property_contexts

V19 separates those by retaining the type declaration while removing the
property-context mapping.

PHONE_MODIFIED=0
