# ST21NFC current findings

## Target identity

The device exposes the ST NFC stack through the following live/vendor components:

```text
I2C device/driver: 6-0008 -> st21nfc
NCI HAL module:     nfc_nci.st21nfc
Android NFC HAL:    android.hardware.nfc.INfc/default
Firmware:           /vendor/firmware/st21nfc_fw7.bin
Firmware config:    /vendor/etc/st21nfc_conf.txt
HAL config:         /vendor/etc/libnfc-hal-st.conf
NCI config:         /vendor/etc/libnfc-nci.conf
```

The exact commercial ST21 silicon suffix should remain **UNKNOWN** until it is identified from a reliable runtime/chip-ID source. The current evidence proves the ST21NFC family stack, not necessarily a particular marketing variant.

---

## 1. Android card-emulation capabilities — PROVEN

`pm list features` reports:

```text
feature:android.hardware.nfc
feature:android.hardware.nfc.any
feature:android.hardware.nfc.hce
feature:android.hardware.nfc.hcef
feature:android.hardware.nfc.uicc
```

Therefore the shipped Android framework declares:

- standard Host Card Emulation (HCE);
- NFC-F/FeliCa host card emulation (`hcef`);
- UICC-backed NFC secure-element support.

`dumpsys nfc` also reports:

```text
mState=on
mEnableHostRouting=true
listenTech=0xf
pollTech=0x2f
```

A third-party HCE service was observed registered on the device:

```text
ComponentInfo{com.yuanwofei.cardemulator.pro/com.yuanwofei.cardemulator.CardService}
On Host Service
AID: F0010203040506
Requires Device Unlock: false
Requires Device ScreenOn: false
```

This is direct runtime proof that Android host card emulation is active and applications can register AID-routed services.

---

## 2. Current host routing — PROVEN

The live NFC routing dump contains:

```text
Entry                 NFCEE_ID
Empty_AID              0x00
PROTOCOL_ISO_DEP       0x00
TECHNOLOGY_A           0x00
TECHNOLOGY_B           0x00
```

`NFCEE_ID 0x00` is the Device Host route in the Android/NCI stack. The current table therefore proves active host routing for ISO-DEP and NFC-A/B handling.

At the same time `dumpsys nfc` reports:

```text
Default route: secure element
```

These observations are not contradictory: the default/fallback route can target an off-host secure element while specific AIDs/protocols/technologies are routed to the Device Host.

---

## 3. Host HCE technology mask — PROVEN

Vendor NCI configuration contains:

```text
HOST_LISTEN_TECH_MASK=0x3
```

with the file documenting:

```text
0x01 = NFC Technology A
0x02 = NFC Technology B
```

Therefore host HCE is explicitly configured for NFC-A and NFC-B.

The same configuration enables flexible AID matching:

```text
AID_MATCHING_MODE=0x03
```

and extended ISO-DEP transceive size:

```text
ISO_DEP_MAX_TRANSCEIVE=0xFEFF
```

---

## 4. NFC-F / FeliCa — SUPPORTED and CONFIGURED

Android declares:

```text
feature:android.hardware.nfc.hcef
```

The ST configuration contains FeliCa/T3T routing parameters:

```text
DEFAULT_SYS_CODE={FE:FE}
DEFAULT_SYS_CODE_ROUTE=0x81
DEFAULT_NFCF_ROUTE=0x81
DEFAULT_SYS_CODE_PWR_STATE=0x3B
```

However, the current `dumpsys nfc` snapshot had no registered HCE-F service and an empty HCE-F routing table.

Therefore:

- NFC-F HCE framework support is **PROVEN**;
- an actual working HCE-F transaction on this handset is **NOT YET PROVEN**;
- off-host FeliCa routing is explicitly **CONFIGURED**.

---

## 5. UICC / off-host secure-element routing — strongly PROVEN at stack level

The vendor HAL configuration defines static off-host pipes:

```text
OFF_HOST_ESE_PIPE_ID=0x5E
OFF_HOST_SIM_PIPE_ID=0x3E
```

The default routing policy is configured as:

```text
DEFAULT_SYS_CODE_ROUTE=0x81
DEFAULT_NFCF_ROUTE=0x81
DEFAULT_OFFHOST_ROUTE=0x81
DEFAULT_ROUTE=0x81
DEFAULT_ISODEP_ROUTE=0x81
```

The comments in the shipped file identify:

```text
0x81 = UICC_1
0x85 = UICC_2
0x82 = eSE
0x86 = eUICC/SPI-SE
```

The same file contains:

```text
OFFHOST_ROUTE_UICC={81,83}
OFFHOST_ROUTE_ESE={82}
```

### Important unresolved inconsistency

The file comments describe UICC2 as `0x85`, while the actual `OFFHOST_ROUTE_UICC` list contains `0x83`.

Do **not** label `0x83` as SIM2 until the runtime NFCEE discovery table is captured.

Possible explanations include:

- ST/Ulefone-specific NFCEE assignment;
- firmware-dependent dynamic IDs;
- stale comments in the vendor configuration;
- a different secure-element endpoint.

Runtime services expose:

```text
android.hardware.secure_element.ISecureElement/SIM1
android.hardware.secure_element.ISecureElement/SIM2
android.se.omapi.ISecureElementService
```

This proves Android Secure Element HAL/OMAPI services exist for both SIM slots. It does **not** by itself prove that both slots currently have an active SWP link or provisioned contactless applets.

---

## 6. Screen-off and switch-off card emulation — CONFIGURED

The vendor stack explicitly enables card emulation while the screen is off and while the phone is switched off:

```text
CE_ON_SCREEN_OFF_STATE=1
CE_ON_SWITCH_OFF_STATE=1
SCREEN_OFF_POWER_STATE=1
```

The HAL configuration separately contains:

```text
CE_ON_SWITCH_OFF_STATE=1
```

