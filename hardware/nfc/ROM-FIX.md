# LieppOS NFC ROM fixes — GQ5012BF1

This file tracks changes that should be implemented in the LieppOS device
tree / ROM rather than merely recorded as hardware research findings.

---

## FIX-001: Correct `/data/nfc` SELinux context

**Status:** PROVEN  
**Component:** NFC / SELinux / persistent storage  
**Priority:** High

### Problem

The stock ROM creates:

    /data/nfc

with:

    owner:   nfc:nfc
    mode:    0770
    context: u:object_r:system_data_file:s0

The Android NFC process runs in:

    u:r:nfc:s0

The installed SELinux policy already defines:

    nfc_data_file

and grants the `nfc` domain the required create/read/write/open/unlink
permissions for files and directories of that type.

However, the shipped file-context policy contains no mapping for `/data/nfc`.

The NFC stack is configured with:

    NFA_STORAGE=/data/nfc

As a result, enforcing SELinux blocks NFC persistent storage.

Observed failures included:

    avc: denied { open }
        path="/data/nfc/nfaStorage.bin1"
        scontext=u:r:nfc:s0
        tcontext=u:object_r:system_data_file:s0

    nfa_nv_co_write: fail to open, error = 13

and:

    NfcEventLog:
        Failed to create directory for /data/nfc/event_log.binpb.new

### Runtime proof

Temporary correction:

    chcon -R u:object_r:nfc_data_file:s0 /data/nfc

was tested with SELinux remaining in enforcing mode.

After an NFC disable/enable cycle, the previous:

    nfa_nv_co_write EACCES failures
    NfcEventLog write failures
    NFC-related AVC denials

disappeared.

The NFC stack then successfully created and used:

    /data/nfc/nfaStorage.bin1
        owner:   nfc:nfc
        mode:    0600
        context: nfc_data_file
        size:    238 bytes

    /data/nfc/event_log.binpb
        owner:   nfc:nfc
        mode:    0600
        context: nfc_data_file
        size:    ~1.4 KiB

    /data/nfc/param/
        context: nfc_data_file

Therefore the SELinux labeling error and its correction are proven.

## Required ROM change

Add a persistent SELinux file-context rule:

    /data/nfc(/.*)?    u:object_r:nfc_data_file:s0

Do **not** add a broad new SELinux `allow` rule.

The platform policy already contains the required permissions:

    nfc -> nfc_data_file

The defect is the missing filesystem label, not missing NFC-domain access
permissions.

## Existing-data migration

A dirty-flash / upgrade may already contain `/data/nfc` and its files with the
old `system_data_file` context.

LieppOS therefore also needs to relabel existing contents, for example during
an appropriate early boot / data-migration stage:

    restorecon_recursive /data/nfc

Exact placement of that command should follow the final device-tree/init
layout.

A clean installation should receive the correct context automatically once the
file-context rule is present.

## Verification

After implementing the ROM fix:

    adb shell 'su -c "ls -ldZ /data/nfc"'

must show:

    u:object_r:nfc_data_file:s0

Then cycle NFC:

    adb shell 'su -c "logcat -b all -c"'
    adb shell cmd nfc disable-nfc
    sleep 2
    adb shell cmd nfc enable-nfc
    sleep 3

and verify:

    adb shell 'su -c "logcat -b all -d | grep -iE \
    \"nfa_nv_co_write|NfcEventLog|avc:.*denied.*nfc|/data/nfc\""'

Expected result:

- no `nfa_nv_co_write ... error = 13`
- no `NfcEventLog` create/write failure
- no `/data/nfc` AVC denial

Finally verify:

    adb shell 'su -c "
    find /data/nfc -maxdepth 2 -exec ls -ldZ {} \;
    "'

Expected persistent files include:

    /data/nfc/nfaStorage.bin1
    /data/nfc/event_log.binpb

with `nfc_data_file` contexts.

## Notes

This fix is relevant beyond the event log.

`nfaStorage.bin1` is NFC/NFA persistent state, so leaving the stock SELinux
failure unfixed can prevent parts of the NFC stack from preserving state across
initialization/restarts.

---


## FIX-002: Bridge ST AIDL V1 HAL to Android T4T NDEF NFCEE

Status: PROVEN
Priority: Medium / feature enablement

### Problem

The GQ5012BF1 ships an ST21NFC HAL using frozen NFC AIDL interface version 1.

The ST vendor stack supports:

    NDEF_NFCEE_ENABLE

and when enabled exposes runtime NFCEE:

    NFCEE ID: 0x10
    protocol: APDU
    info TLV: NDEF_STORAGE

