# V7 exact MTK late-fs runtime result

V7 instruments the actual normal-boot MT6878 `on late-fs` action around:

    wait_for_prop hwservicemanager.ready "true"
    mount_all --late

Marker order:

    v7-mtk-start
    v7-hwsm-ready-passed
    v7-before-mount-all
    v7-after-mount-all
    v7-mtk-complete

The raw runtime result is stored in `v7-mtk-latefs-runtime-result.txt`.

PHONE_MODIFIED=0
