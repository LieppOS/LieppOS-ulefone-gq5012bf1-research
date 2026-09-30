# ST21 + LieppOS master capability plan for Ulefone Armor 29 Pro Thermal (GQ5012BF1)

Status: **research / implementation master document**  
Goal: **utilize every ST21 NFC capability that the GQ5012BF1 hardware, controller firmware, Android NFC stack, secure-element topology, and RF design can expose safely and legitimately.**

This file deliberately separates:

- **PROVEN-GQ5012BF1** — proven from the phone's stock kernel/module evidence already reconstructed in the LieppOS project.
- **PROVEN-ST21-FAMILY** — publicly documented by ST for the ST21NFCD family or implemented by ST's public Android ST21 HAL.
- **IMPLEMENTABLE-HOST** — LieppOS can implement this above the NFCC without changing controller firmware.
- **CONTROLLER-DEPENDENT** — possible only if the exact GQ5012BF1 ST21 firmware advertises or accepts it.
- **BOARD-DEPENDENT** — depends on how Ulefone wired the NFC controller, Secure Element/UICC, clocks, power, antenna, etc.
- **UNKNOWN** — must be measured/reverse-engineered on the exact phone.
- **LIKELY-BLOCKED** — public evidence suggests the feature is below a secure or silicon boundary.

The objective is **not** merely "make Android NFC work." The objective is to expose the complete useful ST21/NCI capability set to LieppOS through a controlled native service, developer API and NFC laboratory UI.

---

# 1. Current GQ5012BF1 NFC facts

## 1.1 Kernel driver

The stock NFC kernel module is:

```text
st21nfc.ko
```

Known GQ5012BF1 stock driver identity:

```text
stock ST21 driver version: 2.2.0.19
public NothingOSS donor:   2.2.0.15
```

The LieppOS project already completed a binary-assisted source-delta reconstruction of the stock **2.2.0.19** implementation.

Final kernel-side reconstruction status:

```text
ST21_SOURCE_DELTA_RECONSTRUCTION_COMPLETE
ABI_EXACT_FOR_STOCK_KERNEL_IMPORT_CONTRACT
```

The reconstruction closes all **54 stock kernel imports / MODVERSION entries** against the exact GKI used by the phone.

The stock 2.2.0.19 delta over the NothingOSS 2.2.0.15 donor includes behavior around:

- controller recovery;
- CORE_RESET_NTF handling;
- probe-time device-property handling;
- DT u32 property parsing;
- explicit GPIO cleanup;
- workqueue destruction;
- dedicated wakeup-source registration/unregistration;
- IRQ wake handling.

Frozen reconstruction source already recorded by the project:

```text
$GKI_WS/lieppos/st21nfc-2.2.0.19-recon/st21nfc.c.r5j-final
```

Important consequence:

> The Linux transport/recovery layer is already under source control. Future ST21 work should focus primarily on the NFC HAL, Android NFC stack, NCI commands, firmware/configuration and exact controller capabilities rather than repeatedly rewriting the kernel transport driver.

---

# 2. Architecture and where each capability lives

The practical stack is:

```text
Applications / LieppOS NFC Lab
            │
            ▼
Android NFC framework / NfcService
            │
            ▼
libnfc-nci / NFA
            │
            ▼
ST NFC AIDL/HIDL HAL
            │
            ▼
ST HAL wrapper / proprietary commands
            │
            ▼
NCI 2.x control + data protocol
            │
            ▼
st21nfc Linux transport driver
            │
            ▼
physical host link to NFCC
            │
            ▼
ST21 NFC controller firmware
            │
            ▼
RF digital + analog frontend
            │
            ▼
13.56 MHz antenna / Secure Elements / UICC
```

This creates four capability boundaries:

### Boundary A — Android/framework policy

LieppOS controls this.

We can remove artificial UI/API restrictions, add privileged APIs, expose native transceive tools, logging, HCE configuration, routing controls and diagnostics.

### Boundary B — ST HAL / NCI protocol

LieppOS controls the host side.

We can build a first-class native NCI console, inspect all commands and notifications, send vendor/proprietary commands, modify configuration and instrument controller traffic.

### Boundary C — ST21 firmware

We can communicate with it but do not automatically control its implementation.

Firmware features, vendor commands, raw-frame access, listen-mode parameters, low-level RF behavior and hidden diagnostics depend on the exact firmware.

### Boundary D — silicon / RF hardware

Software cannot create analog capabilities the silicon does not implement.

True arbitrary modulation, raw RF sampling, arbitrary anticollision timing and other "transparent RF frontend" functions require support from the ST21 silicon/firmware.

---

# 3. Public ST21NFCD family capability set

**Important:** GQ5012BF1 is proven to use the `st21nfc` software stack, but the exact ST21 silicon/revision still needs to be read from the device. Until that is done, the items in this section are **ST21-family capabilities, not automatically proven enabled on this exact board**.

ST publicly describes ST21NFCD as a mobile NFC controller with:

- ARM Cortex-M3 controller;
- NCI 2.0;
- eFlash for full firmware update;
- secure firmware-update mechanism;
- enhanced active load modulation;
- TX drive up to 1.3 W;
- support for small/metal-frame antennas;
- optimized low-power modes;
- battery voltage monitoring;
- integrated PMU;
- automatic wake-up via communications interfaces, timers, GPIO, RF field or tag detection;
- external DC/DC support for TX supply.

Public RF protocol support:

## Reader / Writer

- NFC Forum Type 1 tags;
- NFC Forum Type 2 tags;
- NFC Forum Type 3 tags;
- NFC Forum Type 4 tags;
- NFC Forum Type 5 tags;
- ISO/IEC 15693;
- MIFARE Classic;
- Thinfilm/Kovio barcode.

## Peer-to-peer

- active NFCIP-1;
- passive NFCIP-1;
- ISO/IEC 18092 initiator;
- ISO/IEC 18092 target.

## Card emulation

