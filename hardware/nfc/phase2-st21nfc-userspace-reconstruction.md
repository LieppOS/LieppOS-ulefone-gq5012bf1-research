# ST21NFC userspace and eSE reconstruction

## Entry conditions

Phase 1 established the physical/runtime NFC topology:

    ST21NFC
        |
        +-- NFCEE 0x81 -- UICC
        +-- NFCEE 0x82 -- embedded Secure Element

NFCEE 0x81 is slot-independent: switching the active physical SIM from SIM1
to SIM2 changes the MediaTek Secure Element terminal but leaves the ST21 NFCEE
identifier unchanged.

The embedded SE exists as a real runtime NFCEE but stock Android does not
expose ISecureElement/ESE1 through OMAPI.

The remaining work therefore moves into the ST vendor userspace stack.

## Vendor HAL evidence

`nfc_nci.st21nfc.st.so` contains explicit internal state for:

    mActiveHciNfceeBitmap

    mDataHciHotPlugNtfEse
    mDataHciHotPlugNtfSim

    mDataHciRspHostListESe
    mDataHciRspHostListSim
    mDataHciRspHostListFull
    mDataHciRspHostListNone

    mRfNfceeDiscoveryReqNtfEse
    mRfNfceeDiscoveryReqNtfSim

    mNfceeDiscoverNtf81
    mNfceeDiscoverNtf86

and exports/references:

    i2cNfccMayUseEse()
    hal_wrapper_nfceeModeSetSent()

This proves that the vendor HAL contains explicit HCI/NFCEE logic for SIM and
eSE handling rather than acting only as a transparent NCI transport.

The service binary also consumes:

    OFF_HOST_ESE_PIPE_ID
    OFF_HOST_SIM_PIPE_ID
    OFFHOST_ROUTE_ESE
    OFFHOST_ROUTE_UICC

## APDU caution

The library contains multiple APDU-related state-machine strings, including
raw APDU transmission and loader authentication/erase/get-ATR commands.

These currently appear associated at least partly with the NFCC firmware
download/factory-loader engine.

They must not yet be interpreted as proof of a generic AP-to-eSE APDU API.

The reconstruction must distinguish:

    NFCC loader APDU path

from:

    eSE application APDU path

## Stock NFC SELinux bug

A separate stock-ROM bug is now proven.

`/data/nfc` is labeled:

    u:object_r:system_data_file:s0

while the NFC domain has the required create/read/write permissions for:

    u:object_r:nfc_data_file:s0

In permissive mode the NFC framework can create/write its files and emits AVC
records marked permissive=1.

In enforcing mode access to:

    /data/nfc/nfaStorage.bin1

is denied and:

    nfa_nv_co_write: fail to open, error = 13

is emitted.

The device contains no `/data/nfc` file-context mapping.

The LieppOS fix is expected to include:

    /data/nfc(/.*)?    u:object_r:nfc_data_file:s0

plus restoration of the context on an existing data partition.

## Current reconstruction frontier

1. verify the nfc_data_file relabel fixes NFC persistence under enforcing mode;
2. recover the HAL functions implementing HCI host-list processing;
3. recover SIM/eSE hotplug notification handling;
4. recover mActiveHciNfceeBitmap semantics;
5. recover NFCEE mode-set interception/state transitions;
6. determine the purpose of the hard-coded 0x81 and 0x86 NFCEE records;
7. identify construction/use of the configured eSE static HCI pipe 0x5E;
8. distinguish loader APDU transport from eSE APDU transport;
9. inspect the Android NFC APEX for any surviving NfcAdapterExtras/eSE bridge;
10. reconstruct a controlled LieppOS interface to NFCEE 0x82 if no framework
    interface survives.

The primary target is now the ST HAL's HCI/eSE state machine rather than
further physical NFC enumeration.

## Persistent-storage issue resolved

The `/data/nfc` issue is no longer an open reconstruction item.

