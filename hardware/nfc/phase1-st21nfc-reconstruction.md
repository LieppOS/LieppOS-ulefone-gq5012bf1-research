# Phase 1 — ST21NFC reconstruction

## Current reconstruction frontier

The basic ST21NFC platform capability work is now substantially established:

    Android HCE             proven
    NFC-A/B host routing    proven
    HCE-F framework         proven
    UICC SE services        proven
    SIM1 default route      configured
    screen-off CE           configured
    switch-off CE           configured
    ST SWP/RF debug hooks   present
    MIFARE protocol mapping present

The remaining NFC work is primarily in runtime NFCEE mapping and ST proprietary/off-host behavior:

1. capture the live `NFCEE_DISCOVER_RSP/NTF` sequence and map every NFCEE ID;
2. determine what `0x83` represents and reconcile it with the vendor comment that names UICC2 as `0x85`;
3. prove whether the configured `0x82` eSE route corresponds to a physically present and accessible eSE;
4. dump and characterize the Secure Element / OMAPI reader topology for SIM1 and SIM2;
5. exercise NFC-F/HCE-F with a controlled `HostNfcFService` test application;
6. test screen-off host/off-host behavior separately;
7. test switch-off card emulation with a known controlled UICC/off-host application if one is available;
8. enable/capture ST RF and SWP firmware traces and decode the proprietary events;
9. reconstruct the semantics of the `UICC CONFIG` and `SE CONFIG` `NCI_DIRECT_CTRL` blobs in `st21nfc_conf.txt`;
10. identify the exact ST21 silicon/firmware variant from a reliable chip/firmware response rather than filename inference;
11. determine whether ST proprietary MIFARE card-emulation support is exposed through SWP/SE, NCI vendor commands, or another internal API;
12. determine which low-level card-emulation parameters are controller-controlled versus Android-host-controlled;
13. document the limits of ordinary Android HCE separately from any lower-level ST21 capability;
14. build a small LieppOS NFC diagnostics tool that can dump routing, NFCEE state, firmware information and test HCE/HCE-F without depending on third-party apps.

The hardest remaining item is the off-host/NFCEE reconstruction because the vendor configuration contains multiple static route IDs but the actual runtime mapping must be proven from NCI discovery and SWP behavior rather than inferred from comments.

## Immediate priority

Before modifying the NFC stack, capture the runtime NFCEE table.

Target evidence:

```text
NFCEE ID -> endpoint type -> protocol(s) -> power/link state -> Android SE service
```

Desired result example only:

```text
0x00 -> Device Host
0x81 -> UICC/SIM1
0x82 -> eSE or other endpoint
0x83 -> unknown endpoint
0x85 -> possible UICC/SIM2
```

Do not assign those labels until they are observed.

## Safe implementation order

1. capture current stock behavior;
2. decode NCI/NFCEE discovery;
3. map Secure Element services to NFCEE IDs;
4. test standard HCE/HCE-F;
5. enable vendor tracing;
6. decode proprietary UICC/SE configuration;
7. only then consider vendor-stack patches or direct NCI experiments.

## Runtime Secure Element update

Secure Element runtime enumeration is now partially solved.

Observed:

    SIM1    mIsConnected=true
    SIM2    mIsConnected=false

This establishes that Android exposes both MediaTek UICC Secure Element
terminals and that SIM1 is currently the active/connected terminal.

The vendor NFC configuration routes the default AID, ISO-DEP, NFC-F and generic
off-host traffic to NFCEE ID 0x81, documented by the vendor file as UICC1.
This makes 0x81 -> SIM1 highly likely, but it is not yet considered fully
proven until the ST21 NFCEE discovery sequence is captured directly.

The unresolved UICC route list remains:

    OFFHOST_ROUTE_UICC={81,83}

despite configuration comments describing UICC2 as 0x85.

## Current reconstruction frontier

The Android-facing ST21NFC card-emulation capability is now substantially
mapped:

    NFC-A/B HCE                  proven
    NFC-F/HCE-F                  advertised and enabled
    UICC Secure Element API      proven
    SIM1 SE connection           proven active
    SIM2 SE terminal             proven, currently disconnected
    screen-off CE                enabled
    switch-off CE                enabled
    UICC/SWP configuration       present
    ST proprietary MIFARE path   present
    ST21 kernel IRQ              proven as IRQ 47