- ISO/IEC 14443 Type A;
- ISO/IEC 14443 Type B;
- JIS X 6319-4 / NFC-F-family operation;
- MIFARE Classic through SWP-CLT according to ST's product description.

The MIFARE Classic card-emulation statement is specifically tied to **SWP-CLT** in ST documentation. It must **not** be interpreted as proof that Android host CPU HCE can directly emulate arbitrary MIFARE Classic cards.

Public host / secure-element interfaces listed for the family:

- two SWP master interfaces up to 1.695 Mbit/s;
- I2C slave interface up to 3.4 MHz;
- SPI slave and master up to 13 MHz;
- HSUART up to 6 Mbit/s.

Which of those are physically wired on GQ5012BF1 is a separate board-level question.

---

# 4. Capability matrix for LieppOS

| Capability | Public ST21 support | LieppOS host work | Exact-phone status |
|---|---|---|---|
| NDEF read/write | yes through standard NFC tag stack | straightforward | expected / validate |
| Type 1 tag R/W | ST21NFCD documented | expose/test | controller-dependent until queried |
| Type 2 / NTAG / Ultralight R/W | documented | expose raw + parsed tooling | likely |
| Type 3 / FeliCa tag R/W | documented | expose NFC-F tools | controller/config dependent |
| Type 4 / ISO-DEP | documented | full APDU console | very high-confidence |
| Type 5 / NFC-V | documented | raw + parsed ISO15693 tools | controller/config dependent |
| ISO15693 | documented | native transceive + inventory/block UI | high-priority |
| MIFARE Classic R/W | documented ST21NFCD capability | add dedicated reader API/tooling | must prove exact firmware capability |
| Kovio / Thinfilm | documented | enable proprietary discovery if firmware supports it | unknown on phone |
| ISO18092 active P2P | documented | enable/probe Android/NCI support | unknown |
| ISO18092 passive P2P | documented | enable/probe | unknown |
| Type-A card emulation | documented | HCE + routing laboratory | expected |
| Type-B card emulation | documented controller family | custom routing/listen-mode research | unknown host exposure |
| NFC-F/JIS card emulation | documented | NFC-F HCE/routing research | board/firmware dependent |
| MIFARE Classic CE via SWP-CLT | documented | requires matching SE/SWP path | board-dependent |
| Secure-element routing | supported by ST HAL | expose controlled route inspector/editor | exact SE topology unknown |
| eSE routing | ST HAL supports route IDs/config | inspect exact board | unknown |
| UICC/SIM routing | ST HAL supports | inspect exact board | unknown |
| screen-off CE | ST HAL config supports | enable as LieppOS option | board/SE dependent |
| switch-off CE | ST HAL config supports | expose policy | controller/board dependent |
| USB-charging NFC mode | ST HAL supports vendor setting | expose if relevant | unknown stock config |
| observe mode | current Android/ST HAL supports | add analyzer UI/API | firmware-capability dependent |
| per-tech observe mode | current ST HAL implementation supports | expose A/B/F/V mask | firmware-capability dependent |
| polling frame notifications | Android proprietary NCI spec | capture/log/decode | firmware-capability dependent |
| poll-frame RSSI/gain metadata | Android proprietary spec has gain byte | visualize | firmware-capability dependent |
| custom polling-loop frames | Android proprietary NCI spec | implement frame-table editor | firmware-capability dependent |
| observe exit-frame table | Android proprietary NCI spec | editor + logger | firmware-capability dependent |
| power-saving NCI mode | Android proprietary spec | expose diagnostics/policy | firmware-capability dependent |
| blank/custom NCI frame function | Android proprietary spec defines blank NCI command | research carefully | firmware-capability dependent |
| raw NCI logging | host-side possible | implement always-on trace ringbuffer | implementable |
| ST FW debug traces | ST HAL exposes vendor debug mode | capture/decode | controller-dependent but promising |
| HAL event log | current ST config supports | preserve / expose | implementable |
| controller firmware update | documented + ST HAL | build safe inspector/updater | update path exists |
| custom-parameter config update | ST HAL has separate state | extract/decode/configure | high-priority unknown |
| UWB parameter update path | newer ST HAL has handler | inventory only unless board has relevant integration | likely irrelevant / verify |
| firmware recovery | ST HAL + kernel recovery paths | preserve and instrument | proven stack behavior |
| hibernate exit/recovery | ST HAL includes explicit state | expose diagnostics | implementable |
| arbitrary NFC UID | not proven | test vendor/listen config | unknown |
| arbitrary ATQA/SAK | not proven | test NFCC listen controls | unknown |
| arbitrary NTAG emulation | not proven | requires low-level listen-mode feature | unknown / low confidence |
| host MIFARE Classic emulation | not proven | controller/SE limitation | low confidence |
| analog register control | not public standard interface | vendor-command RE | unknown |
| arbitrary RF modulation | not publicly documented | cannot create in Android | likely blocked |
| raw RF waveform capture | not publicly documented | impossible without HW support | likely blocked |
| fully custom ST21 firmware | secure update exists | updater can send images | likely blocked by authentication |

---

# 5. ST Android HAL features we should utilize

ST publishes an Android `hardware/st/nfc` HAL implementation.

The current tree contains:

```text
st21nfc/
    adaptation/
    gki/
    hal/
    include/
    hal_wrapper.cc
    libnfc-hal-st-example.conf
```

This should become a primary LieppOS source reference.

## 5.1 Firmware and configuration storage

ST's example configuration exposes:

```text
STNFC_FW_PATH_STORAGE="/vendor/firmware"
STNFC_FW_BIN_NAME="/st54j_fw.bin"
STNFC_FW_CONF_NAME="/st54j_conf.bin"
```

These exact example filenames do **not** prove that the Ulefone uses ST54J or those files. The important fact is that ST's HAL architecture supports separately supplied:

- controller firmware image;
- controller configuration/custom-parameter image.

The exact GQ5012BF1 filenames must be extracted from stock vendor configuration/libraries.

---

# 6. Firmware update architecture

The ST21 family publicly supports:

```text
eFlash for full firmware update
secure firmware update mechanism
```

ST's Android HAL has explicit states and handlers for:

```text
FW_UPDATE_NEEDED
CONF_UPDATE_NEEDED
UWB_CONF_UPDATE_NEEDED

HAL_WRAPPER_STATE_UPDATE
HAL_WRAPPER_STATE_APPLY_CUSTOM_PARAM
HAL_WRAPPER_STATE_APPLY_UWB_PARAM
```

and routines/state transitions including:

```text
UpdateHandler
ApplyCustomParamHandler
ApplyUwbParamHandler
ExitHibernateHandler
```

The public HAL also handles:

- firmware download retries;
- reset pulses;
- recovery;
- controller mode checks;
- firmware-patch availability;
- custom-parameter availability.

## 6.1 LieppOS firmware objectives

Implement a **read-only firmware inspector first**:

```text
controller silicon / HW revision
FW version
FW capabilities
FW update state
config version
image filenames
image hashes
image metadata
rollback/version fields
authentication/signature fields
```

Then implement a guarded updater capable of using **authentic accepted images**.

## 6.2 What an unlocked phone does NOT automatically provide

An unlocked Android bootloader does not imply an unlocked ST21 bootloader.

The controller has its own secure firmware-update mechanism. Therefore:

```text
root               != controller signing authority
custom Android     != controller signing authority
custom kernel      != controller signing authority
AVB disabled       != controller signing authority
```

A modified firmware image is expected to be rejected if authentication occurs inside the controller loader.

## 6.3 Full-custom firmware research

Treat this as a final-stage research problem.

Possible outcomes:

1. official images are authenticated and only accepted signatures boot;
2. official firmware can be upgraded/downgraded subject to anti-rollback;
3. config/custom-param files have weaker or separate authentication;
4. service/development mode exists;
5. a loader/protocol vulnerability exists;
6. exact silicon has undocumented debug facilities.

Do not assume any of these without evidence.

---

# 7. Configuration/custom-parameter research

This may be more valuable than replacing executable firmware.

ST's HAL explicitly distinguishes:

```text
FW update
configuration/custom-parameter update
```

We need to determine what lives in the Ulefone configuration blob.

Potential classes of parameters to investigate:

- RF tuning profiles;
- antenna tuning values;
- reader discovery parameters;
- listen-mode parameters;
- power thresholds;
- Secure Element routing defaults;
- low-power behavior;
- clock settings;
- field-detection settings;
- protocol enables;
- proprietary protocol IDs;
- trace/debug settings;
- regional or certification parameters.

These are **candidate categories**, not proven contents of the GQ5012BF1 blob.

Every field must be identified by stock behavior, ST HAL code, firmware/config diffs, or controlled read-only command output before modification.

---

# 8. Proprietary protocol/discovery configuration already exposed by ST HAL

ST's current example configuration contains an `NFA_PROPRIETARY_CFG` block with entries for:

```text
protocol18092Active
protocolBPrime
protocolDual
protocol15693
protocolKovio
protocolMifare
discoveryPollKovio
discoveryPollBPrime
discoveryListenBPrime
```

This is extremely relevant.

It means LieppOS should not restrict itself to only the technologies exposed by the default Android UI.

We should provide a capability inspector showing:

```text
NFC-A
NFC-B
NFC-F
NFC-V / ISO15693
ISO18092 active
B-prime
dual protocol
Kovio
MIFARE
Kovio poll
B-prime poll
B-prime listen
```

For each:

```text
framework support
HAL config value
NFCC advertised support
runtime enable result
test result
```

Do not enable unsupported technologies by blindly changing `0xFF` or vendor protocol IDs. First query exact NFCC capability behavior.

---

# 9. Reader/Writer features to implement

## 9.1 Universal tag inventory

LieppOS NFC Lab should identify at least:

- technology;
- RF protocol;
- UID/identifier;
- ATQA/SAK when exposed;
- ATS / historical bytes when exposed;
- ISO-DEP parameters;
- NFC-F IDm/PMm/system code;
- ISO15693 UID/DSFID/AFI where exposed;
- NDEF capability;
- writable/read-only state;
- raw technology list;
- max transceive size;
- timeout;
- controller/protocol route.

## 9.2 Raw transceive consoles

Implement technology-specific consoles for authorized tags:

### NFC-A

- frame payload input/output;
- CRC/framing mode where host API permits;
- activation metadata;
- ISO-DEP/APDU mode;
- timing/log timestamps.

### NFC-B

- activation parameters;
- ISO-DEP/APDU;
- raw transceive where exposed.

### NFC-F

- polling/system-code tools;
- raw command console.

### NFC-V / ISO15693

- inventory;
- addressed/non-addressed commands;
- system information;
- block read/write tooling;
- raw command console.

### MIFARE Classic

Only expose this if the exact firmware reports/supports `NCI_PROTOCOL_MIFARE`.

Goal:

- identify controller-level MIFARE protocol support;
- determine whether authentication is performed in controller firmware;
- support user-supplied legitimate keys;
- read/write blocks for cards the user is authorized to test;
- characterize limitations versus dedicated low-level tools.

### Kovio

If the controller/firmware exposes the proprietary Kovio discovery type, add read/decode support.

---

# 10. ISO-DEP / smart-card laboratory

This is one of the areas where the phone can become more capable than a small embedded multitool.

Implement:

```text
APDU terminal
APDU history
APDU script engine
TLV parser
BER-TLV viewer
ATR/ATS viewer
ISO7816 status-word decoder
AID database
session recorder
replay against authorized test cards
PC remote API
Wi-Fi/USB/ADB bridge
```

Use it for development against user-owned/test smart cards and HCE applications.

ST's example HAL config currently exposes a very large:

```text
ISO_DEP_MAX_TRANSCEIVE
```

setting, so LieppOS should query and expose the actual max transceive supported by this phone rather than hardcoding Android app-level assumptions.

---

# 11. Host Card Emulation