The NCI configuration also contains:

```text
ALWAYS_ON_SET_EE_POWER_AND_LINK_CONF=0x03
OFFHOST_AID_ROUTE_PWR_STATE=0x3B
```

This is strong evidence that the design intends off-host secure-element transactions to remain available in low-power states.

Actual transaction success with the phone powered off is **NOT YET TESTED**.

---

## 7. UICC listen technologies — CONFIGURED

The NCI configuration contains:

```text
UICC_LISTEN_TECH_MASK=0x07
```

The shipped comments define the default set as NFC-A, NFC-B and NFC-F.

This is consistent with the default UICC route handling ISO-DEP and FeliCa/T3T traffic.

---

## 8. MIFARE support in the ST stack — PROVEN as protocol support, emulation unresolved

The ST proprietary protocol map documents byte 5 as `NCI_PROTOCOL_MIFARE`:

```text
NFA_PROPRIETARY_CFG={05:FF:FF:06:8A:90:77:FF:FF}
```

The MIFARE protocol slot is set to `0x90`, not `0xFF`/unsupported.

The NCI configuration also contains:

```text
LEGACY_MIFARE_READER=0x0
```

Therefore MIFARE protocol support exists in the ST/NCI stack.

This does **NOT** prove any of the following:

- arbitrary MIFARE Classic card cloning;
- programmable fixed UID emulation;
- Android-host MIFARE Classic card emulation;
- access to any ST proprietary MIFARE card-emulation path from ordinary applications.

Those require separate low-level proof.

**Update 2026-10-02 — the emulation question is now split, not unresolved.**
ST documents MIFARE Classic card emulation on this controller family as an
**off-host** feature *"through SWP-CLT"*: the CLF relays listen-direction
14443-A/MIFARE traffic to a secure element, and the emulation state machine plus
MIFARE keys live in the SE. So "no `NFA_CeT2t*` functions" only disproves the
**host** path. Host MIFARE CE: **NOT POSSIBLE (architectural)**. SE-side MIFARE
CE over SWP-CLT: **OPEN** — the transports exist on this board (`0x81`/`0x83`
UICC + `0x82` eSE, `OFF_HOST_ESE_PIPE_ID=0x5E`,
`UICC_LISTEN_TECH_MASK=0x07`), and off-host CE plumbing is already proven by the
runtime-proven T4T-NFCEE emulation; what is missing is an SE-side MIFARE
applet with NXP-provisioned keys plus a technology-level SE listen route
(`seTechMask[0]=0x00` today). Details, per-path verdicts and read-only
experiments: `mifare-ce-offhost-se-path.md`.

---

## 9. ST proprietary firmware configuration — PROVEN

`/vendor/etc/st21nfc_conf.txt` performs a hardware reset and NCI initialization, then writes device-specific proprietary configuration.

Relevant sections include:

```text
REM UICC CONFIG
NCI_DIRECT_CTRL,...

REM SE CONFIG
NCI_DIRECT_CTRL,...

REM IOT CONFIG
NCI_DIRECT_CTRL,...

REM ANTENNA CONFIG
NCI_DIRECT_CTRL,...

REM NFCC CONFIG
NCI_DIRECT_CTRL,...
```

This confirms that UICC/SE behavior is part of the generated hardware configuration, rather than only generic unused comments in the Android config files.

The file also contains custom RF-A/RF-B tuning, DPC configuration and antenna parameters.

---

## 10. SWP/RF debug hooks — PROVEN

The ST HAL configuration contains:

```text
STNFC_FW_DEBUG_ENABLED=1
```

and documents firmware RF/SWP tracing, including:

```text
# use value 5 to enable CLT mode logging -- for debug only.
# STNFC_FW_SWP_LOG_SIZE=30
# STNFC_FW_RF_LOG_SIZE=15
```

This is a useful future reverse-engineering path for mapping runtime secure-element and SWP behavior.

---

## 11. Current capability matrix

| Capability | Current status |
|---|---|
| Android ISO-DEP HCE | **PROVEN** |
| NFC-A host CE | **PROVEN/configured** |
| NFC-B host CE | **PROVEN/configured** |
| NFC-F/FeliCa HCE framework | **PROVEN** |
| NFC-F/FeliCa HCE transaction | **NOT YET TESTED** |
| UICC secure-element Android services | **PROVEN** |
| SIM1 default off-host routing | **STRONGLY CONFIGURED** |
| SIM2 secure-element service | **PROVEN** |
| SIM2 runtime NFC NFCEE ID | **UNKNOWN** |
| eSE route configuration | **PROVEN in config** |
| physical/usable eSE | **UNKNOWN** |
| screen-off card emulation | **CONFIGURED** |
| switched-off card emulation | **CONFIGURED, NOT TESTED** |
| MIFARE protocol support | **PROVEN in ST stack** |
| MIFARE Classic reader (POLL) | **PROVEN** |
| MIFARE card emulation via Android host | **NOT POSSIBLE (architectural)** |
| MIFARE card emulation via SWP-CLT (off-host SE) | **OPEN — needs SE-side applet + MIFARE keys** |
| arbitrary fixed UID emulation | **UNKNOWN below HCE; not provided by normal Android HCE** |
| low-level ST proprietary CE control | **RESEARCH TARGET** |

---

## 12. Architectural model supported by current evidence

```text
                         +--------------------------+
                         | Android application CPU  |
                         |                          |
                         | HostApduService / HCE    |
                         | HostNfcFService / HCE-F  |
                         +------------+-------------+
                                      |
                                      | Device Host / NCI route 0x00
                                      |
External reader <----> ST21NFC / NFCC
                         |
                         +---- SWP/off-host ----> UICC / SIM1
                         |
                         +---- SWP/off-host ----> second SE endpoint (mapping TBD)
                         |
                         +---- eSE route 0x82 configured (physical endpoint TBD)
```

