# V17 policy-off isolation conclusion

V17 was constructed with:

- vendor SELinux artifacts byte-identical to V15
- module-loader/runtime files byte-identical to V16
- frozen V12 system_b unchanged
- root vbmeta_b and vbmeta_system_b unchanged

V16 had left every seeded Android-init marker at zero.

V17 produced fresh:

    v15-mtkgki-early-init=1
    v15-after-ready-zero=1
    v15-after-insmod-start=1

and later progressed through:

    v9-system-pfsd-start
    v10-before-keymaster
    v10-after-keymaster
    v9-keymaster-passed
    v9-before-apex-wait
    v9-apex-activated
    v9-derive-sdk-passed
    v9-init-user0-passed
    v9-restorecon-data-passed
    v9-derive-classpath-passed
    v9-art-boot-passed
    v9-before-odsign-key
    v9-odsign-key-done
    v9-snapshotde-passed
    v8-mtk-pfsd-start

V17 then retained:

    v15-insmod-running=0
    v15-insmod-stopped=0
    v8-modules-ready-passed=0

Therefore the V17 control strongly isolates the V16 SELinux payload, or
filesystem labeling induced by that payload, as the cause of the new
pre-early-init regression.

Separately, V17 reproduces the previously established MTK modules-ready
producer failure when the reconstructed init.insmod.sh domain is absent.

Stock Slot-A provenance also showed vendor_init set/read access to
vendor_mtk_device_prop. The V16 reconstruction did not yet reproduce those
vendor_init permissions.

PHONE_MODIFIED=0