LieppOS should expose all Android HCE functionality without unnecessary framework restrictions.

## Type-4 / ISO-DEP HCE

Build a developer HCE manager with:

- AID editor;
- multiple virtual cards;
- APDU scripting;
- dynamic response engine;
- SQLite-backed card state;
- network-backed test services;
- per-reader logging;
- latency measurements;
- per-AID routing selection;
- service enable/disable without editing XML manually.

## NFC-F HCE

Investigate and expose Android HostNfcFService functionality if supported by the framework and exact controller configuration.

## Limits

Standard Android HCE does **not** imply:

- arbitrary anticollision UID;
- arbitrary ATQA;
- arbitrary SAK;
- NTAG/Ultralight memory-level emulation;
- MIFARE Classic host emulation.

Those are separate NFCC/controller capabilities that must be proven.

---

# 12. Secure Element and off-host routing

ST's HAL example explicitly supports route configuration for:

```text
host
UICC_1
UICC_2
eSE
eUICC / SPI-SE
```

and exposes config fields including:

```text
DEFAULT_ROUTE
DEFAULT_OFFHOST_ROUTE
DEFAULT_NFCF_ROUTE
DEFAULT_SYS_CODE_ROUTE
DEFAULT_ISODEP_ROUTE
OFFHOST_ROUTE_UICC
OFFHOST_ROUTE_ESE
OFF_HOST_ESE_PIPE_ID
OFF_HOST_SIM_PIPE_ID
```

LieppOS should build an **SE topology inspector** that reports what actually exists on the Armor 29 Pro:

```text
NFCEE list
NFCEE IDs
UICC routes
eSE routes
eUICC routes
HCI gates/pipes
AID routing table
protocol routing
technology routing
power-state masks
FeliCa system-code routing
```

No route should be modified until the exact stock topology is preserved.

This area can affect payments, transit credentials and SIM/eSIM services, so the default LieppOS UI should be read-only unless explicitly placed in developer mode.

---

# 13. Screen-off and switch-off card emulation

Public ST configuration includes:

```text
CE_ON_SWITCH_OFF_STATE
SCREEN_OFF_POWER_STATE        (older HAL/config generation)
```

and current route/power configuration.

Potential LieppOS features:

- inspect screen-off CE state;
- choose whether HCE/off-host CE remains active with display off;
- inspect switch-off CE capability;
- configure only off-host routes for true power-off operation;
- show which credentials/routes remain usable in each power state.

True phone-off operation usually depends on off-host Secure Element routing and board power design, not just Android software.

---

# 14. Observe mode — high-priority Flipper-like capability

Recent Android defines proprietary NCI commands for passive observe mode.

Current ST Android HAL code has explicit support for observe mode, including per-technology behavior.

Android proprietary NCI capabilities include:

```text
Observe mode
Polling frame notification
Power saving mode
Autotransact polling-loop filter
Number of exit-frame entries
Reader-mode annotation
```

## 14.1 Capability discovery

The first command to support in LieppOS NFC Lab is:

```text
NCI_ANDROID_GET_CAPS
```

Record every returned capability byte verbatim.

Do not infer support from Android version.

## 14.2 Observe mode

If supported:

```text
NCI_ANDROID_PASSIVE_OBSERVE_MODE_CMD
```

allows the NFCC to observe polling activity in listen mode without immediately participating in normal card emulation.

## 14.3 Per-technology observe mode

Newer ST HAL code implements per-technology observe behavior.

Android defines a technology mask:

```text
bit 0 = NFC-A
bit 1 = NFC-B
bit 2 = NFC-F
bit 3 = NFC-V
```

LieppOS should expose this as four toggles.

## 14.4 Polling frame notifications

`NCI_ANDROID_POLLING_FRAME_NTF` can report polling frames seen by the controller.

The Android specification supports frame types:

```text
remote field
NFC-A
NFC-B
NFC-F
NFC-V
unknown/raw frame
```

Reports include:

- timestamp;
- gain field when available;
- identifiable frame data;
- short/long frame flag.

This is one of the best opportunities for a phone-native **reader analyzer**.

A LieppOS UI should display:

```text
timestamp
field on/off
technology
raw bytes
decoded command
gain
reader/session grouping
```

and allow export to JSON/PCAP-like research formats.

---

# 15. Observe exit-frame filters

Android proprietary NCI supports a configurable table of frames that can cause observe mode to suspend/exit.

Capabilities include:

```text
NCI_ANDROID_SET_PASSIVE_OBSERVER_EXIT_FRAME_CMD
NCI_ANDROID_GET_PASSIVE_OBSERVER_EXIT_FRAME_CMD
```

Entries may include:

- frame type;
- power state;
- reference data;
- mask;
- timeout.

LieppOS NFC Lab should provide a safe editor for **authorized test readers**.

This gives us a programmable reader-detection / reader-classification system if supported by the exact firmware.

---

# 16. Custom polling-loop frames

Android proprietary NCI defines:

```text
NCI_ANDROID_SET_POLLING_LOOP_ANNOTATION_CMD
NCI_ANDROID_GET_POLLING_LOOP_ANNOTATION_CMD
```

The table can contain custom RF frames inserted into the standard polling loop.

The current specification allows up to four entries, with:

- qualifier/type;
- placement in discovery loop;
- waiting time;
- 1–16 bytes of frame data.

If supported by the GQ5012BF1 firmware, this is an important route toward **Flipper-like customized polling** without replacing ST21 firmware.

LieppOS should expose this only in a developer laboratory UI because malformed polling sequences can interfere with ordinary NFC discovery.

---

# 17. Blank NCI command

Android's proprietary NCI specification includes:

```text
NCI_ANDROID_BLANK_NCI_CMD
```

with a frame-data payload.

This must be investigated on the exact controller rather than assumed to mean arbitrary over-the-air RF transmission.

Research steps:

1. query capabilities;
2. inspect ST HAL handling;
3. determine whether controller accepts the opcode;
4. characterize what layer the provided frame represents;
5. compare emitted NCI notifications;
6. never label it "raw RF" until RF behavior is proven.

