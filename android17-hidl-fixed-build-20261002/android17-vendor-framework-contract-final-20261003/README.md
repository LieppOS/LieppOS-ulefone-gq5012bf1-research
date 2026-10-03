# Android 17 framework ↔ stock vendor contract reconciliation

This investigation is host-side plus read-only collection from healthy Slot A.
Slot B was not booted.

The previous static audit incorrectly reported:

    MISSING_CORE_APEX=com.android.vndk

because it checked only the unversioned APEX basename.

The Android 17 system image actually contains a versioned VNDK compatibility
APEX (), so the VNDK contract must be evaluated by
matching its version against the stock vendor's .

This pass also:

- captures the complete live stock vendor/ODM VINTF tree;
- reads the device manifest target FCM level;
- inventories Android 17 framework compatibility matrices;
- determines which matrix level applies to this stock vendor;
- separates irrelevant newer kernel matrix alternatives from the selected FCM;
- executes checkvintf against the Android 17 system/product/system_ext plus the
  stock vendor/ODM VINTF contract;
- preserves the exact tool output.

Final machine status:

OLD_UNVERSIONED_VNDK_MISSING_RESULT=FALSE_POSITIVE
VERSIONED_VNDK_APEX_PRESENT=YES
VNDK_APEX_MATCHES_VENDOR=YES
LIVE_DEVICE_TARGET_LEVEL=8
MATCHING_FRAMEWORK_MATRIX=YES
CHECKVINTF_RC=70
FRAMEWORK_VENDOR_VINTF_COMPATIBILITY=NOT_PROVEN
STATIC_CONTRACT_BLOCKER_FOUND=UNRESOLVED

VNDK:

VERSIONED_VNDK_APEX_PRESENT=YES
VERSIONED_VNDK_APEX_VERSIONS=34
LIVE_RO_VNDK_VERSION=34
VNDK_APEX_MATCHES_VENDOR=YES

FCM:

LIVE_DEVICE_TARGET_LEVEL=8
FRAMEWORK_MATRIX_LEVELS=202404,202504,202604,7,8
MATCHING_FRAMEWORK_MATRIX=YES

Kernel/FCM:

LIVE_DEVICE_TARGET_LEVEL=8
SELECTED_MATRIX_ROWS=1
/mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/system/etc/vintf/compatibility_matrix.8.xml	type=framework	level=8	version=9.0	kernels=5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,5.15.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8,6.1.0@8
SELECTED_FCM_HAS_KERNEL_6_1=YES
SELECTED_FCM_HAS_KERNEL_6_6=NO