Temporary correction:

    chcon -R u:object_r:nfc_data_file:s0 /data/nfc

was tested with SELinux enforcing.

After an NFC disable/enable cycle there were no further:

    nfa_nv_co_write EACCES failures
    NfcEventLog write failures
    NFC-related AVC denials

The permanent LieppOS fix is therefore a file-context mapping for `/data/nfc`
to `nfc_data_file`, plus restoration of the correct context for existing data
partitions.

This item is PROVEN and can be removed from the active investigation frontier.

## ROM implementation note

The proven `/data/nfc` SELinux correction is tracked as an implementation item
in:

    hardware/nfc/ROM-FIX.md

The research phase should retain the evidence and behavior analysis, while
device-tree / ROM changes belong in that file.

## T4T NDEF NFCEE capability — supported but stock-disabled

Static reconstruction now shows a complete T4T NDEF NFCEE implementation
across both the ST vendor HAL and the Android NFC APEX.

The ST HAL contains hard-coded NFCEE discovery templates:

    NFCEE_DISCOVER_RSP:
        42 00 02 00 03

which advertises three NFCEEs in this alternate topology.

Templates include:

    NFCEE 0x81
        HOST_ID 0x02
        UICC

    NFCEE 0x86
        HOST_ID 0xC0

    NFCEE 0x10
        NFCEE protocol APDU
        NDEF_STORAGE information TLV

The NFCEE 0x10 template is:

    62 00 0e 10 01 01 00 01 04 06 00 20 00 00 3b 01 00

Decoded:

    ID            0x10
    initial state disabled
    protocol      APDU
    info TLV      NDEF_STORAGE

The ST HAL also contains a dedicated:

    mRfNfceeDiscoveryReqNtfNdefNfcee

template referencing NFCEE 0x10.

The Android NFC APEX native library contains the full T4T NFCEE
implementation, including:

    NFA_T4tNfcEeOpenConnection
    NFA_T4tNfcEeRead
    NFA_T4tNfcEeWrite
    NFA_T4tNfcEeClear
    NFA_T4tNfcEeIsEmulationSupported
    NativeT4tNfcee
    RW_T4tNfcee*
    CE_T4tRegisterAID

The Java NFC package also contains:

    IT4tNdefNfcee
    T4tNdefNfceeService
    NdefNfceeService

Stock ST HAL runtime configuration currently reports:

    NDEF_NFCEE_ENABLE=0

Therefore current classification is:

    vendor capability        PROVEN PRESENT
    Android native support   PROVEN PRESENT
    Android Java support     PROVEN PRESENT
    stock configuration      DISABLED
    runtime activation       NOT YET PROVEN

This must not yet be promoted to ROM-FIX.md until enabling the feature produces
runtime NFCEE 0x10 and successful Type-4 NDEF operation.

## Runtime T4T NFCEE activation and Android vendor-config collision

### Stage A: ST-side NDEF NFCEE activation — PROVEN

A temporary runtime override changed:

    /vendor/etc/libnfc-hal-st.conf

from:

    NDEF_NFCEE_ENABLE=0

to:

    NDEF_NFCEE_ENABLE=1

After restarting the ST NFC HAL, runtime NFCEE discovery changed from two
NFCEEs to three:

    Tx 22 00 00

    Rx 42 00 02 00 03

    Rx 62 00 08 81 01 00 01 03 01 02 00
    Rx 62 00 08 82 01 00 01 03 01 c0 01
    Rx 62 00 0e 10 01 01 00 01 04 06 00 20 00 00 3b 01 00

This proves that NFCEE 0x10 is not merely a dormant static packet template.
The ST vendor HAL exposes it at runtime when NDEF_NFCEE_ENABLE is enabled.

NFCEE 0x10 advertises:

    NFCEE ID       0x10
    state          disabled
    protocol       APDU
    info TLV       NDEF_STORAGE