---

# 18. Polling-loop notifications without full observe mode

ST's Android HAL history contains explicit work around forwarding polling-loop notifications and observe-mode interaction.

Therefore LieppOS should treat these as separate capability bits:

```text
observe mode
polling-frame notifications
per-tech observe
poll-loop custom frames
reader annotation
```

rather than one boolean feature.

---

# 19. Power-saving features

Android proprietary NCI defines power-saving capability/query commands.

ST21NFCD publicly documents:

- optimized power modes;
- low-power state machine;
- automatic wake through RF field/tag detection;
- battery voltage monitoring.

LieppOS objectives:

- report NFCC power mode;
- report power-saving support;
- expose power-state transitions in diagnostics;
- log field-detect wakeups;
- measure NFC idle power in controlled integration testing;
- preserve secure-element availability when Android enters deep sleep.

Do not expose arbitrary PMU/voltage changes until exact vendor commands and safe ranges are understood.

---

# 20. RF field/tag wake

ST21NFCD family documentation states automatic wake-up can occur from:

- host communication interface;
- internal timers;
- GPIO;
- RF field;
- tag detection.

If the exact GQ5012BF1 silicon/firmware supports all of these, LieppOS can potentially implement very low-power NFC discovery while the AP is suspended.

Research goals:

```text
which wake sources are enabled
which are configurable
how ST HAL programs them
what kernel IRQ wakes the AP
whether field detection can be surfaced separately from tag activation
```

---

# 21. ST firmware debug traces

ST's HAL includes vendor-specific firmware debug tracing support.

Configuration includes:

```text
STNFC_FW_DEBUG_ENABLED
```

The public HAL contains proprietary commands/buffers for reading/configuring firmware debug traces.

This is a high-value reverse-engineering target.

LieppOS should implement:

```text
ST21 firmware trace enable/disable
trace stream capture
timestamping
raw binary export
string/event decoder as semantics are learned
trace correlation with NCI packets
```

This may reveal internal:

- RF state transitions;
- routing;
- protocol activation;
- error recovery;
- FW update decisions;
- SWP/SE activity.

Do not assume all traces are available in production firmware.

---

# 22. HAL event logging

Current ST configuration contains:

```text
HAL_EVENT_LOG_DEBUG_ENABLED
HAL_EVENT_LOG_STORAGE
```

LieppOS should make HAL event logging a proper debugging facility:

```text
/data/vendor/nfc/... ringbuffer
export button
boot/session ID
controller FW version
NCI TX/RX sequence
HAL state transition
driver reset/recovery events
```

Sensitive Secure Element/application data should be redacted by default.

---

# 23. Complete NCI recorder

This should be implemented regardless of hidden controller features.

Create a privileged native recorder between Android NFC stack and ST HAL transport.

Record:

```text
monotonic timestamp
direction: HOST->NFCC / NFCC->HOST
NCI MT/PBF/GID/OID
payload
decoded standard command
decoded Android proprietary command
decoded known ST proprietary command
HAL state
RF state
current route
optional application/session label
```

Storage formats:

```text
binary lossless
human-readable text
JSON
Wireshark-friendly custom export if practical
```

This recorder becomes the primary oracle for discovering all Ulefone-specific controller usage.

---

# 24. ST proprietary command dictionary

Build a versioned database in the research repo.

For every observed ST command:

```text
GID
OID
request bytes
response bytes
notification bytes
call site
precondition
controller mode
stock purpose
side effects
firmware versions observed
confidence
```

Seed it from ST's public HAL and expand it only with exact GQ5012BF1 evidence.

Possible categories:

- firmware info;
- firmware update;
- custom params;
- debug traces;
- NFC mode;
- hibernate;
- recovery;
- Secure Element;
- RF configuration;
- diagnostics.

---

# 25. MIFARE Classic

This deserves explicit treatment because ST publicly lists MIFARE Classic support in reader/writer mode.

## Goal

Determine whether exact GQ5012BF1 firmware exposes:

```text
NCI_PROTOCOL_MIFARE
```

ST's HAL has a `protocolMifare` proprietary protocol configuration field.

If present, implement:

- Classic card identification;
- controller-supported authentication;
- sector/block viewer;
- authorized key entry/storage;
- read/write tools for owned/test cards;
- controller error/status decoder.

## Do not assume

- Crypto1 implementation is accessible to host software;
- arbitrary raw Crypto1 exchanges are exposed;
- nested/hardnested/offline recovery primitives exist;
- host can emulate Classic;
- UID can be freely chosen.

Those are separate questions.

---

# 26. ISO15693 / NFC-V

ST21NFCD publicly supports ISO/IEC 15693 and NFC Forum Type 5.

ST HAL proprietary config also contains `protocol15693`.

LieppOS should implement first-class NFC-V tooling:

```text
inventory
UID
system info
DSFID
AFI
block size/count
single/multi-block read
single/multi-block write where authorized
lock status
raw command terminal
timing/session log
```

Also verify Android proprietary observe mode's NFC-V mask and polling-frame notifications.

---

# 27. NFC-F / FeliCa

Public controller documentation includes:

- Type 3 tag support;
- JIS X 6319-4 card emulation;
- NFC-F routing configuration in ST HAL.

LieppOS goals:

```text
FeliCa polling
IDm / PMm
system-code discovery
raw command console
NfcF HCE
off-host NFC-F route inspection
system-code routing editor in developer mode
```

Do not modify transit/payment routes by default.

---

# 28. NFC-A / NFC-B

LieppOS should expose activation information normally hidden by simple Android apps.

For NFC-A:

```text
UID
ATQA
SAK
ATS
historical bytes
protocol mapping
ISO-DEP parameters
raw transceive capability
```

For NFC-B:

```text
PUPI / activation info when available
ATQB
protocol info
ATTRIB/ISO-DEP metadata
raw transceive capability
```

