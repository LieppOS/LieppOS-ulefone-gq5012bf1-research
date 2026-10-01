# Android 17 HIDL runtime — lunch combo discovery failure

The HIDL device.mk modification exists, but the Android 17 source tree uses
the three-part lunch syntax:

<product>-<release>-<variant>

The old combo:

lineage_gq5012bf1-userdebug

was rejected by lunch.

Automatic discovery did not find a valid lineage_gq5012bf1 three-part combo.

No build was started.
No device was accessed.
