# Android 17 zygote / hwservicemanager / adbd resolution

The previous second-stage static audit reported three missing boot-critical
binaries solely because it checked fixed paths under `/system/bin`:

- hwservicemanager
- vndservicemanager
- adbd

That classification required correction before treating those absences as a
boot blocker.

This pass:

- searches the complete built partition tree for the binaries;
- resolves the actual executable referenced by each critical init service;
- checks whether vndservicemanager is even defined as a service;
- verifies the modular com.android.adbd APEX contract;
- locates every ro.zygote property source in the exact Android 17 build;
- checks the dynamic zygote init import;
- verifies that the selected zygote rc file exists;
- compares the result with healthy Slot-A runtime properties.

Machine result:

STATIC_RO_ZYGOTE_FOUND=NO
LIVE_A_RO_ZYGOTE_FOUND=YES
ZYGOTE_DYNAMIC_IMPORT_PRESENT=YES
ZYGOTE_SELECTED_RC_RESOLVES=YES
ZYGOTE_CHAIN_STATUS=PROPERTY_SOURCE_OUTSIDE_SCANNED_SYSTEM_PROPS
HWSERVICEMANAGER_BINARY_FOUND=YES
HWSERVICEMANAGER_SERVICE_RESOLVES=NO
VNDSERVICEMANAGER_SERVICE_DEFINED=NO
VNDSERVICEMANAGER_BINARY_FOUND=NO
ADBD_APEX_PRESENT=YES
ADBD_MODULE_CONTRACT_FOUND=YES
OLD_SYSTEM_BIN_MISSING_CLASSIFIER=NOT_FULLY_CLEARED
NEXT_FOCUS=RESOLVE_CRITICAL_SERVICE_EXEC_PATH

No Slot-B boot was performed.

All phone access was read-only from healthy Slot A.