Then investigate whether listen-mode parameters such as UID/ATQA/SAK/Type-B identifiers can be changed through standard or ST proprietary NFCC configuration.

Status today:

```text
arbitrary UID      UNKNOWN
arbitrary ATQA     UNKNOWN
arbitrary SAK      UNKNOWN
```

Do not advertise these as features until proven.

---

# 29. Peer-to-peer / NFCIP-1

ST21NFCD documents active and passive P2P, initiator and target.

Modern Android removed/deemphasized Android Beam, but LieppOS controls the framework and can investigate direct NCI/NFA P2P support.

Potential lab features:

- LLCP diagnostics;
- SNEP/test messaging;
- initiator/target mode tests;
- active vs passive mode selection;
- peer activation trace.

This is lower priority than reader/writer, HCE and observe mode.

---

# 30. Antenna / RF capability

ST21NFCD family advertises:

- enhanced active load modulation;
- TX drive up to 1.3 W;
- support for small / metal-frame antennas;
- optional external TX DC/DC support.

These are hardware capabilities, not permission to increase RF power arbitrarily.

Before exposing RF tuning:

1. extract the Ulefone NFC antenna schematic/DT/config evidence if available;
2. decode stock ST RF configuration;
3. identify regulatory/tuning parameters;
4. preserve stock values;
5. distinguish diagnostic readout from writable tuning.

LieppOS should initially expose only **read-only RF diagnostics**.

---

# 31. Arbitrary UID / tag emulation research

This is a major desired Flipper-like capability but currently **unproven**.

Research order:

1. inspect CORE_GET_CONFIG results;
2. enumerate standard NCI listen-mode configuration;
3. search ST HAL for proprietary listen parameters;
4. diff config blobs across public ST devices if available;
5. query vendor commands read-only;
6. test only with a controlled reader and a non-production LieppOS build.

Possible outcomes:

```text
A. UID/ATQA/SAK configurable through NFCC
B. partially configurable
C. randomized/fixed by controller
D. only off-host SE can control them
E. firmware hardcodes them
```

No conclusion yet.

---

# 32. Ultralight / NTAG emulation research

Reader/writer support for Type 2 tags does not mean the controller can emulate a Type 2 memory tag from the Android host.

To get Flipper-like NTAG emulation we would need:

- listen-mode Type-2 protocol support;
- host access early enough in anticollision/command processing;
- controllable UID/ATQA/SAK;
- command-level memory response handling;
- acceptable timing.

No public ST21NFCD documentation currently proves host-driven Type-2 tag emulation.

Classification:

```text
UNKNOWN / low-confidence
```

---

# 33. MIFARE Classic emulation research

ST advertises Classic card emulation specifically **through SWP-CLT**.

Therefore the likely model is Secure Element/UICC-assisted contactless emulation, not arbitrary Android-host Classic card emulation.

LieppOS should:

1. inspect whether the board has an appropriate SWP-connected SE/UICC;
2. inventory NFCEEs;
3. identify CLT routes/features;
4. inspect HCI/SWP events.

Host-driven arbitrary Classic cloning should remain **unproven**.

---

# 34. Raw RF / transparent mode

No public ST21NFCD source used here documents a general host-controlled transparent RF mode comparable to a dedicated NFC RF frontend such as ST25R3916.

Therefore:

```text
arbitrary modulation          LIKELY-BLOCKED / UNKNOWN
raw ADC/RF waveform capture   LIKELY-BLOCKED
fully custom anticollision    LIKELY-BLOCKED unless hidden FW support
arbitrary PHY timing          LIKELY-BLOCKED unless hidden FW support
```

This is the main class of feature where a Flipper-style dedicated frontend may remain superior.

Do not confuse raw NCI frames with raw RF waveforms.

---

# 35. LieppOS NFC Lab architecture

Recommended components:

```text
packages/apps/LieppOSNfcLab/
vendor/lieppos/nfc/
system/nfc extensions
hardware/st/nfc fork
native st21d service
```

Possible architecture:

```text
LieppOSNfcLab (UI)
       │ Binder/AIDL
       ▼
lieppos-st21d (privileged native service)
       ├── capability DB
       ├── NCI recorder
       ├── raw NCI console
       ├── observe-mode manager
       ├── polling-frame decoder
       ├── SE route inspector
       ├── FW/config inspector
       ├── ST trace decoder
       └── safe command policy
                │
                ▼
        ST AIDL NFC HAL
                │
                ▼
          st21nfc driver
                │
                ▼
             NFCC
```

Do not let arbitrary third-party Android apps open the raw controller directly by default.

Expose a permission such as:

```text
com.lieppos.permission.NFC_LAB
```

with signature/privileged protection.

---

# 36. Proposed LieppOS APIs

## Capability service

```text
getControllerIdentity()
getFirmwareVersion()
getConfigVersion()
getNciVersion()
getCapabilities()
getAndroidProprietaryCapabilities()
getSupportedProtocols()
getSecureElements()
```

## Trace API

```text
startNciTrace()
stopNciTrace()
startFirmwareTrace()
stopFirmwareTrace()
exportTrace()
```

## Observe API

```text
getObserveSupport()
setObserveMode()
setObservedTechnologies(A,B,F,V)
setExitFrameTable()
getExitFrameTable()
getPollingFrames()
```

## Discovery API

```text
getDiscoveryProtocols()
setDeveloperDiscoveryMask()
getPollingLoopAnnotations()
setPollingLoopAnnotations()
```

## Firmware API

Initially read-only:

```text
getFirmwareImageInfo()
getConfigImageInfo()
verifyImage()
getUpdateEligibility()
```

Only later:

```text
applyOfficialFirmware()
applyOfficialConfig()
```

with explicit recovery safeguards.

---

# 37. Safety model

Raw NFC control can break ordinary NFC, Secure Element routing, payment/transit operation or controller firmware.

Use levels:

## Level 0 — normal Android

No lab privileges.

## Level 1 — read-only diagnostics

Allowed:

- controller info;
- NCI logging;
- capability query;
- route inspection;
- firmware/config hashing;
- read-only traces.

## Level 2 — reversible RF/NCI developer settings

Allowed:

- observe mode;
- polling annotations;
- temporary discovery masks;
- trace controls.

Restore stock configuration automatically after process death/reboot.

## Level 3 — persistent config changes

Require:

- exact stock backup;
- validated field semantics;
- rollback plan;
- explicit confirmation.

## Level 4 — firmware update

Require:

- frozen authentic stock image;
- exact update protocol;
- loader/recovery proof;
- signature/version verification;
- uninterrupted power;
- no experimental images.

---

# 38. Static audit required on GQ5012BF1

Before any active controller experiments, inventory stock files:

```text
/vendor/firmware/
/vendor/etc/
/vendor/etc/nfc/
/vendor/lib64/
/vendor/lib64/hw/
/system/etc/
/product/etc/
```

Search for:

```text
st21
st54
nfc
libnfc-hal-st
STNFC_
FW_UPDATE
CONF_UPDATE
CUSTOM_PARAM
firmware_debug
CORE_CONF
NFA_PROPRIETARY_CFG
DEFAULT_ROUTE
DEFAULT_OFFHOST_ROUTE
DEFAULT_NFCF_ROUTE
OFFHOST_ROUTE
ISO_DEP_MAX_TRANSCEIVE
PRESENCE_CHECK
observe
polling
```

For every hit record:

```text
path
SHA256
ELF build ID if applicable
owner package
config semantics
runtime consumer
```

---

# 39. Exact controller identity task

This is the single most important unresolved hardware fact.

Determine:

```text
exact ST chip model
hardware revision
ROM/loader revision
firmware version
NCI version
firmware capability structure
vendor capability structure
host transport
clock source
IRQ/reset GPIO topology
SE/UICC/SWP topology
```

Sources:

- CORE_RESET_RSP/NTF;
- CORE_INIT_RSP;
- ST proprietary info commands;
- HAL logs;
- stock firmware metadata;
- DT;
- kernel driver probe logs.

Only after this should the generic "ST21NFCD feature set" be relabeled as exact GQ5012BF1 capabilities.

---

# 40. Capability closure ledger

Create a machine-readable TSV/CSV:

```text
feature
layer
public_ST_support
stock_GQ5012_evidence
capability_query
runtime_readonly_result
requires_write
requires_firmware
requires_secure_element
LieppOS_status
confidence
notes
```

Every feature in this document should eventually move to one of:

```text
PROVEN_AVAILABLE
PROVEN_AVAILABLE_LIEPPOS_EXPOSED
PROVEN_UNAVAILABLE
BOARD_NOT_CONNECTED
FW_NOT_SUPPORTED
SE_REQUIRED
BLOCKED_BY_SECURE_FW
UNKNOWN
```

---

# 41. Priority roadmap

## P0 — preserve current known-good NFC

- keep reconstructed stock-equivalent `st21nfc` 2.2.0.19;
- freeze stock HAL/config/firmware;
- hash every artifact;
- preserve normal NFC behavior.

## P1 — exact controller inventory

- chip/revision;
- FW/config versions;
- NCI version;
- NFCEE/SE topology;
- exact vendor config.

## P2 — complete NCI recorder

Capture stock initialization from power-on through discovery.

This should reveal Ulefone-specific vendor commands without guessing.

## P3 — capability query

Implement:

```text
NCI_ANDROID_GET_CAPS
```

and standard NCI capability/config enumeration.

## P4 — expose every normal protocol

Validate and expose:

```text
A
B
F
V
Type1-5
ISO15693
MIFARE Classic
Kovio
ISO18092/P2P
```

## P5 — observe mode

Implement:

```text
observe enable/query
per-tech mask
polling-frame notifications
gain/timestamp logging
exit-frame filters
```

## P6 — polling-loop customization

Implement and validate custom polling-loop annotation frames if supported.

## P7 — ST debug facilities

- firmware trace;
- HAL event log;
- hibernate/recovery states;
- vendor command dictionary.

## P8 — Secure Element routing

Map all UICC/eSE/eUICC/HCI/SWP capabilities.

## P9 — config blob reverse engineering

Decode every custom parameter before changing anything.

## P10 — advanced emulation

Investigate:

```text
custom UID
ATQA/SAK
Type-2 emulation
Type-B identity parameters
FeliCa identity parameters
Classic via SWP
```

## P11 — firmware authentication/update

Understand image format, signature, anti-rollback and recovery.

Only authentic images should be used until controller security is completely understood.

## P12 — silicon-boundary determination

Produce a final table of functions that cannot be exposed because they require unavailable RF hardware/firmware.

---

# 42. Target end state

The desired LieppOS experience:

```text
Settings
└── LieppOS NFC Lab
    ├── Controller
    │   ├── ST21 model / HW revision
    │   ├── FW / config version
    │   ├── NCI version
    │   ├── capabilities
    │   └── firmware/config inspector
    │
    ├── Reader
    │   ├── NFC-A
    │   ├── NFC-B
    │   ├── NFC-F
    │   ├── NFC-V
    │   ├── MIFARE Classic
    │   ├── Type 1-5
    │   └── Kovio
    │
    ├── APDU Lab
    │   ├── terminal
    │   ├── scripts
    │   ├── TLV decoder
    │   └── session capture
    │
    ├── Card Emulation
    │   ├── ISO-DEP HCE
    │   ├── NFC-F HCE
    │   ├── route inspector
    │   └── advanced listen-mode options
    │
    ├── Reader Analyzer
    │   ├── observe mode
    │   ├── A/B/F/V filters
    │   ├── polling frames
    │   ├── gain
    │   ├── timestamps
    │   └── exit-frame rules
    │
    ├── Discovery Lab
    │   ├── technology mask
    │   ├── custom polling frames
    │   ├── proprietary protocols
    │   └── power-saving state
    │
    ├── Secure Elements
    │   ├── NFCEE inventory
    │   ├── UICC/eSE/eUICC
    │   ├── HCI/SWP
    │   └── routing table
    │
    ├── Debug
    │   ├── NCI recorder
    │   ├── ST FW traces
    │   ├── HAL events
    │   ├── recovery/hibernate
    │   └── vendor command console
    │
    └── Developer
        ├── raw NCI
        ├── capability DB
        ├── temporary controller config
        └── official FW/config updater
```