The Android NFC stack then logged:

    nfa_ee_nci_disc_ntf:
    NDEF-NFCEE not config but enabled in FW, discard data

Therefore:

    ST NDEF-NFCEE runtime support       PROVEN
    NFCEE 0x10 runtime exposure         PROVEN
    Android acceptance of NFCEE 0x10    STOCK-DISABLED

The Android stack replaces/discards the unconfigured NFCEE and later exposes
an invalid internal NFCEE slot 0xFF / handle 0x04FF.

---

### Active Android NFC configuration file — PROVEN

Runtime ConfigFile logging proves that the NFC Mainline stack parses:

    /vendor/etc/libnfc-nci.conf

not the APEX copy at:

    /apex/com.android.nfcservices/etc/libnfc-nci.conf

The stock vendor configuration contains:

    NFA_STORAGE="/data/nfc"
    NFA_MAX_EE_SUPPORTED=0x05

but does not contain a textual:

    T4T_NFCEE_ENABLE

---

### T4T_NFCEE_ENABLE is supplied through the vendor-config merge path

A test manually added:

    T4T_NFCEE_ENABLE=1

to the active:

    /vendor/etc/libnfc-nci.conf

The NFC application immediately entered a SIGABRT restart loop with:

    ConfigFile - [T4T_NFCEE_ENABLE] = 1
    config.cc:118] Check failed: !hasKey(key)

Backtrace:

    ConfigFile::addConfig()
    NfcConfig::loadConfig()
    NfcConfig::getInstance()
    NfcConfig::getUnsigned()
    RoutingManager::RoutingManager()
    JNI_OnLoad
    NativeNfcManager
    NfcService

Static disassembly of the installed libnfc_nci_jni.so reconstructs the
relevant NfcConfig::loadConfig() sequence:

    ConfigFile::parseFromFile(...)
        |
        v
    NfcAdaptation::GetInstance()
        |
        v
    NfcAdaptation::GetVendorConfigs(map)
        |
        v
    iterate vendor-config map
        |
        v
    ConfigFile::addConfig(key, value)

ConfigFile::addConfig() rejects duplicate keys with a fatal CHECK.

Since stock operation does not crash, but adding textual
T4T_NFCEE_ENABLE causes the vendor-config merge to hit the duplicate-key
CHECK, T4T_NFCEE_ENABLE is already supplied through the vendor configuration
path rather than needing to be added to libnfc-nci.conf.

Therefore the correct future activation target is the source of the
vendor/AIDL NfcConfig value, not a duplicate text entry.

DO NOT implement:

    T4T_NFCEE_ENABLE=1

directly in /vendor/etc/libnfc-nci.conf on this software stack.

Next target:

    NfcAdaptation::GetVendorConfigs()
        -> NFC HAL getConfig()
        -> android.hardware.nfc.NfcConfig
        -> t4tNfceeEnable

The value and its ST HAL source must be reconstructed before another runtime
activation test.

---

### Unexpected reboot during experiment — unrelated SIM reboot request

During the duplicate-key NFC crash loop the device rebooted.

Persistent pstore proves this was an orderly reboot requested by system_server:

    Received sys.powerctl='reboot,SIM is added.'
    Got shutdown_command 'reboot,SIM is added.'
    Reboot start, reason: reboot,SIM is added.
    reboot: Restarting system with command 'SIM is added.'

At the same time, com.android.nfc was repeatedly aborting and restarting.

The reboot must therefore NOT be documented as an NFC-triggered kernel panic,
watchdog reset, or T4T hardware failure.

Classification:

    NFC userspace crash loop            PROVEN
    kernel panic                        NO
    watchdog-triggered reboot           NOT INDICATED
    reboot requester                    system_server
    reboot reason                       "SIM is added."
    causal connection to NFC test       NOT PROVEN

After the reboot all temporary NFC bind mounts were removed and normal stock
NFC operation returned.


## Android Mainline T4T gate source — AIDL NfcConfig