The next major task is to replace the unresolved off-host labels with the actual runtime NFCEE discovery map.

## Secure Element runtime state

Runtime `dumpsys secure_element` now provides direct evidence for the two
MediaTek UICC Secure Element terminals:

    SECURE ELEMENT SERVICE TERMINAL: SIM1
    mIsConnected:true

    SECURE ELEMENT SERVICE TERMINAL: SIM2
    mIsConnected:false

This proves that both SIM1 and SIM2 terminals are instantiated by Android's
Secure Element framework, but only SIM1 is currently connected.

Current interpretation:

    SIM1    Secure Element terminal present and connected
    SIM2    Secure Element terminal present but not connected

This strongly supports the vendor NFC configuration selecting UICC1 as the
default off-host route:

    DEFAULT_SYS_CODE_ROUTE=0x81
    DEFAULT_NFCF_ROUTE=0x81
    DEFAULT_OFFHOST_ROUTE=0x81
    DEFAULT_ROUTE=0x81
    DEFAULT_ISODEP_ROUTE=0x81

However, the runtime NFCEE mapping has still not been captured, so the mapping

    0x81 -> SIM1/UICC1

should remain "strongly supported" rather than "proven from NFCEE discovery".

The vendor configuration also contains:

    OFFHOST_ROUTE_UICC={81,83}

while its comments describe:

    0x81 = UICC_1
    0x85 = UICC_2

The meaning of 0x83 therefore remains unresolved. It may be a runtime-specific
NFCEE assignment, an ST/vendor-specific identifier, or stale configuration
documentation.

## MediaTek UICC Secure Element HAL observations

Runtime logcat repeatedly shows both UICC HAL worker threads:

    MtkUiccSEHal: [se1]operator():1337: threadLoop, result = -1
    MtkUiccSEHal: [se2]operator():1337: threadLoop, result = -1

Do not currently interpret `result = -1` as a confirmed error.

Possible meanings include:

- no pending UICC/SE event;
- timeout/polling return;
- disconnected terminal state;
- lower-layer modem/UICC notification behavior;
- actual communication failure.

This requires either controlled SIM insertion/removal testing or
reverse-engineering of the MtkUiccSEHal implementation before assigning exact
semantics.

Notably, the same `-1` value is emitted for both se1 and se2 even though
`dumpsys secure_element` reports SIM1 connected and SIM2 disconnected, so the
worker-loop return value is clearly not a simple equivalent of
`mIsConnected`.

## Kernel ST21NFC evidence

The ST21NFC device owns a live kernel IRQ entry:

    /proc/irq/47/st21nfc

Therefore the running kernel has an active ST21NFC interrupt handler registered
on IRQ 47.

Combined with the previously proven I2C device:

    6-0008 -> st21nfc

the current kernel-level topology is:

    I2C bus 6
        |
        +-- address 0x08
              |
              +-- st21nfc
                    |
                    +-- IRQ 47

No useful ST21NFC-specific debugfs/proc diagnostics were found beyond the IRQ
entry in the current search.


## ST21NFC interrupt topology update

`/proc/interrupts` provides stronger runtime evidence for the ST21NFC interrupt
path:

    47: 17969 0 0 0 0 0 0 0  mtk-eint  2 Level  st21nfc

This establishes:

    Linux IRQ        47
    IRQ controller   MediaTek EINT
    EINT line        2
    trigger mode     level
    consumer         st21nfc

The non-zero and increasing interrupt count also proves that the registered
ST21NFC interrupt path is actively receiving hardware events.

Current kernel topology:

    MediaTek I2C bus 6
        |
        +-- 0x08 st21nfc
                |
                +-- MediaTek EINT 2
                        |
                        +-- Linux IRQ 47

## Runtime NFCEE mapping solved

A clean `cmd nfc disable-nfc` / `cmd nfc enable-nfc` cycle produced the complete
ST21NFC initialization sequence, including raw NCI NFCEE discovery.

The NFCC reports exactly two NFCEEs:

    Tx 22 00 00
    Rx 42 00 02 00 02

and then advertises:

    Rx 62 00 08 81 01 00 01 03 01 02 00
    Rx 62 00 08 82 01 00 01 03 01 c0 01

Decoded according to the NCI NFCEE_DISCOVER_NTF structure:

    NFCEE 0x81
        status       0x01
        protocols    0
        HOST_ID      0x02
        supply       0x00

    NFCEE 0x82
        status       0x01
        protocols    0
        HOST_ID      0xC0
        supply       0x01

ST's HCI/NCI definitions identify:

    HOST_ID 0x02 = UICC
    HOST_ID 0xC0 = embedded Secure Element (eSE)

Therefore the runtime map is now proven as:

    NFCEE 0x81 -> UICC
    NFCEE 0x82 -> eSE

For the current device state, 0x81 corresponds to the active SIM1/UICC1 path.
`dumpsys secure_element` reports SIM1 connected and SIM2 disconnected, and the
vendor NFC configuration identifies 0x81 as its primary/default UICC route.

The eSE is no longer merely configuration support. NFCEE 0x82 is actually
advertised by the ST21 controller at runtime.

Both NFCEEs are successfully enabled:

    Tx 22 01 02 81 01
    Rx 42 01 01 00

    i2cNfccMayUseEse(1), result = 0
    Tx 22 01 02 82 01
    Rx 42 01 01 00

The explicit eSE arbitration call immediately before activation of NFCEE 0x82
independently reinforces the 0x82 -> eSE mapping.

### Secondary UICC route

The vendor HAL loads:

    OFFHOST_ROUTE_UICC=8183
    OFFHOST_ROUTE_ESE=82

but NFCEE discovery on the current boot reports only 0x81 and 0x82.

No NFCEE 0x83 is currently advertised.