---

# 43. What may ultimately exceed Flipper Zero

Assuming the exact controller exposes the necessary protocol features, the phone can exceed a small standalone NFC multitool in:

- APDU development;
- large-scale logging;
- HCE flexibility;
- dynamic card services;
- SQL/network-backed virtual cards;
- Secure Element routing inspection;
- Android framework integration;
- Wi-Fi/USB remote automation;
- scriptability;
- storage;
- visualization;
- protocol databases;
- NCI-level introspection;
- controller firmware/config management.

---

# 44. What may remain below Flipper Zero

Unless hidden ST21 functionality is found, dedicated NFC RF hardware likely retains an advantage in:

- transparent/raw RF access;
- arbitrary modulation;
- sub-protocol anticollision manipulation;
- exact tag-level UID/ATQA/SAK emulation;
- arbitrary Type-2 memory-tag emulation;
- deeply customized MIFARE Classic emulation;
- analog/RF experimentation.

The exact boundary must be measured, not assumed.

---

# 45. Research rules

1. **Query before modifying.**
2. Preserve every stock firmware/config/HAL artifact by SHA256.
3. Treat public ST21NFCD functionality as family evidence until exact silicon identity is proven.
4. Treat ST HAL code as implementation evidence, not proof that every command is accepted by this firmware.
5. Never fake capabilities in LieppOS UI.
6. Never patch controller firmware CRC/signature checks merely to make an image load.
7. Do not change Secure Element payment/transit routing during early research.
8. All controller writes should initially be volatile/reversible.
9. Every discovered GQ5012BF1-specific fact goes into `LieppOS/ulefone-gq5012bf1-research`.
10. Final objective is **maximum real capability with stock-oracle parity and recoverability**, not feature claims.

---

# 46. Current final assessment

## Already solved

```text
Linux ST21 transport/recovery driver:
    source reconstructed
    stock 2.2.0.19 behavior recovered
    54/54 stock kernel ABI requirements matched
```

## Publicly supported by the ST21NFCD family

```text
NCI 2.0
Type 1/2/3/4/5 reader/writer
ISO15693
MIFARE Classic reader/writer
Kovio
active/passive NFCIP-1 P2P
Type-A / Type-B card emulation
JIS X 6319-4 / NFC-F-family card emulation
Classic CE through SWP-CLT
eFlash firmware update
secure firmware update
SWP
I2C/SPI/HSUART host interface options
advanced power/wake features
```

## Publicly present in ST's Android stack

```text
firmware update
custom-parameter update
controller recovery
hibernate handling
firmware debug traces
HAL event logging
proprietary protocol configuration
MIFARE/15693/Kovio/B-prime protocol IDs
Secure Element/UICC/eSE routing
screen/switch-off CE configuration
USB-charging NFC mode
large ISO-DEP transfer configuration
observe-mode integration in current HAL
```

## Android proprietary NCI opportunities

```text
capability query
passive observe mode
per-technology observe mode
polling-frame notifications
frame timestamps
gain data
observe exit-frame filters
custom polling-loop frames
reader-mode annotation capability
power-saving capability
blank NCI command
```

## Biggest unknowns for this exact phone

```text
exact ST21 silicon/revision
installed FW version
installed config version
firmware/config filenames
firmware authentication details
anti-rollback
exact supported Android proprietary capabilities
MIFARE Classic enablement
Kovio enablement
B-prime support
observe-mode version
custom polling-frame support
ST FW trace availability
actual eSE/UICC/SWP wiring
arbitrary UID control
ATQA/SAK control
Type-2 emulation
Classic host emulation
RF tuning access
transparent/raw RF capability
```

These unknowns are the next research program.

---

# 47. Primary sources

## ST ST21NFCD product page

STMicroelectronics — ST21NFCD NFC controller:

https://www.st.com/en/secure-mcus/st21nfcd.html

Publicly documents NCI 2.0, reader/writer protocols, P2P, card emulation, MIFARE Classic, ISO15693, Kovio, SWP, eFlash update, secure firmware update, low-power/wake and RF hardware features.

## ST21NFCD data brief

https://www.st.com/resource/en/data_brief/st21nfcd.pdf

## AOSP/ST NFC HAL

Android Open Source Project — ST NFC HAL:

https://android.googlesource.com/platform/hardware/st/nfc/

Current ST21 source tree:

https://android.googlesource.com/platform/hardware/st/nfc/+/refs/heads/main/st21nfc/

Example ST HAL configuration:

https://android.googlesource.com/platform/hardware/st/nfc/+/refs/heads/main/st21nfc/libnfc-hal-st-example.conf

Current AIDL ST HAL implementation:

https://android.googlesource.com/platform/hardware/st/nfc/+/sdk-release/aidl/hal_st21nfc.cc

Useful implementation evidence includes firmware/config update state machines, proprietary protocol configuration, Secure Element routes, debug facilities and observe-mode integration.

## Android proprietary NCI specification

https://source.android.com/docs/core/connect/android-proprietary-nci-commands

Defines Android NFCC capability queries, observe mode, polling-frame notifications, per-technology observation, exit-frame filters, custom polling-loop frames, power-saving commands and related notifications.

## ST HAL observe-mode implementation history

Per-technology observe-mode support commit:

https://android.googlesource.com/platform/hardware/st/nfc/+/8bc67f5b72935c4caf3a2d7ae8b5ba6ce0a1846f

---

# 48. Repo location

This document should live at:

```text
LieppOS/ulefone-gq5012bf1-research/kernel/st21-lieppos.md
```

Future NFC research should update this document rather than creating contradictory standalone capability lists.