Static reconstruction of the installed NFC Mainline library now identifies the
source of the Android-side T4T_NFCEE_ENABLE configuration.

The installed NfcConfig::loadConfig() performs:

    ConfigFile::parseFromFile(...)
        |
        v
    NfcAdaptation::GetInstance()
        |
        v
    NfcAdaptation::GetVendorConfigs(configMap)
        |
        v
    iterate configMap
        |
        v
    ConfigFile::addConfig(key, value)

The corresponding AOSP NfcAdaptation implementation for the AIDL NFC HAL does:

    mAidlHal->getConfig(&aidlConfigValue)

and then inserts:

    NAME_T4T_NFCEE_ENABLE
        =
    aidlConfigValue.t4tNfceeEnable ? 1 : 0

into the vendor configuration map.

Therefore T4T_NFCEE_ENABLE is not intended to be manually duplicated in:

    /vendor/etc/libnfc-nci.conf

On this device, adding it there produced:

    ConfigFile::addConfig()
    Check failed: !hasKey(key)

and a com.android.nfc SIGABRT restart loop.

The correct activation path is:

    NFC HAL AIDL NfcConfig
        |
        +-- t4tNfceeEnable
                  |
                  v
    NfcAdaptation::GetVendorConfigs()
                  |
                  v
    T4T_NFCEE_ENABLE
                  |
                  v
    Android T4T NFCEE subsystem

Next target:

    exact device implementation of StNfc_hal_getConfig()

We need to determine whether the May-2024 ST HAL:

    * explicitly sets t4tNfceeEnable=false,
    * leaves the later-added field at its default false value,
    * or derives it from some existing ST configuration parameter.

Do not add T4T_NFCEE_ENABLE directly to libnfc-nci.conf.


### Location of ST AIDL getConfig implementation

Binary inspection clarified the division between the ST NFC service and the
ST NCI shared library.

`nfc_nci.st21nfc.st.so` exports the ST configuration parser/helpers including:

    CNfcConfig::GetInstance()
    CNfcConfig::getValue(...)
    GetNumValue
    GetByteArrayValue

but it does not export:

    StNfc_hal_getConfig

The stripped service executable:

    android.hardware.nfc-service-st

contains the strings:

    getConfig
    StNfc_hal_getConfig

This matches the ST reference build architecture in which hal_st21nfc.cc is
compiled directly into android.hardware.nfc-service.st while the ST NCI library
is a shared dependency.

Therefore the exact device implementation of StNfc_hal_getConfig must be
reconstructed from:

    blobs/android.hardware.nfc-service-st

rather than:

    blobs/nfc_nci.st21nfc.st.so

This is important for the T4T NFCEE compatibility investigation because
StNfc_hal_getConfig produces the AIDL android.hardware.nfc.NfcConfig object
that NfcAdaptation::GetVendorConfigs() converts into Android Mainline
configuration keys.

Current hypothesis:

    older ST HAL NfcConfig
        -> no t4tNfceeEnable field
        -> newer client defaults field to false
        -> T4T_NFCEE_ENABLE=0

This hypothesis still requires exact AIDL interface-version and service-binary
verification.


### AIDL V1 / Mainline T4T version skew — PROVEN

Runtime Binder interrogation of:

    android.hardware.nfc.INfc/default

returned:

    getInterfaceVersion() = 1

The interface hash is:

    73acf94ceb90a5d5736bc6b37dc703a6ad5fb5e0

The ST service executable dynamically links:

    android.hardware.nfc-V1-ndk.so
    nfc_nci.st21nfc.st.so

and imports the ST configuration helpers:

    GetNumValue
    GetByteArrayValue

Therefore the Ulefone/ST NFC HAL is a frozen AIDL V1 HAL.

The frozen NFC V1 NfcConfig predates the later T4T NFCEE field:

    t4tNfceeEnable

