# V7 exact MTK late-fs bracket

Static/runtime audit established:

- ro.hardware=mt6878;
- normal init imports init.mt6878.rc;
- /vendor/etc/fstab.mt6878 is the live default device fstab;
- its explicit latemount entry is /data;
- /metadata is first-stage mounted;
- V6 proved main init can observe hwservicemanager.ready=true.

V7 instruments the actual MT6878 late-fs action itself.

Markers:

    v7-mtk-start
    v7-hwsm-ready-passed
    v7-before-mount-all
    v7-after-mount-all
    v7-mtk-complete

This distinguishes:

- an exact MTK hwservicemanager readiness race;
- entry into mount_all --late;
- return from mount_all --late;
- completion of the MTK late-fs action.

SOURCE_SHA256_BEFORE=12b5aed87f03df3226d84c3a545b53b98c23269a5bd8c81408c6616c2676ffbb
SOURCE_SHA256_AFTER=15989f5792ff91a25ba797d4b06441b25af79b2d9a8aa9629eca5a8e853243b5
PHONE_MODIFIED=0