Since SIM2 is also disconnected at the Android Secure Element layer, the
leading hypothesis is now:

    0x81 -> UICC1 / SIM1
    0x82 -> eSE
    0x83 -> probable UICC2 / SIM2 route when available

The 0x83 -> UICC2 association remains unproven until an NFC initialization is
captured with a usable SIM/secure element in slot 2.

Older vendor comments describing UICC2 as 0x85 should therefore be treated as
generic or stale until runtime evidence supports them.

### eUICC distinction

Android emits:

    NfcCardEmulationManager:
        Euicc CardEmulation is not support

The runtime-discovered NFCEE 0x82 is therefore an eSE endpoint and must not be
described as proof of eUICC card-emulation support.

## Runtime routing nuance

Although the configured default ISO-DEP, NFC-F, system-code and generic
off-host routes are 0x81, runtime routing contains fallback behavior.

Observed:

    New default ISO-DEP route=0x81
    New default A/B route=0x81
    New default F route=0x81
    New default SC route=0x81

but the stack subsequently reports:

    Route does not support A/B, using DH as default

and installs the default AID on:

    route=00

where route 0x00 is the Device Host.

Therefore the effective routing topology must be described per protocol/AID
rather than as a blanket "all NFC traffic is routed to UICC1" rule.

## ST21NFC firmware identity

Runtime initialization provides:

    HAL version       140-20240525-24W21p0
    HwVersion         0x04
    HwRevision        0x04
    FwVersion         0x01209280
    LoaderVersion     0x020201
    CustomerVersion   0x4646
    firmware image    st21nfc_fw7.bin

The vendor firmware image reports integrated NFC firmware patch 0x01209280,
matching the running controller firmware.


## SIM2 NFCEE comparison

The NFC initialization sequence was repeated after changing to the SIM2 test
configuration.

The resulting NFCEE topology was byte-for-byte unchanged:

    Rx 42 00 02 00 02

    Rx 62 00 08 81 01 00 01 03 01 02 00
    Rx 62 00 08 82 01 00 01 03 01 c0 01

The NFA layer likewise reports only:

    nfcee_id=0x81
    nfcee_id=0x82

and the eSE arbitration sequence remains:

    i2cNfccMayUseEse(1)
    ...
    i2cNfccMayUseEse(0)

No NFCEE 0x83 appears.

This weakens the previous hypothesis that:

    0x81 = SIM1
    0x83 = SIM2

The current stronger hypothesis is:

    0x81 = generic UICC NFCEE
    0x82 = embedded Secure Element
    0x83 = optional/dormant/alternate UICC route not instantiated on this SKU

The physical SIM slot may instead be selected below the ST21/NCI layer by the
MediaTek UICC/modem stack, while ST21 continues to expose the same UICC NFCEE
ID 0x81.

This must be correlated with `dumpsys secure_element` while SIM2 is active.

If Android reports:

    SIM1 mIsConnected:false
    SIM2 mIsConnected:true

while ST21 still reports NFCEE 0x81 with HOST_ID 0x02, that will strongly prove
that NFCEE 0x81 is slot-independent and multiplexed to the active UICC.

## UICC NFCEE is slot-independent

The SIM2 experiment now provides direct runtime evidence that NFCEE 0x81 is
not tied specifically to physical SIM slot 1.

With the SIM moved to slot 2:

    dumpsys secure_element:

        SIM1
        mIsConnected:false

        SIM2
        mIsConnected:true

The modem/RIL state independently confirms the same physical configuration:

    gsm.sim.state=[ABSENT,LOADED]

    vendor.gsm.ril.uicctype=[]
    vendor.gsm.ril.uicctype.2=[USIM]

    vendor.gsm.sim.ril.phbready=[false,true]

Despite that slot transition, ST21 NFCEE discovery remains unchanged:

    NFCEE count = 2

    0x81    HOST_ID 0x02    UICC
    0x82    HOST_ID 0xC0    eSE

No NFCEE 0x83 appears.

This strongly proves that:

    0x81 != physical SIM1

Instead, 0x81 is a logical UICC/contactless NFCEE whose backing physical SIM
slot is selected below the ST21/NCI layer by the MediaTek UICC/modem stack.

Current topology:

    ST21NFC
        |
        +-- NFCEE 0x81 -- logical UICC route
        |                    |
        |                    +-- MediaTek UICC/CLF switching
        |                            |
        |                            +-- SIM1
        |                            +-- SIM2
        |
        +-- NFCEE 0x82 -- embedded Secure Element

The device is configured for dual-SIM dual-standby:

    persist.radio.multisim.config=dsds
    ro.telephony.sim.count=2

and also exposes:

    ro.vendor.mtk_uicc_clf=1

The exact semantics of `ro.vendor.mtk_uicc_clf` have not yet been decoded, but
the property is clearly relevant to the MediaTek UICC/contactless integration
and should be retained for later source/binary reconstruction.

## Revised interpretation of OFFHOST_ROUTE_UICC

The vendor HAL configuration remains:

    OFFHOST_ROUTE_UICC=8183

but the runtime evidence no longer supports interpreting this as:

    0x81 = SIM1
    0x83 = SIM2

The current interpretation is:

    0x81 = active/logical UICC NFCEE
    0x82 = eSE
    0x83 = optional/secondary/dormant UICC route, unresolved

The highest-value remaining test for 0x83 is NFCEE discovery with two valid
SIMs installed simultaneously.

If two active SIMs cause:

    NFCEE count = 3

and a new NFCEE 0x83 appears, then 0x83 is likely the second simultaneous UICC
endpoint.

If the topology remains only 0x81 and 0x82 with two active SIMs, the platform
likely supports only one contactless UICC/SWP route at a time.

## /data/nfc SELinux bug confirmed

The NFC persistent-storage problem is now proven to be SELinux labeling rather
than Unix ownership or an NFA storage-path problem.