Modern Android NFC Mainline uses:

    NfcAdaptation::GetVendorConfigs()

to convert:

    aidlConfigValue.t4tNfceeEnable

into:

    T4T_NFCEE_ENABLE

The resulting compatibility path is therefore:

    ST AIDL V1 HAL
        |
        | old NfcConfig parcel
        | no t4tNfceeEnable
        v
    newer Android NFC Mainline
        |
        | missing appended field defaults false
        v
    T4T_NFCEE_ENABLE=0
        |
        v
    T4T NDEF NFCEE disabled in Android

This explains the runtime Stage-A result:

    ST NDEF_NFCEE_ENABLE=1
        -> NFCEE 0x10 exposed

while Android reports:

    NDEF-NFCEE not config but enabled in FW, discard data

It also explains why manually adding:

    T4T_NFCEE_ENABLE=1

to /vendor/etc/libnfc-nci.conf is incorrect: NfcConfig::loadConfig() later
merges the vendor/AIDL configuration map and attempts to insert the same
T4T_NFCEE_ENABLE key, causing ConfigFile::addConfig() to abort on a duplicate.

Likely LieppOS fix direction:

    provide an Android/Mainline compatibility override for T4T_NFCEE_ENABLE
    when using this ST AIDL V1 HAL

rather than adding a duplicate textual key or blindly modifying the old
vendor parcelable.

Exact implementation remains to be runtime-proven.


### Exact ST getConfig reconstruction — bridge is missing

The exact GQ5012BF1 android.hardware.nfc-service-st implementation of
StNfc_hal_getConfig() was reconstructed from the stripped ARM64 binary.

Function:

    start: 0x6dc0
    return: 0x720c

The function first zero-initializes the returned NfcConfig object:

    [config + 0x00 .. config + 0x60] = 0

and then populates the AIDL V1 configuration using ST GetNumValue() and
GetByteArrayValue() helpers.

Recovered configuration map:

    0x6e4c  CE_ON_SWITCH_OFF_STATE
    0x6e78  POLL_BAIL_OUT_MODE
    0x6ea0  ISO_DEP_MAX_TRANSCEIVE
    0x6ec0  DEFAULT_OFFHOST_ROUTE
    0x6ee0  DEFAULT_NFCF_ROUTE
    0x6f00  DEFAULT_SYS_CODE_ROUTE
    0x6f20  DEFAULT_SYS_CODE_PWR_STATE
    0x6f40  DEFAULT_ROUTE

    0x6f64  DEVICE_HOST_ALLOW_LIST
    0x6f80  DEVICE_HOST_WHITE_LIST (fallback)

    0x6ffc  OFF_HOST_ESE_PIPE_ID
    0x701c  OFF_HOST_SIM_PIPE_ID
    0x7040  NFA_PROPRIETARY_CFG
    0x7088  PRESENCE_CHECK_ALGORITHM
    0x70a8  STNFC_USB_CHARGING_MODE

    0x70e4  OFFHOST_ROUTE_UICC
    0x7160  OFFHOST_ROUTE_ESE

    0x71dc  DEFAULT_ISODEP_ROUTE

Critically, the service executable contains no configuration-string lookup
for either:

    NDEF_NFCEE_ENABLE
    T4T_NFCEE_ENABLE

NDEF_NFCEE_ENABLE exists in nfc_nci.st21nfc.st.so and is consumed by the
older ST vendor path, but StNfc_hal_getConfig() does not export or bridge it
into the AIDL NfcConfig returned to Android.

Therefore the exact compatibility gap is now proven:

    libnfc-hal-st.conf:
        NDEF_NFCEE_ENABLE
                |
                v
        ST vendor HAL / NFCC
                |
                +---- NFCEE 0x10 can be enabled

    StNfc_hal_getConfig()
                |
                X  no bridge
                |
                v
        AIDL V1 NfcConfig
                |
                v
        modern Android NFC Mainline
                |
                +---- t4tNfceeEnable defaults false
                |
                v
        T4T_NFCEE_ENABLE=0

