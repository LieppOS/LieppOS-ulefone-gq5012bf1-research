# Android 17 Slot-B logo-hang second-stage forensics

This pass follows the controlled plain Slot-B reboot which remained at the
graphical logo and exposed no ADB or fastboot transport.

No additional Slot-B boot was performed.

## Contract correction

The Android 17 framework / stock vendor compatibility contract is already
proven compatible by the earlier exact `checkvintf` run.

Important established results:

- stock device target FCM level: 8;
- Android 17 provides an FCM level-8 framework matrix;
- the selected level-8 matrix accepts kernel 6.1;
- stock kernel 6.1.115 plus its captured config passed all applicable kernel
  requirements;
- the Android 17 image contains `com.android.vndk.v34.apex`;
- stock vendor reports `ro.vndk.version=34`;
- the versioned VNDK contract matches;
- the exact prior `checkvintf` run returned `COMPATIBLE`;
- all applicable device-manifest HAL instances were covered.

A later host-side check returning status 70 was a harness error caused by an
unmapped `/apex` path. It is not evidence of a framework/vendor
incompatibility.

Therefore VINTF, VNDK and the kernel FCM are no longer treated as primary
candidates for the Slot-B logo hang.

## New focus

The investigation moves to the normal second-stage boot chain:

    first/second-stage init
        -> vold / shared userdata
        -> apexd activation
        -> linker configuration
        -> zygote
        -> system_server
        -> SurfaceFlinger / boot completion

This directory contains:

- Android 17 boot properties;
- boot-critical init definitions;
- zygote contract;
- APEX activation triggers;
- data/FBE/vold triggers;
- core binary presence;
- persistent logd evidence from shared userdata;
- bootstat state;
- DropBox timeline;
- MediaTek AEE inventory;
- shared APEX state.

All phone access in this pass is read-only from healthy Slot A.

## Machine status

VINTF_AS_PRIMARY_LOGO_HANG_BLOCKER=RULED_OUT
VNDK_AS_PRIMARY_LOGO_HANG_BLOCKER=RULED_OUT
KERNEL_FCM_AS_PRIMARY_LOGO_HANG_BLOCKER=RULED_OUT
NEXT_BOOT_STAGE_FOCUS=SECOND_STAGE_DATA_APEX_ZYGOTE
MISSING_BOOT_CRITICAL_BINARY_COUNT=3
MISSING_BOOT_CRITICAL_BINARY=system/bin/hwservicemanager
MISSING_BOOT_CRITICAL_BINARY=system/bin/vndservicemanager
MISSING_BOOT_CRITICAL_BINARY=system/bin/adbd
FAILED_B_RUNTIME_LOG_STATUS=NO_UNAMBIGUOUS_FAILED_B_RUNTIME_LOG_RECOVERED
STATIC_CORE_BINARY_SET=FAIL

## Recovered runtime evidence

SLOT_B_MARKER=NO
ANDROID17_SDK37_MARKER=NO
APEXD_MARKER=NO
VOLD_MARKER=NO
ZYGOTE_MARKER=NO
SYSTEM_SERVER_MARKER=NO
SURFACEFLINGER_MARKER=NO
FATAL_RUNTIME_MARKER=NO
RUNTIME_EVIDENCE_RESULT=NO_UNAMBIGUOUS_FAILED_B_RUNTIME_LOG_RECOVERED
