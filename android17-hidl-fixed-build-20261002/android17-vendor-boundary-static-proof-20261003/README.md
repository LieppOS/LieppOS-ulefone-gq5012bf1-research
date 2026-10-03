# Android 17 / stock-vendor compatibility boundary

This investigation was performed host-side with only read-only
inspection of healthy Slot A.

No Slot-B boot or partition write was performed.

## Static status

    VNDK_V34_PACKAGED=NO
    PREVIOUS_VNDK_MISSING_CLASSIFICATION=UNRESOLVED
    SYSTEM_LINKER32=NO
    SYSTEM_LINKER64=NO
    SYSTEM_LIBC32=NO
    SYSTEM_LIBC64=NO
    FRAMEWORK_MATRIX_HAS_KERNEL_6_1=YES
    FRAMEWORK_MATRIX_HAS_KERNEL_6_6=YES
    CHECKVINTF=FAIL_OR_INCOMPLETE
    LIVE_HEALTH_EXAMPLE_PROCESS=YES
    LIVE_VENDOR_HEALTH_PROVIDER_PROVEN=NO
    BASIC_VENDOR_RUNTIME_BRIDGE=INCOMPLETE

## Important correction

The earlier static audit classified com.android.vndk as absent.
The Android 17 image actually packages the versioned compatibility
APEX com.android.vndk.v34 when VNDK_V34_PACKAGED=YES.

Therefore an unversioned com.android.vndk lookup is not a valid
test for the VNDK v34 compatibility runtime.

Health service registration is also not sufficient to prove
vendor-side provider provenance.