Stock state:

    /data/nfc
        owner   nfc:nfc
        mode    0770
        label   system_data_file

The running NFC process is:

    u:r:nfc:s0

The installed SELinux policy contains `nfc_data_file` and explicitly permits
the NFC domain to create/read/write files and directories of that type.

However, no file-context rule maps `/data/nfc` to `nfc_data_file`.

Under permissive SELinux, AVC records show the NFC process successfully
attempting create/write/open operations against the incorrectly labelled
directory.

After returning to enforcing mode:

    avc: denied { open }
        path="/data/nfc/nfaStorage.bin1"
        scontext=u:r:nfc:s0
        tcontext=u:object_r:system_data_file:s0

is followed directly by:

    nfa_nv_co_write: fail to open, error = 13

The required permanent LieppOS mapping is therefore expected to be:

    /data/nfc(/.*)?    u:object_r:nfc_data_file:s0

with an appropriate restorecon of existing contents.

## /data/nfc SELinux labeling bug — PROVEN

The NFC persistent-storage failure is now conclusively attributed to the
incorrect SELinux label on `/data/nfc`.

Stock state:

    /data/nfc
        owner:   nfc:nfc
        mode:    0770
        label:   u:object_r:system_data_file:s0

The NFC process runs as:

    u:r:nfc:s0

Under the stock label and enforcing SELinux, runtime AVCs explicitly showed:

    denied { open }
    path="/data/nfc/nfaStorage.bin1"
    scontext=u:r:nfc:s0
    tcontext=u:object_r:system_data_file:s0

followed by:

    nfa_nv_co_write: fail to open, error = 13

NfcEventLog also failed to create/write:

    /data/nfc/event_log.binpb.new

The installed SELinux policy already contains `nfc_data_file` and grants the
NFC domain the necessary directory and file permissions.

A temporary relabel was performed:

    chcon -R u:object_r:nfc_data_file:s0 /data/nfc

After relabeling, while SELinux remained ENFORCING, an NFC disable/enable cycle
completed without:

    nfa_nv_co_write errors
    NfcEventLog write errors
    NFC-related AVC denials

The persistent NFC files are now present under the correct context:

    /data/nfc/nfaStorage.bin1
    /data/nfc/event_log.binpb
    /data/nfc/param/

Therefore the bug and fix are proven.

Required permanent LieppOS policy mapping:

    /data/nfc(/.*)?    u:object_r:nfc_data_file:s0

Existing installations must additionally relabel the existing directory,
typically through restorecon during upgrade/boot migration.

## T4T NDEF NFCEE runtime status

Current status:

    Android Java T4T API path          PROVEN PRESENT
    Android JNI/NFA/RW implementation  PROVEN PRESENT
    ST vendor HAL templates            PROVEN PRESENT
    ST NDEF_NFCEE_ENABLE switch        PROVEN
    NFCEE 0x10 runtime exposure        PROVEN
    NFCEE 0x10 NDEF_STORAGE TLV        PROVEN
    stock ST switch                    DISABLED
    Android vendor config gate         PRESENT, exact source under reconstruction
    T4T read/write                     NOT YET PROVEN
    RF Type-4 NDEF emulation           NOT YET PROVEN

Important integration finding:

    NfcConfig::loadConfig()
        -> parse /vendor/etc/libnfc-nci.conf
        -> NfcAdaptation::GetVendorConfigs()
        -> ConfigFile::addConfig()

Do not manually add T4T_NFCEE_ENABLE to /vendor/etc/libnfc-nci.conf.
It collides with the vendor-config map and causes com.android.nfc to abort
with ConfigFile::addConfig() duplicate-key CHECK failure.

The next reverse-engineering target is the vendor/AIDL getConfig path that
supplies t4tNfceeEnable.


### Missing ST-to-Mainline T4T bridge — PROVEN

Exact device binary reconstruction proves:

    android.hardware.nfc-service-st
        AIDL interface version: 1
        NfcConfig writer: old V1 layout
        StNfc_hal_getConfig(): 0x6dc0..0x720c

The service does not query:

    NDEF_NFCEE_ENABLE
    T4T_NFCEE_ENABLE

although nfc_nci.st21nfc.st.so independently supports
NDEF_NFCEE_ENABLE and exposes NFCEE 0x10 when it is enabled.

Thus the stock software contains no bridge between:

    ST NDEF_NFCEE_ENABLE
             and
    Android NfcConfig.t4tNfceeEnable

This old-HAL/new-Mainline version skew is the reason Android discards the
otherwise runtime-visible NDEF NFCEE 0x10.

Permanent LieppOS fix: not yet runtime-proven.
Do not add T4T_NFCEE_ENABLE directly to /vendor/etc/libnfc-nci.conf.


### Mainline T4T force point — PROVEN

Installed libnfc_nci_jni.so:

    NfcAdaptation::GetVendorConfigs()
        0x1dbf18..0x1dd1a4

