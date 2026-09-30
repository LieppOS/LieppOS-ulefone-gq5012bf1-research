# MTK recovery AIDL BootControl startup audit

The current OrangeFox recovery overlays the stock fastbootd/Binder/BootControl
client stack, while the device-specific MediaTek recovery AIDL service remains
in the byte-identical stock platform vendor-ramdisk fragment.

Known-good stock service:

    android.hardware.boot.IBootControl/default
    /system/bin/hw/android.hardware.boot-service.mtk_recovery

The service is configured as class `early_hal`.

Current userspace fastbootd reports slot-count=0 and current-slot empty,
which AOSP fastbootd behavior associates with an unavailable BootControl
client/HAL.

This audit resolves the final merged recovery dependency providers, init
startup rules, VINTF declaration, service_contexts and file_contexts before
any recovery image is modified.