However android.hardware.nfc-service-st uses an old AIDL V1 NfcConfig layout
and its StNfc_hal_getConfig() does not export either:

    NDEF_NFCEE_ENABLE
    T4T_NFCEE_ENABLE

Modern Android NFC Mainline expects:

    NfcConfig.t4tNfceeEnable

and converts it into:

    T4T_NFCEE_ENABLE

Because the old HAL cannot provide that later-added field, Mainline sees it
as false and stock Android discards otherwise-working NFCEE 0x10:

    NDEF-NFCEE not config but enabled in FW, discard data

### Incorrect workaround

DO NOT add:

    T4T_NFCEE_ENABLE=1

to:

    /vendor/etc/libnfc-nci.conf

NfcConfig::loadConfig() parses the text file and later merges the same key
from NfcAdaptation::GetVendorConfigs(). A duplicate key causes:

    ConfigFile::addConfig()
    Check failed: !hasKey(key)

and com.android.nfc enters a SIGABRT restart loop.

### Runtime-proven compatibility fix

Two gates are required.

ST side:

    /vendor/etc/libnfc-hal-st.conf

    NDEF_NFCEE_ENABLE=1

Android Mainline side:

The installed libnfc_nci_jni.so reads the effective newer AIDL field at:

    NfcAdaptation::GetVendorConfigs()
    0x1dc734:
        ldrb w1, [sp, #0x200]

and immediately converts it into the ConfigValue for:

    T4T_NFCEE_ENABLE

A one-instruction experimental patch:

    original:
        ldrb w1, [sp, #0x200]

    test replacement:
        mov w1, #1

was used to emulate the missing AIDL field.

Only four bytes were modified.

### Runtime proof

With both gates enabled:

    NfcRoutingOptionManager:
        mNdefNfceeRoute=0x10

    NdefNfceeService:
        registered as "Embedded tag"

    AID:
        D2760000850101
        route=NDEF-NFCEE

    libnfc_nci:
        nfa_t4tnfcee_init
        nfa_t4tnfcee_sys_enable

NFCEE discovery:

    Tx 22 00 00
    Rx 42 00 02 00 03

    Rx 62 00 08 81 ...
    Rx 62 00 08 82 ...
    Rx 62 00 0e 10 01 01 00 01 04 06 00 20 00 00 3b 01 00

Android then enables NFCEE 0x10:

    Tx 22 01 02 10 01
    Rx 42 01 01 00

Runtime state:

    NFCEE ID: 0x10
    status: 0x00 ENABLED
    handle: 0x0410

Routing:

    techA=0x04
    techB=0x04

and:

    AID D2760000850101
    route=NDEF-NFCEE
    power=0x3F

The previous:

    NDEF-NFCEE not config but enabled in FW, discard data

path is no longer taken.

### Permanent LieppOS implementation

Do not ship the binary instruction patch.

Implement a device-specific compatibility bridge in the Android NFC
Mainline source for this old ST AIDL V1 HAL.

Conceptually:

    if (GQ5012BF1 old ST NFC HAL) {
        T4T_NFCEE_ENABLE = 1;
    }

The override must happen in the vendor-config/AIDL merge path, not by adding
a duplicate T4T_NFCEE_ENABLE entry to libnfc-nci.conf.

Also ship:

    NDEF_NFCEE_ENABLE=1

in the ST HAL configuration.

The permanent source implementation should be scoped to the affected device
or HAL fingerprint so unrelated NFC HALs are not changed.

### Still to validate

The following are NOT yet proven:

    actual RF Type-4 NDEF emulation with an external reader
    NDEF read from NFCEE 0x10
    NDEF write/update into NFCEE 0x10
    persistence of NDEF data across NFC restart / reboot


#### Additional Stage-C routing proof

With the compatibility bridge active, `dumpsys nfc` reports:

    NdefNfceeService
        Description: Embedded tag
        Off-host SE: NDEF-NFCEE

    AID D2760000850101
        routed to NFCEE 0x10

and the native routing table contains:

    AID_D2760000850101
        NFCEE_ID = 0x10
        Power State = 0x3B
        Exact match

Thus Android's normal card-emulation routing layer accepts and installs the
embedded Type-4 NDEF target after applying FIX-002.


#### Runtime storage-access proof

FIX-002 was additionally validated by invoking the Android
IT4tNdefNfcee API.

The controller reports:

    T4T NDEF emulation supported: true

and its Type-4 CC file was successfully read through NFCEE 0x10.

Live CC information:

    CCLEN       = 15
    version     = 0x20
    NDEF file   = 0xE104
    max size    = 8192 bytes
    read access = allowed
    write access = allowed

The native stack opened an NFCEE logical connection, selected the Type-4
application and CC file, read the file, delivered
NFA_T4TNFCEE_READ_CC_DATA_CPLT_EVT, and closed the logical connection.

Thus FIX-002 restores not only discovery/routing of NFCEE 0x10 but actual
Android access to its Type-4 storage.


#### Runtime NDEF write/read proof

With FIX-002 active, NFCEE 0x10 accepted a controlled 23-byte NDEF record.

The native write state machine completed through:

    RW_T4tNfceeUpdateNlen
    RW_T4tNfceeStartUpdateFile
    RW_T4tNfceeUpdateFile
    RW_T4tNfceeUpdateNlen
    NFA_T4TNFCEE_WRITE_CPLT_EVT

A subsequent operation opened a new NFCEE logical connection and read:

    NLEN = 0x0017

followed by exactly 23 bytes of NDEF data.

The returned bytes matched the written record exactly.

Therefore FIX-002 enables functional read/write access to the controller
resident Type-4 NDEF store, not merely NFCEE discovery and routing.


#### External RF Type-4 emulation proof

With FIX-002 active and NDEF NFCEE 0x10 enabled, an independent
ST25R3916B + ESP32 reader successfully activated the phone as:

    ISO14443A
    ATQA 04 00
    SAK 20
    ISO-DEP
    NFC Forum Type-4 Tag

The external reader detected an 8192-byte writable NDEF area and read the
exact 23-byte NDEF message previously written through the Android
IT4tNdefNfcee interface:

    D1 01 13 54 02 65 6E
    4C 69 65 70 70 4F 53 20
    54 34 54 20 74 65 73 74

which decodes to:

    LieppOS T4T test

This proves FIX-002 is sufficient not only for Android-side NFCEE storage
access, but for end-to-end external NFC-A / ISO-DEP / Type-4 NDEF card
emulation over RF.


#### Full-reboot persistence proof

NFCEE 0x10 NDEF storage has now been proven persistent across a complete
phone reboot.

After reboot the stock configuration and stock NFC JNI were restored,
confirming that the temporary compatibility setup had disappeared.

The T4T compatibility bridge and NDEF_NFCEE_ENABLE=1 were then restored
without performing any NDEF write.

An independent ST25R3916B reader subsequently read the exact same
23-byte NDEF payload that had been written before reboot.

Therefore FIX-002 exposes persistent NFCEE Type-4 NDEF storage rather than
transient NFC-process memory.

#### Bidirectional external RF Type-4 proof

With FIX-002 active, NFCEE 0x10 is not only accessible from Android; it is
also externally readable and writable over ISO-DEP Type-4 RF.

A ST25R3916 external writer successfully completed the Type-4 write sequence:

~~~text
BeginWriteMessage / NLEN=0       ERR_NONE
WriteBytes payload @ offset 2    ERR_NONE
EndWriteMessage / final NLEN     ERR_NONE
~~~

The externally written 23-byte NDEF Text record contained:

~~~text
LieppOS RF proof
~~~

External RF readback returned the same bytes.

Without performing an Android-side write, Android subsequently read file
0xE104 using IT4tNdefNfcee.readData() and returned the exact same 23-byte
NDEF message.

Therefore FIX-002 enables a fully functional bidirectional embedded Type-4
NDEF endpoint:

~~~text
Android
   <->
NFCEE 0x10 / E104
   <->
external ISO-DEP Type-4 reader/writer
~~~

#### Interrupted external write robustness finding

The Type-4 write implementation follows:

~~~text
1. NLEN = 0
2. write payload
3. NLEN = final message length
~~~

A controlled RF write that returned ERR_TIMEOUT left the NDEF file with
effective NLEN=0.

Android independently reported:

~~~text
nfa_t4tnfcee_get_len: No Data to Read
~~~

and an external ST25 profile repeatedly reported:

~~~text
NDEF state: INITIALIZED
Writable: YES
NDEF message length: 0
NDEF area length: 8192
NDEF mapping version: 2.0
~~~

The Type-4 application, CC file, E104 file, and write capability remained
functional.

This is a robustness concern for interrupted external writes, not a failure
of FIX-002 itself.

#### Final controlled external-write proof

A manually gated ST25R3916 test removed the remaining post-upload auto-run
ambiguity.

The externally observed NDEF changed in one monitored transaction from:

~~~text
LieppOS RF proof
~~~

to:

~~~text
LieppOS RF final
~~~

All three Type-4 write phases returned ERR_NONE, external RF readback returned
the new payload, and Android subsequently returned the exact same 23 bytes via
IT4tNdefNfcee.readData(0xE104).

Therefore the complete path:

~~~text
Android <-> NFCEE 0x10 / E104 <-> external ISO-DEP Type-4 reader/writer
~~~

is end-to-end runtime proven with a controlled OLD -> NEW external mutation.