The effective t4tNfceeEnable byte is read at:

    0x1dc734:
        ldrb w1, [sp, #0x200]

and immediately converted into the ConfigValue for:

    T4T_NFCEE_ENABLE

The old ST AIDL V1 HAL cannot provide this later-added field, so it remains
zero.

Experimental compatibility patch:

    0x1dc734
    ldrb w1,[sp,#0x200]
        ->
    mov w1,#1

Runtime validation pending.


### T4T compatibility bridge — RUNTIME PROVEN

Stage C successfully bridged the old ST AIDL V1 HAL to the newer Android
Mainline T4T NFCEE implementation.

Required combination:

    ST:
        NDEF_NFCEE_ENABLE=1

    Android Mainline:
        effective t4tNfceeEnable=1

Experimental Mainline patch:

    libnfc_nci_jni.so
    0x1dc734

    ldrb w1,[sp,#0x200]
        ->
    mov w1,#1

Result:

    NdefNfceeService registered
    NDEF route = 0x10
    T4T subsystem initialized
    NFCEE 0x10 discovered
    NFCEE 0x10 enabled successfully
    handle = 0x0410
    A/B ISO-DEP routing installed
    D2760000850101 routed to NDEF-NFCEE

This proves the missing old-HAL/new-Mainline bridge is the blocker.

RF emulation and actual NDEF read/write remain to be tested.


### Embedded Type-4 NDEF service and routing — RUNTIME PROVEN

After enabling the ST NDEF NFCEE and bridging the missing Mainline
t4tNfceeEnable field, Android exposes the controller-resident NFCEE as:

    Component:
        com.android.nfc.ndef_nfcee/
        com.android.nfc.ndef_nfcee.NdefNfceeService

    Description:
        Embedded tag

    Service type:
        Off-host

    Off-host SE:
        NDEF-NFCEE

Static NFC Forum Type-4 NDEF application AID:

    D2760000850101

Effective Android routing:

    Routed to NFCEE 0x10

Routing table:

    AID_D2760000850101
        NFCEE_ID = 0x10
        Power State = 0x3B
        Exact match

The Android T4T/NDEF-NFCEE path is therefore integrated into the normal
card-emulation routing stack, not merely present as an enabled NFCEE.

The exact installed native library also exports operational T4T methods:

    t4tNfceeManager_doReadData
    t4tNfceeManager_doWriteData
    t4tNfceeManager_doClearNdefData
    t4tNfceeManager_isNdefNfceeEmulationSupported
    NativeT4tNfcee::openConnection
    NativeT4tNfcee::closeConnection
    NativeT4tNfcee::t4tReadData
    NativeT4tNfcee::t4tWriteData

Runtime NDEF read/write and external RF emulation are the next validation
targets.


### Runtime Type-4 CC-file read — PROVEN

A root app_process probe successfully invoked the real:

    android.nfc.IT4tNdefNfcee

interface through the NFC service.

Runtime results:

    isNdefOperationOngoing = false
    isNdefNfceeEmulationSupported = true

The CC file was successfully read from NFCEE 0x10.

Recovered live CC parameters:

    CC length       = 15
    mapping version = 0x20
    NDEF file ID    = 0xE104
    max NDEF size   = 8192 bytes
    read allowed    = true
    write allowed   = true

Native/NCI execution proves an actual NFCEE operation rather than a cached
framework value.

The stack performed:

    NativeT4tNfcee::openConnection
    NFA_T4tNfcEeOpenConnection
    RW_T4tNfceeSelectApplication
    RW_T4tNfceeSelectFile
    RW_T4tNfceeReadDataLen
    RW_T4tNfceeReadFile

and completed with:

    NFA_T4TNFCEE_READ_CC_DATA_CPLT_EVT

The NCI logical connection used conn_id 3 and was closed cleanly afterward.

This proves that the controller/NFCEE-resident Type-4 NDEF storage is
operational and readable from Android after applying the compatibility bridge.

Next target:

    read NDEF file 0xE104 without modifying it.


### Uninitialized NDEF file NLEN=0xFFFF read bug — PROVEN

Runtime read of the live NDEF file:

    file ID = 0xE104
    capacity = 8192 bytes

successfully performs:

    Type-4 application selection
    CC-file read
    NDEF-file selection
    NDEF NLEN read

The live two-byte NLEN returned by NFCEE 0x10 is:

    0xFFFF

The stack then incorrectly treats this as a literal 65535-byte payload:

    nfa_t4tnfcee_get_len:
        readLen 0xffff

    RW_T4tNfceeReadFile:
        Readlen=0xffff

and fails:

    rw_t4t_read_file:
        Cannot read above 0x7FFF for MV2.0

The Binder API consequently throws:

    java.lang.IllegalStateException:
        Ndef Nfcee read failed

Since the CC advertises only 8192 bytes of capacity, 0xFFFF cannot be a
valid NDEF message length.

This is consistent with the never-written / erased-file state documented
by the NativeT4tNfcee read API, but the lower NFA/RW path does not
special-case the erased 0xFFFF NLEN before invoking the normal MV2.0
reader.

Do not classify NDEF-file contents as successfully read yet.

Next test:
    initialize 0xE104 with a controlled NDEF record,
    then verify write -> read -> RF emulation.


### NFCEE NDEF write and readback — RUNTIME PROVEN

A controlled NDEF record was written to the live Type-4 NDEF file:

    NFCEE      = 0x10
    file ID    = 0xE104
    data size  = 23 bytes

Payload:

    D1 01 13 54 02 65 6E
    4C 69 65 70 70 4F 53 20
    54 34 54 20 74 65 73 74

which represents the NFC Forum Text record:

    "LieppOS T4T test"

Binder result:

    WRITE_STATUS = 0

Native execution completed:

    NFA_T4TNFCEE_OP_WRITE
    RW_T4tNfceeSelectApplication
    RW_T4tNfceeSelectFile
    RW_T4tNfceeUpdateNlen
    RW_T4tNfceeStartUpdateFile
    RW_T4tNfceeUpdateFile
    RW_T4tNfceeUpdateNlen
    NFA_T4TNFCEE_WRITE_CPLT_EVT

NativeT4tNfcee::t4tWriteData returned 23 bytes written. NfcService maps a
positive native byte count to Binder status 0.

The write logical connection was then closed.

A separate read operation subsequently reopened NFCEE 0x10 and reported:

    NLEN = 0x0017
         = 23

followed by:

    RW_T4tNfceeReadFile: Readlen=0x17
    copying data len 23
    NFA_T4TNFCEE_READ_CPLT_EVT

Binder returned:

    READ_LENGTH = 23
    MATCH = true

and the exact data written was recovered.

Important API detail:

    IT4tNdefNfcee.readData(fileId)

returns only the NDEF message bytes. The two-byte Type-4 NLEN is read and
consumed internally by the NFA/RW implementation.

Thus Android -> NFC Mainline -> ST HAL -> NFCEE 0x10 persistent storage
write and independent connection readback are runtime-proven.

Persistence across NFC restart/reboot and external RF emulation remain to
be tested.


### NDEF NFCEE RF listen request — RUNTIME PROVEN

After enabling NFCEE 0x10, the controller emits:

    61 0A 0B
    02
    00 03 10 80 04
    00 03 10 81 04

This is the previously reconstructed RF_NFCEE_DISCOVERY_REQ_NTF for
NFCEE 0x10 requesting ISO-DEP passive-listen operation on NFC-A and NFC-B.

Android receives it as:

    NFA_EE_DISCOVER_REQ_EVT
    nfceeId=0x0410
    la_proto=0x04
    lb_proto=0x04
    lf_proto=0x00

RoutingManager records:

    Handle=0x0410
    techA=0x04
    techB=0x04

The NFCC is then programmed with:

    RF_DISCOVER_CMD:
        21 03 05 02 80 01 81 01

representing NFC-A and NFC-B passive-listen discovery.

The command succeeds:

    41 03 01 00

Therefore the failure observed with an external Android reader is NOT due
to the NDEF NFCEE failing to request RF discovery.

External reader testing separately proves that the Ulefone detects the
reader's RF field, but no RF_INTF_ACTIVATED_NTF / ISO-DEP activation has
yet been observed.

Current failure boundary:

    RF field detected
        ->
    passive listen configured
        ->
    NO RF interface activation

The next investigation target is RF anticollision / listen-mode activation,
not NDEF storage or AID routing.


### External Type-4 NDEF RF emulation — END-TO-END RUNTIME PROVEN

An independent ST25R3916B reader connected to an ESP32 successfully
activated and profiled the Ulefone over 13.56 MHz RF, without ADB or any
wired connection to the phone.

External reader result:

    Type: ISO14443A
    UID: 08 F5 39 D9
    UID length: 4
    RF interface: ISO-DEP
    ATQA: 04 00
    SAK: 20
    NFCA subtype: NFCA T4T

The reader then successfully initialized the NFC Forum NDEF mapping:

    NDEF context init: ERR_NONE
    NDEF detect: ERR_NONE
    NDEF state: READWRITE
    Writable: YES
    NDEF message length: 23
    NDEF area length: 8192
    NDEF available space: 8190
    NDEF mapping version: 2.0

A raw NDEF read over RF succeeded:

    D1 01 13 54 02 65 6E
    4C 69 65 70 70 4F 53 20
    54 34 54 20 74 65 73 74

This is byte-for-byte identical to the payload previously written through
IT4tNdefNfcee:

    "LieppOS T4T test"

Therefore the following are runtime-proven end-to-end with an independent
external NFC reader:

- NFC-A RF activation and anticollision
- ISO-DEP activation
- NFC Forum Type-4 Tag presentation
- NDEF mapping detection
- CC/NDEF metadata access
- external RF NDEF payload read
- exact persistence of the 23-byte payload across independent RF access

The previous Android phone reader test that only produced RF_FIELD events
was a reader/application-side limitation and did not indicate a failure of
the Ulefone Type-4 emulation path.

External write capability is advertised by the Type-4 CC and reported by
the reader, but an external RF write operation has not yet been performed.

### Type-4 NDEF survives NFC disable/enable — RUNTIME PROVEN

After the 23-byte NDEF payload had been written previously, NFC was
explicitly disabled and re-enabled:

    cmd nfc disable-nfc
    sleep 3
    cmd nfc enable-nfc
    cmd nfc status

Result:

    Nfc is enabled

No NDEF write was performed after the restart.

An independent ST25R3916B + ESP32 reader subsequently activated the
Ulefone over RF and obtained:

    Type: ISO14443A
    UID: 08 AB 69 46
    RF interface: ISO-DEP
    ATQA: 04 00
    SAK: 20
    NFCA subtype: NFCA T4T

    NDEF state: READWRITE
    Writable: YES
    NDEF message length: 23
    NDEF area length: 8192
    NDEF mapping version: 2.0

Raw NDEF:

    D1 01 13 54 02 65 6E 4C 69 65 70 70 4F 53 20
    54 34 54 20 74 65 73 74

This is byte-for-byte identical to the original "LieppOS T4T test"
payload.

Therefore the NDEF data stored in NFCEE 0x10 survives a complete Android
NFC disable -> enable cycle.

Full device reboot persistence remains to be tested.

### Type-4 NDEF survives full device reboot — RUNTIME PROVEN

The Ulefone was fully rebooted after the 23-byte NDEF message had already
been written.

Immediately after boot, before restoring the experimental bridge:

    NDEF_NFCEE_ENABLE=0

No experimental mounts were present and the visible NFC JNI was the stock
binary:

    SHA256:
    b11bdea0ac537778f437810d43133f1f5b9240383c639d308e551a71b921cd8e

The experimental compatibility environment was then restored WITHOUT
performing any NDEF write:

    /data/local/tmp/libnfc-hal-st.t4t.conf
        -> /vendor/etc/libnfc-hal-st.conf

    NDEF_NFCEE_ENABLE=1

and inside the new com.android.nfc mount namespace:

    /data/local/tmp/libnfc_nci_jni.t4t-force.so
        -> /apex/com.android.nfcservices/lib64/libnfc_nci_jni.so

The new NFC process saw the patched JNI:

    1012cd8985432f1543a31f8bb0f3d088c9fb1aa6cc38b279428563a1f5579276

No IT4tNdefNfcee writeData() operation was performed after reboot.

An independent ST25R3916B + ESP32 reader then activated the Ulefone over
RF and obtained:

    Type: ISO14443A
    RF interface: ISO-DEP
    ATQA: 04 00
    SAK: 20
    NFCA subtype: NFCA T4T

    NDEF state: READWRITE
    Writable: YES
    NDEF message length: 23
    NDEF area length: 8192
    NDEF mapping version: 2.0

Raw RF-read NDEF:

    D1 01 13 54 02 65 6E 4C 69 65 70 70 4F 53 20
    54 34 54 20 74 65 73 74

This is byte-for-byte identical to the message written before the full
device reboot:

    "LieppOS T4T test"

Therefore NFCEE 0x10 Type-4 NDEF contents persist across a complete device
reboot.

The ESP32 EN button was pressed only to restart the one-shot external
reader sketch; it does not modify the Ulefone NDEF storage.

### External RF write -> Android Binder readback — END-TO-END RUNTIME PROVEN

A controlled ST25R3916 Type-4 writer was used against the Ulefone NFCEE NDEF endpoint.

The Type-4 write path was split into its three protocol stages:

~~~text
Stage 1 BeginWriteMessage: ERR_NONE
Stage 2 WriteBytes:        ERR_NONE
Stage 3 EndWriteMessage:   ERR_NONE
~~~

The externally verified 23-byte NDEF payload was:

~~~text
D1 01 13 54 02 65 6E
4C 69 65 70 70 4F 53 20
52 46 20 70 72 6F 6F 66
~~~

This is an NFC Forum Text RTD containing:

~~~text
LieppOS RF proof
~~~

After the external RF write/readback, Android independently read file 0xE104
through IT4tNdefNfcee.readData(), without performing an Android-side write:

~~~text
NDEF_FILE_ID=0xE104
MAX_SIZE=8192
BUSY=false
RAW_LENGTH=23
RAW_HEX=D1 01 13 54 02 65 6E 4C 69 65 70 70 4F 53 20 52 46 20 70 72 6F 6F 66
~~~

Therefore the following path is runtime proven:

~~~text
ST25R3916 external RF Type-4 write
    -> NFCEE 0x10 / E104
    -> Android IT4tNdefNfcee.readData()
    -> exact same NDEF bytes
~~~

Combined with the previously proven Android-write -> NFCEE -> external-RF-read
direction, bidirectional Type-4 NDEF access is end-to-end runtime proven.

Note: T4tNdefRead.java's historical NLEN parser is obsolete.
readData() returns the NDEF message bytes only, not the two-byte NLEN.
Its reported NLEN=0xD101 is simply the first two NDEF bytes interpreted
incorrectly.

### Interrupted external Type-4 write leaves NLEN=0 — RUNTIME PROVEN

During a controlled external write attempt the ST25 writer returned ERR_TIMEOUT.

Before the attempt, the externally read NDEF message length was 23 bytes.

After the timeout, Android successfully selected the Type-4 application,
read the CC file, selected E104, and then reported:

~~~text
RW_T4tNfceeReadDataLen
nfa_t4tnfcee_get_len: No Data to Read
~~~

An independent ST25R3916 profile repeatedly reported:

~~~text
NDEF state: INITIALIZED
Writable: YES
NDEF message length: 0
NDEF area length: 8192
NDEF available space: 8190
NDEF mapping version: 2.0
~~~

RFAL source confirms the Type-4 write sequence is:

~~~text
1. write NLEN=0
2. write NDEF payload at offset 2
3. write final NLEN
~~~

Thus an interrupted external Type-4 transaction can leave E104 logically
empty (NLEN=0) while the Type-4 application, CC file, NDEF file, and write
capability remain functional.

### Controlled external RF OLD -> NEW mutation + Android readback — END-TO-END RUNTIME PROVEN

The external ST25R3916 Type-4 writer was modified with a hard manual gate.

Before the user entered `g`, no RFAL/NFC operation was executed. The observed
startup sequence was:

~~~text
ARMED - type g then Enter to start RF test
g
GO - starting RF
rfalNfcInitialize: ERR_NONE
rfalNfcDiscover: ERR_NONE
~~~

The reader first independently read the existing NDEF payload:

~~~text
D1 01 13 54 02 65 6E 4C 69 65 70 70 4F 53 20
52 46 20 70 72 6F 6F 66
~~~

which is:

~~~text
LieppOS RF proof
~~~

The externally triggered Type-4 write then completed all three stages:

~~~text
Stage 1 BeginWriteMessage: ERR_NONE
Stage 2 WriteBytes:        ERR_NONE
Stage 3 EndWriteMessage:   ERR_NONE
~~~

The reader immediately read back:

~~~text
D1 01 13 54 02 65 6E 4C 69 65 70 70 4F 53 20
52 46 20 66 69 6E 61 6C
~~~

which is:

~~~text
LieppOS RF final
~~~

Without performing any Android-side write, Android then independently read
NFCEE Type-4 NDEF file 0xE104 through IT4tNdefNfcee.readData():

~~~text
NDEF_FILE_ID=0xE104
MAX_SIZE=8192
BUSY=false
RAW_LENGTH=23
RAW_HEX=D1 01 13 54 02 65 6E 4C 69 65 70 70 4F 53 20 52 46 20 66 69 6E 61 6C
NDEF_BACKUP=/data/local/tmp/t4t-e104-ndef.bin
~~~

Therefore the exact controlled chain is runtime proven:

~~~text
external RF reads OLD
    -> explicit manual trigger
    -> external RF writes NEW
    -> external RF reads NEW
    -> Android reads exact same NEW bytes
~~~

This removes the earlier post-upload auto-run ambiguity completely.

Bidirectional Type-4 NDEF access across:

~~~text
Android <-> NFCEE 0x10 / E104 <-> external ISO-DEP Type-4 RF
~~~

is now end-to-end runtime proven.