The remaining NFC work is primarily below the Android framework layer:

1. capture the actual NCI NFCEE_DISCOVER response/notifications;
2. map runtime NFCEE IDs to SIM1, SIM2 and any eSE;
3. resolve the unexplained OFFHOST_ROUTE_UICC={81,83} mapping;
4. determine whether a physically usable eSE exists or only configuration
   support is present;
5. decode ST proprietary UICC and SE NCI_DIRECT_CTRL configuration records;
6. determine the exact meaning of the MtkUiccSEHal threadLoop result=-1;
7. capture SWP state transitions with SIM insertion/removal and NFC activity;
8. identify the limits of host-controlled versus SWP/off-host card emulation;
9. determine whether ST proprietary MIFARE card-emulation functionality can be
   reached from LieppOS;
10. reconstruct any useful vendor NFC HAL extensions needed for low-level
    card-emulation experiments.

The highest-priority remaining item is runtime NFCEE discovery because it will
replace configuration-based assumptions with direct controller evidence and
will establish the real SIM1/SIM2/eSE routing topology.

## Runtime Secure Element update

Secure Element runtime enumeration is now partially solved.

Observed:

    SIM1    mIsConnected=true
    SIM2    mIsConnected=false

This establishes that Android exposes both MediaTek UICC Secure Element
terminals and that SIM1 is currently the active/connected terminal.

The vendor NFC configuration routes the default AID, ISO-DEP, NFC-F and generic
off-host traffic to NFCEE ID 0x81, documented by the vendor file as UICC1.
This makes 0x81 -> SIM1 highly likely, but it is not yet considered fully
proven until the ST21 NFCEE discovery sequence is captured directly.

The unresolved UICC route list remains:

    OFFHOST_ROUTE_UICC={81,83}

despite configuration comments describing UICC2 as 0x85.

## Current reconstruction frontier

The Android-facing ST21NFC card-emulation capability is now substantially
mapped:

    NFC-A/B HCE                  proven
    NFC-F/HCE-F                  advertised and enabled
    UICC Secure Element API      proven
    SIM1 SE connection           proven active
    SIM2 SE terminal             proven, currently disconnected
    screen-off CE                enabled
    switch-off CE                enabled
    UICC/SWP configuration       present
    ST proprietary MIFARE path   present
    ST21 kernel IRQ              proven as IRQ 47

The remaining NFC work is primarily below the Android framework layer:

1. capture the actual NCI NFCEE_DISCOVER response/notifications;
2. map runtime NFCEE IDs to SIM1, SIM2 and any eSE;
3. resolve the unexplained OFFHOST_ROUTE_UICC={81,83} mapping;
4. determine whether a physically usable eSE exists or only configuration
   support is present;
5. decode ST proprietary UICC and SE NCI_DIRECT_CTRL configuration records;
6. determine the exact meaning of the MtkUiccSEHal threadLoop result=-1;
7. capture SWP state transitions with SIM insertion/removal and NFC activity;
8. identify the limits of host-controlled versus SWP/off-host card emulation;
9. determine whether ST proprietary MIFARE card-emulation functionality can be
   reached from LieppOS;
10. reconstruct any useful vendor NFC HAL extensions needed for low-level
    card-emulation experiments.

The highest-priority remaining item is runtime NFCEE discovery because it will
replace configuration-based assumptions with direct controller evidence and
will establish the real SIM1/SIM2/eSE routing topology.

## Secondary-UICC experiment result

Repeating NFCEE discovery under the SIM2 test configuration produced no third
NFCEE.

The controller still exposes exactly:

    0x81    UICC host
    0x82    eSE

NFCEE 0x83 remains absent.

The previous candidate mapping 0x83 -> SIM2/UICC2 is therefore no longer the
leading explanation.

The current priority is to determine whether NFCEE 0x81 is a generic,
slot-independent UICC route multiplexed by the MediaTek modem/UICC layer.

Required proof:

1. capture `dumpsys secure_element` with SIM2 active;
2. verify SIM1/SIM2 connection-state transition;
3. correlate that transition with the unchanged ST21 NFCEE 0x81;
4. determine where slot selection occurs below the NFC/NCI layer;
5. only then assign semantics to the dormant OFFHOST_ROUTE_UICC ID 0x83.

## UICC slot-multiplexing solved

The slot-specific UICC question is now substantially solved.

Observed sequence:

    SIM1 active:
        SIM1 connected
        SIM2 disconnected
        ST21 NFCEE 0x81 = UICC

    SIM2 active:
        SIM1 disconnected
        SIM2 connected
        ST21 NFCEE 0x81 = UICC

The ST21 NFCEE identifier does not change when the active physical SIM slot
changes.

Therefore NFCEE 0x81 is a slot-independent logical UICC endpoint and physical
SIM selection occurs below the ST21/NCI layer.

The remaining 0x83 question is now narrower:

1. install two valid SIMs simultaneously;
2. repeat NFCEE discovery;
3. determine whether a third NFCEE appears;
4. if 0x83 appears, map it to the second simultaneous UICC;
5. if 0x83 remains absent, treat it as dormant/generic vendor configuration;
6. identify the MediaTek component responsible for selecting the physical SIM
   behind logical NFCEE 0x81;
7. inspect the meaning of ro.vendor.mtk_uicc_clf=1;
8. reconstruct any modem/UICC/SWP switching interface relevant to LieppOS.

The logical UICC NFCEE mapping itself is no longer an open question:

    0x81 = UICC
    0x82 = eSE

## eSE exposure boundary established

The runtime-discovered embedded Secure Element at NFCEE 0x82 is not exposed
through Android's standard OMAPI Secure Element HAL.

Observed Android feature set:

    android.hardware.se.omapi.uicc

No corresponding:

    android.hardware.se.omapi.ese

is advertised.

Runtime Secure Element HAL instances are limited to:

    ISecureElement/SIM1
    ISecureElement/SIM2

and the active DSDS VINTF manifests likewise declare only SIM1 and SIM2.

No direct eSE device node or dedicated AP-side eSE HAL was found. The only
relevant NFC character device is:

    /dev/st21nfc

Therefore the current architecture is:

    Android HCE
        |
        +-- Device Host

    Android OMAPI
        |
        +-- SIM1
        +-- SIM2

    ST21NFC
        |
        +-- NFCEE 0x81 -- UICC
        +-- NFCEE 0x82 -- eSE

The eSE exists physically/runtime-visible to the NFC controller but is not
directly exposed as an Android OMAPI terminal.

The leading path for LieppOS is therefore reconstruction of the ST21 HCI/NCI
off-host eSE access mechanism, including the configured static eSE pipe 0x5E.

The next work items are:

1. inspect nfc_nci.st21nfc.st.so;
2. inspect android.hardware.nfc-service-st;
3. inspect the installed com.android.nfc implementation;
4. determine whether an NFC Extras/eSE execution path survives in vendor code;
5. if absent, reconstruct the required HCI/eSE bridge for LieppOS;
6. separately resolve the /data/nfc persistent-storage EACCES condition.

## NFC persistent-storage labeling investigation

The stock NFC framework is configured with:

    NFA_STORAGE=/data/nfc

Runtime state:

    /data/nfc
        owner:   nfc:nfc
        mode:    0770
        context: u:object_r:system_data_file:s0

    com.android.nfc
        uid:     nfc
        context: u:r:nfc:s0

Despite correct Unix ownership, NFC initialization repeatedly reports:

    nfa_nv_co_write: fail to open, error = 13

and the Java NFC event logger reports:

    Failed to create directory for /data/nfc/event_log.binpb.new

No /data/nfc file-context mapping exists in the installed device policy.
`restorecon -nRFv /data/nfc` therefore proposes no relabel.

The only NFC-related /data entry found in vendor_file_contexts is:

    /data/nfc_socket(/.*)? -> nfc_socket_file

This strongly suggests that the stock image is missing the expected
/data/nfc -> nfc_data_file labeling rule.

This is not yet marked fully proven until the failures are compared under
temporary SELinux permissive mode and/or with a temporary nfc_data_file label.

The issue is particularly relevant because NFA HCI persistent state is written
through the failing nfa_nv_co_write path.