This explains the runtime message:

    NDEF-NFCEE not config but enabled in FW, discard data

when only the ST-side NDEF_NFCEE_ENABLE switch is enabled.

This is not merely a missing text configuration entry. It is a version-skew
integration defect between the old ST AIDL V1 HAL and the newer Android NFC
Mainline T4T-NFCEE implementation.


### Exact Mainline T4T gate and patch point — PROVEN

The installed libnfc_nci_jni.so provides definitive binary proof of how the
old ST AIDL V1 HAL disables the newer Android T4T NFCEE feature.

NfcAdaptation::GetVendorConfigs():

    0x1dbf18 .. 0x1dd1a4

zero-initializes the extended AIDL NfcConfig storage before calling the vendor
NFC HAL.

The AIDL getConfig call receives its output into the stack-backed NfcConfig
object. Because the GQ5012BF1 ST HAL is frozen AIDL V1, it does not provide
the later-added t4tNfceeEnable member.

The exact Android-side T4T conversion is:

    0x1dc734  ldrb w1, [sp, #0x200]
    0x1dc738  add  x0, sp, #0xe0
    0x1dc73c  ConfigValue::ConfigValue(unsigned int)

followed immediately by construction/insertion of:

    T4T_NFCEE_ENABLE

whose string is referenced at:

    0x1dc754 / 0x1dc758
    string address 0x74baf

Therefore:

    [sp + 0x200] = effective aidlConfigValue.t4tNfceeEnable

and on the ST AIDL V1 implementation it remains zero.

Exact compatibility failure:

    ST HAL AIDL V1
        -> no t4tNfceeEnable field
        -> extended field remains zero
        -> GetVendorConfigs()
        -> T4T_NFCEE_ENABLE=0
        -> Android rejects runtime NFCEE 0x10

A minimal experimental Mainline patch point is therefore:

    0x1dc734

Original:

    ldrb w1, [sp, #0x200]

Experimental replacement:

    mov w1, #1

This forces only the T4T_NFCEE_ENABLE ConfigValue produced by
GetVendorConfigs() and does not add a duplicate textual configuration key.

This one-instruction patch is an experimental compatibility shim, not yet a
permanent LieppOS ROM fix. Runtime acceptance of NFCEE 0x10 must be proven
first.


### Exact T4T NDEF NFCEE Binder API — PROVEN

Decompilation of the exact installed com.android.nfc APK reconstructs the
Android API exposed for NFCEE 0x10.

INfcAdapter exposes:

    getT4tNdefNfceeInterface()

which returns:

    android.nfc.IT4tNdefNfcee

The device implementation is:

    NfcService.T4tNdefNfceeService

and implements:

    int writeData(int fileId, byte[] data)
    byte[] readData(int fileId)
    T4tNdefNfceeCcFileInfo readCcfile()
    int clearNdefData()
    boolean isNdefOperationOngoing()
    boolean isNdefNfceeEmulationSupported()

All methods enforce NFC admin permissions.

File IDs supplied to readData()/writeData() are converted to two-byte
big-endian values using:

    ByteBuffer.allocate(2)
    ByteBuffer.putShort((short) fileId)

and passed to the native T4T NFCEE implementation.

readCcfile() parses a minimum 15-byte Type-4 CC file:

    bytes 0..1    CCLEN
    byte  2       mapping version
    bytes 9..10   NDEF file ID
    bytes 11..12  maximum NDEF file size
    byte  13      read access; 0 = allowed
    byte  14      write access; 0 = allowed

The implementation accepts mapping version:

    0x20 = NFC Forum Type-4 Mapping 2.0

Native backend methods are:

    doReadData()
    doWriteData()
    doClearNdefData()
    isNdefOperationOngoing()
    isNdefNfceeEmulationSupported()

Runtime invocation remains to be validated.

