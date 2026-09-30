# LieppOS — XIAO nRF52840 + Wio-SX1262 Meshtastic / Reticulum Master Research

**Project:** LieppOS  
**Target phone:** Ulefone Armor 29 Thermal (`gq5012bf1`)  
**Radio kit:** Seeed XIAO nRF52840 + Wio-SX1262 Kit  
**Region:** Lithuania / EU868  
**Preferred host link:** USB-C OTG / USB serial, not Bluetooth  
**Status:** RNode bring-up and Reticulum/LXMF host-side validation complete; hybrid Meshtastic + Reticulum design defined.

> Intended repo destination: `LieppOS/ulefone-gq5012bf1-research`

---

## 1. Goal

The long-term goal is a compact radio accessory for LieppOS that can support:

- personal Meshtastic messaging,
- Reticulum / LXMF messaging,
- low-power off-grid operation,
- optional temporary mesh-relay duty,
- phone-controlled operating profiles,
- one USB-C connection to the Ulefone,
- ideally one XIAO + one SX1262 instead of separate radios.

The preferred operating philosophy is **personal communications first**. The device should not consume battery, RF airtime, or network resources relaying other people's traffic unless the user explicitly enables a helper/router profile from the phone.

---

## 2. Hardware

### 2.1 Exact kit

Seeed XIAO nRF52840 + Wio-SX1262 Kit for Meshtastic, Seeed SKU `102010710`.

Core hardware:

| Component | Details |
|---|---|
| MCU | Nordic nRF52840 |
| CPU | Cortex-M4F, 64 MHz |
| RAM | 256 KB |
| Internal flash | 1 MB |
| Additional onboard flash | 2 MB |
| LoRa radio | Semtech SX1262 |
| Kit radio range | approximately 862–930 MHz |
| Intended local band | EU868 |
| Host connection | USB CDC / USB-C OTG |
| GNSS | no onboard GNSS on base kit |

Target physical topology:

```text
Ulefone / LieppOS
       │
       │ USB-C OTG
       ▼
XIAO nRF52840
       │ SPI
       ▼
Wio-SX1262
       │
       ▼
LoRa / EU868
```

The kit ships with Meshtastic firmware, but was successfully converted into a working RNode during this research.

---

## 3. Recommended LieppOS software architecture

Long-term architecture:

```text
LieppOS apps
    │
    ▼
LieppOS Mesh / Radio Service
    │
    ├── Meshtastic backend
    │      └── USB Meshtastic PhoneAPI
    │
    ├── Reticulum backend
    │      ├── native RNode interface
    │      └── Meshtastic tunnel interface
    │
    └── Internet / LAN Reticulum interfaces
```

This allows the phone to treat the external hardware as a radio peripheral while keeping protocol intelligence and profile management in LieppOS.

---

# Part I — Native RNode / Reticulum Bring-up

## 4. RNode firmware donor and exact-board support

Reticulum itself runs on the host. The XIAO runs **RNode firmware** and behaves as a USB-connected radio modem.

The relevant community RNode_Firmware_CE work added exact-board support for the Seeed XIAO nRF52840 + Wio-SX1262.

Important board IDs:

```text
PRODUCT_XIAO_NRF = 0x18
BOARD_XIAO_NRF   = 0x53
MODEL_19         = 0x19
```

`MODEL_19` represents XIAO nRF52840 + Wio-SX1262 in the 868 MHz-class range.

Build target:

```text
FQBN: Seeeduino:nrf52:xiaonRF52840
BOARD_MODEL=0x53
BOARD_VARIANT=0x19
```

Pinned research branch/commit used:

```text
Repository:
https://github.com/SP5MI/RNode_Firmware_CE.git

Branch:
fix/nrf52-firmware-hash

Commit:
03024a6c0a9c1df246ac385df519ad186bbeeb02

Commit message:
Use linker symbols for NRF52 application size in firmware validation
```

Relevant upstream PR:

```text
https://github.com/liberatedsystems/RNode_Firmware_CE/pull/115
```

---

## 5. XIAO nRF52840 bootloader layout

The Seeed OTAFIX bootloader layout places the application at:

```text
APPLICATION_START = 0x27000
```

Not:

```text
0x26000
```

The map/ELF generated during this project confirmed the application starts exactly at `0x27000`.

The linker-symbol hash fix in the selected branch uses the real linked application extent instead of relying on an incorrect hard-coded firmware-size address.

---

## 6. Exact Wio-SX1262 board pin mapping used

The selected board definition used:

```text
CS      D4
SCK     D8
MOSI    D10
MISO    D9
BUSY    D3
DIO1    D1
RESET   D2
RXEN    D5
TXEN    -1

TX LED  pin 11
RX LED  pin 12
GREEN   pin 13
LED_ON  LOW
LED_OFF HIGH
```

Radio features included:

```text
HAS_TCXO = true
DIO2_AS_RF_SWITCH = true
```

For the XIAO target, TCXO voltage configuration was already correct at 1.8 V.

---

## 7. First major failure: radio not detected

Initial firmware built and flashed successfully, but the actual firmware hash returned all zeroes:

```text
0000000000000000000000000000000000000000000000000000000000000000
```

Raw serial output revealed the important boot message:

```text
No radio module found
```

This proved the real failure was the SX1262 `preInit()` probe.

Startup chain:

```text
SX1262 preInit()
     ↓
probe fails
     ↓
modems_installed = false
     ↓
device_init() skipped
     ↓
device_validate_partitions() skipped
     ↓
actual firmware hash remains all zeroes
```

The zero hash was therefore a symptom of radio initialization failure, not a standalone firmware-hash defect.

---

## 8. SX1262 `preInit()` bugs found

Two concrete issues were found in `Radio.cpp`.

### 8.1 No radio reset before probing

`preInit()` started SPI and immediately probed the SX1262 sync-word registers.

The XIAO/Wio radio can retain state across an MCU-only reset, so the SX1262 needed an explicit hardware reset before the sync-word probe.

### 8.2 Public LoRa sync-word typo

The code checked:

```text
0x4434
```

but the standard SX126x public LoRa sync word is:

```text
0x3444
```

The private sync word:

```text
0x1424
```

was already correct.

---

## 9. Working `Radio.cpp` patch

The successful local patch added an XIAO-only radio reset before the probe and corrected the public sync word.

Core patch logic:

```cpp
#if BOARD_MODEL == BOARD_XIAO_NRF
  if (_busy != -1) {
    pinMode(_busy, INPUT);
  }

  // The Wio-SX1262 can retain radio state across an MCU-only reset.
  // Reset it before probing the sync-word registers.
  reset();
  delay(20);
#endif
```

And:

```text
0x4434 → 0x3444
```

A temporary failure diagnostic was also added:

```text
SX1262 sync probe failed: 0x....
```

The working patch was committed locally as:

```text
de2424d7
Fix SX1262 preInit on XIAO nRF52840
```

---

## 10. Successful patched build

Patched build:

```text
Sketch uses 220536 bytes
Global variables use 23496 bytes
```

Patched packaged firmware SHA-256:

```text
0aef30b5e3dfcfe17ef629b81dc10cb67e56af0c25e7f78102770093a127feac
```

The firmware flashed successfully through the Seeed nRF52 DFU path.

---

## 11. USB identities observed

### Bootloader

```text
VID:PID 239a:810b
Vendor: Seeed_Studio
Model: XIAO-BOOT
Serial: C698397CF7DDBB03
```

### Running application

```text
VID:PID 2886:8044
Vendor: Seeed
Model: XIAO_nRF52840
Serial: C698397CF7DDBB03
```

The Linux `/dev/ttyACM*` number can change after reset, so stable discovery by USB serial or `/dev/serial/by-id/` is preferred.

Stable by-id entry observed:

```text
/dev/serial/by-id/usb-Seeed_XIAO_nRF52840_C698397CF7DDBB03-if00
```

---

## 12. Provisioning

Manual provisioning was required because `rnodeconf -r` initially reported:

```text
No signing key found
```

Keys were generated with:

```bash
rnodeconf -k
```

Then provisioning completed with:

```bash
rnodeconf /dev/ttyACM0 \
  -r \
  --platform NRF52 \
  --model 19 \
  --product 18 \
  --hwrev 1
```

Successful result included:

```text
EEPROM checksum correct
Device signature validated
EEPROM Bootstrapping successful!
```

Do not re-run provisioning unless intentionally resetting device identity.

---

## 13. Host `rnodeconf` model patch

The installed `rnodeconf` did not know the new exact-board product/model IDs.

Host-side additions used:

```python
0x18: "Seeed XIAO nRF52840 Wio-SX1262",
```

and:

```python
0x19: [862000000, 930000000, 22, "862 - 930 MHz", None, "SX1262"],
```

`None` for firmware filename is intentional because this is a locally built development firmware rather than an official downloadable release artifact.

---

## 14. Firmware validation success

After the `Radio.cpp` fix, `rnodeconf -L` returned the actual patched firmware hash:

```text
0aef30b5e3dfcfe17ef629b81dc10cb67e56af0c25e7f78102770093a127feac
```

Then the target firmware hash was written.

Immediately afterward the board temporarily stopped responding because RNode intentionally resets the nRF52 when the firmware hash changes while the current boot is not yet validated.

After reboot, both values matched:

```text
Target:
0aef30b5e3dfcfe17ef629b81dc10cb67e56af0c25e7f78102770093a127feac

Actual:
0aef30b5e3dfcfe17ef629b81dc10cb67e56af0c25e7f78102770093a127feac
```

This physically proved:

- SX1262 `preInit()` succeeds,
- `modems_installed == true`,
- device initialization runs,
- EEPROM target hash loads correctly,
- linker-derived nRF52 application hashing works,
- `0x27000` application start is correct,
- persistent firmware validation survives reboot.

---

## 15. RNode LED behavior

For this board definition:

```text
red LED  → TX indication
blue LED → RX indication
```

Occasional red flashes are therefore consistent with transmit/status activity.

The fatal boot error indicator is a continuous alternating RX/TX pattern, not an occasional isolated red blink.

---

# Part II — Reticulum Host Validation

## 16. First working RF profile

Initial test profile:

```text
Frequency:       869.525 MHz
Bandwidth:       125 kHz
TX power:        7 dBm
Spreading factor: 8
Coding rate:      5 (4/5)
```

The low initial TX power was chosen for bench testing.

Antenna must be attached before transmitting.

Regulatory limits and duty-cycle rules must be checked against current EU/Lithuanian requirements before higher-power or sustained operation.

---

## 17. Reticulum test configuration

A dedicated test instance was created:

```text
~/.reticulum-xiao-test
```

Example interface:

```ini
[[XIAO RNode]]
  type = RNodeInterface
  enabled = yes
  port = /dev/ttyACM0

  frequency = 869525000
  bandwidth = 125000
  txpower = 7
  spreadingfactor = 8
  codingrate = 5
```

Later the isolated shared instance was named:

```ini
instance_name = xiao-test
```

to prevent collisions with `rns/default`.

---

## 18. Reticulum RNode interface validated

`rnstatus` reported:

```text
RNodeInterface[XIAO RNode]
Status    : Up
Mode      : Full
Rate      : 3.12 kbps
MTU       : 508
Noise Fl. : approximately -110 / -111 dBm
Interference: none observed
```

The daemon also confirmed:

```text
frequency      869.525 MHz
bandwidth      125.0 kHz
TX power       7 dBm
SF             8
CR             5
symbol time    2.05 ms
symbol rate    488 baud
preamble       22 symbols / ~45 ms
CSMA slot      24 ms
DIFS           48 ms
```

This proves:

```text
Linux Reticulum
      ↓
RNodeInterface
      ↓
USB CDC
      ↓
XIAO nRF52840
      ↓
SX1262
```

---

## 19. LoRa TX validated

A local Reticulum announce was generated.

Afterward:

```text
RNodeInterface[XIAO RNode]
Traffic ↑183 B
Airtime 0.01% (1h)
```

This proves the single-node TX chain:

```text
Reticulum application
      ↓
shared Reticulum instance
      ↓
RNodeInterface
      ↓
USB
      ↓
nRF52840
      ↓
SX1262
      ↓
real LoRa airtime
```

True RF RX is still not physically validated because there is currently no second compatible transmitter.

---

# Part III — Public Reticulum / LXMF Validation

## 20. Public Reticulum TCP transport

A second interface was added:

```ini
[[RMAP World]]
  type = TCPClientInterface
  enabled = yes
  target_host = rmap.world
  target_port = 4242
```

The test instance uses:

```ini
enable_transport = No
share_instance = Yes
instance_name = xiao-test
```

This keeps the machine as an endpoint rather than volunteering it as a general Reticulum transport node.

`rnstatus` confirmed simultaneously:

```text
Shared Instance[rns/xiao-test]            Up
TCPInterface[RMAP World/rmap.world:4242] Up
RNodeInterface[XIAO RNode]                Up
```

This is an important architectural result: Internet Reticulum and LoRa RNode can coexist inside one host Reticulum instance.

---

## 21. Shared-instance collision and fix

An earlier restart accidentally attached to another existing:

```text
rns/default
```

instance.

The fix was to explicitly set:

```ini
instance_name = xiao-test
```

This allows multiple independent Reticulum stacks on the same Linux host.

---

## 22. Controlled LXMF end-to-end test

Because a published remote support LXMF destination was not reachable at that moment, a controlled second Reticulum instance was created:

```text
instance_name = peer-test
```

It used an independent TCP connection to:

```text
rmap.world:4242
```

Receiver LXMF address:

```text
f156fb3792519fe7e5323e180c33dd24
```

Sender LXMF address:

```text
c43d699999b71455e699c7c59788bfb8
```

The sender:

- found a path,
- established a Reticulum link,
- measured roughly 295 ms RTT,
- transferred the LXMF message,
- reached progress `1.0`,
- received a positive delivery notification,
- entered LXMF state `8` / delivered.

The independent receiver printed the exact expected title and body.

This validated:

```text
xiao-test
   │
   │ TCP
   ▼
rmap.world
   │
   │ public Reticulum
   ▼
rmap.world
   │
   │ independent TCP connection
   ▼
peer-test
   │
   ▼
LXMF receiver
```

This was not a local shared-instance shortcut.

---

## 23. LXMF signature nuance

The receiver printed:

```text
SIG : False
```

This did **not** invalidate the successful encrypted Reticulum link or LXMF delivery.

LXMF distinguishes at least:

```text
SOURCE_UNKNOWN
SIGNATURE_INVALID
```

The test callback did not print `message.unverified_reason`, so the exact reason was not proven.

Because the sender identity was not explicitly announced before the message, `SOURCE_UNKNOWN` is a plausible explanation.

Future test:

```python
print(message.unverified_reason)
```

and announce the sender delivery identity before sending.

---

# Part IV — Meshtastic + Reticulum on One XIAO

## 24. Three possible dual-protocol designs

### Option A — Meshtastic firmware + Reticulum tunnel

**Recommended hybrid experiment.**

Meshtastic reserves:

```text
PortNum 76
RETICULUM_TUNNEL_APP
```

for fragmented Reticulum packets.

Architecture:

```text
LieppOS Reticulum
      ↓
MeshtasticRNSInterface
      ↓
fragment RNS packet
      ↓
Meshtastic Port 76
      ↓
Meshtastic PhoneAPI over USB
      ↓
XIAO Meshtastic firmware
      ↓
SX1262
```

This allows normal Meshtastic traffic and tunneled Reticulum traffic to coexist on one MCU and one radio.

Important: this is **Reticulum over Meshtastic**, not native RNode RF.

---

### Option B — Dual-boot / dual-personality

Store or manage both:

- Meshtastic firmware,
- RNode firmware.

Only one is active at a time.

Advantages:

- full native Meshtastic behavior,
- full native RNode behavior,
- simpler protocol isolation.

Disadvantage:

- no simultaneous operation.

The XIAO's 2 MB auxiliary flash makes an alternate-image design conceptually possible, but bootloader and partition handling would need explicit engineering.

---

### Option C — merged native RNode + native Meshtastic firmware

Technically possible, but not recommended.

Both stacks would want to control:

- SX1262 radio state,
- frequency,
- BW/SF/CR,
- RX timing,
- CSMA,
- TX queue,
- retransmission policy.

A custom scheduler would be required:

```text
Meshtastic stack ─┐
                  ├── radio arbiter ── SX1262
RNode stack ──────┘
```

If the two stacks use different PHY settings, the radio will miss packets whenever tuned to the other configuration.

For truly independent simultaneous native Meshtastic + native RNode, two radios remain the cleanest architecture.

---

# Part V — Recommended Hybrid Design

## 25. Can both logical interfaces work at the same time?

Yes.

In hybrid mode:

```text
LieppOS
├── Meshtastic interface
│      └── normal Meshtastic traffic
│
└── Reticulum interface
       └── Reticulum packets
              ↓
       RETICULUM_TUNNEL_APP 76
```

Both are active concurrently at the software level.

But there is only one physical radio stack:

```text
Meshtastic MAC / mesh
        ↓
      SX1262
```

So both logical protocols share:

- the same LoRa channel,
- the same RF airtime,
- the same Meshtastic routing behavior,
- the same congestion,
- the same duty-cycle budget.

---

## 26. Host-side `MeshtasticRNSInterface`

A proper LieppOS implementation should create a custom Reticulum interface that:

1. receives an RNS packet,
2. fragments it,
3. assigns packet/fragment IDs,
4. sends fragments as Meshtastic Port 76 payloads,
5. receives Port 76 payloads,
6. reorders and reassembles them,
7. handles missing fragments and timeouts,
8. deduplicates repeated fragments,
9. validates completed packet integrity,
10. injects the reconstructed RNS packet back into Reticulum.

This should be implemented as a robust production transport, not merely the earlier community proof-of-concept.

---

# Part VI — Personal Modem Philosophy

## 27. User requirement

The primary requirement is **personal send/receive**, not being a permanent public mesh helper.

Desired behavior:

```text
send my messages/content       YES
receive my messages/content    YES
Meshtastic                     YES
Reticulum/LXMF                 YES
relay random third-party data  NO by default
GPS beaconing                  NO by default
telemetry                      NO by default
MQTT                           NO by default
Wi-Fi                          NO by default
neighbor/range testing         NO by default
```

This is particularly important for battery and RF efficiency in off-grid / disaster scenarios.

---

## 28. Important correction: movement is not the main cost

Simply carrying the station while moving is not what significantly increases energy use.

Major costs are:

- relaying other nodes' packets,
- frequent transmit activity,
- constant receive listening,
- GPS usage and position beacons,
- telemetry,
- neighbor-info exchanges,
- Wi-Fi,
- MQTT,
- BLE if not needed,
- repeated retry traffic.

Occasional user-generated text/LXMF traffic can be relatively light compared with running as active mesh infrastructure.

---

# Part VII — LieppOS Radio Profiles

## 29. Phone should be the control plane

The preferred design is:

```text
LieppOS
   │
   │ profile/config commands over USB
   ▼
XIAO
   │
   ▼
SX1262
```

LieppOS chooses the operating profile. The XIAO applies it.

Meshtastic's PhoneAPI already provides access to device, power, LoRa, position, network, channel and module configuration. Some changes can require a radio reboot; LieppOS should treat this as:

```text
apply complete profile
      ↓
persist
      ↓
reboot XIAO if required
      ↓
USB re-enumeration
      ↓
automatic reconnect
      ↓
verify active state
```

---

## 30. Recommended profile set

### 30.1 SURVIVAL

Goal: maximize battery life.

Suggested behavior:

- no relaying,
- no automatic location,
- no telemetry,
- no MQTT,
- Wi-Fi off,
- BLE off when USB is used,
- aggressive power saving,
- explicit-user TX only,
- optionally duty-cycled RX / periodic receive windows.

Tradeoff:

**incoming messages may be delayed while the radio sleeps.**

---

### 30.2 LISTEN

Goal: personal receive availability without helping the mesh.

Suggested behavior:

- no relaying,
- no telemetry,
- no automatic location broadcasts,
- no MQTT,
- USB host active,
- continuous or near-continuous LoRa RX.

Tradeoff:

higher idle draw than SURVIVAL.

---

### 30.3 ACTIVE

Goal: normal personal communications.

Suggested behavior:

- immediate personal send/receive,
- no infrastructure duty,
- Meshtastic traffic enabled,
- Reticulum tunnel enabled,
- normal RX availability,
- standard retry policy.

---

### 30.4 EMERGENCY

Goal: temporary maximum reach/reliability.

Suggested behavior:

- higher TX power within current legal limits,
- potentially larger retry budget,
- optional user-enabled distress beacon,
- optional temporary location sharing,
- explicit timeout or manual exit back to previous profile.

Example:

```text
Emergency for 15 min
Emergency for 1 hour
Emergency until battery reaches 20%
Emergency until manually disabled
```

---

# Part VIII — Personal vs Mesh Helper Toggle

## 31. Desired phone UI

Recommended role control:

```text
[ PERSONAL ]  [ HELP MESH ]  [ BASE / ROUTER ]
```

This lets the user decide when the node should contribute infrastructure resources.

---

## 32. PERSONAL

Goal:

**only personal traffic.**

Desired policy:

- send/receive user's Meshtastic traffic,
- Reticulum tunnel remains enabled,
- no third-party rebroadcasting,
- no automatic telemetry/location unless explicitly enabled,
- MQTT off,
- Wi-Fi off,
- BLE off if USB is the host,
- low practical TX power.

### Meshtastic role caveat

A correction discovered during research:

`CLIENT_MUTE` is not a guaranteed strict "never relay anything" mode.

Current Meshtastic behavior/documentation treats normal client-class roles as mesh participants, and `CLIENT_MUTE` primarily suppresses some of the node's own periodic broadcasts.

Meshtastic has a `rebroadcast_mode = NONE`, but current standard-role constraints do not make this a clean drop-in solution for a normal messaging client.

Therefore, for a **strict Personal profile**, the preferred implementation is a small custom Meshtastic firmware policy/patch:

```text
if profile == PERSONAL:
    do not rebroadcast third-party packets
```

while preserving direct user messaging and Port 76 Reticulum tunneling.

---

## 33. HELP MESH

Goal:

temporarily help nearby people.

Recommended behavior:

- allow mesh rebroadcasting,
- keep user's own Meshtastic messaging active,
- keep Reticulum tunnel active,
- use `CLIENT`-class behavior,
- preferably restrict rebroadcasting to the desired local mesh/policy where possible,
- do not automatically enable MQTT.

Suggested timed controls:

```text
Help mesh for:
- 15 minutes
- 1 hour
- until battery reaches X%
- until manually disabled
```

When the timer or battery condition is met, return automatically to PERSONAL.

---

## 34. BASE / ROUTER

Goal:

intentionally turn the device into infrastructure.

Use only when deliberately placed somewhere useful:

- elevated window,
- rooftop,
- hill,
- fixed powered location.

Possible roles:

- ROUTER,
- ROUTER_LATE.

This is not recommended as the normal handheld/moving profile because it spends more battery and RF airtime supporting other nodes.

---

# Part IX — Disaster / "Apocalypse" Design Rationale

## 35. Why this profile model matters

In an infrastructure-loss scenario:

- battery is scarce,
- RF airtime is scarce,
- unnecessary RF activity can reduce privacy,
- cellular data may be absent,
- LoRa links may be the only low-power long-range option.

The preferred default is therefore:

```text
quiet
personal
encrypted
USB-controlled
no public relay duty
```

Then the user can deliberately switch to:

```text
HELP MESH
```

when there is a reason to contribute battery and radio airtime to the local community.

This gives the user direct control over the tradeoff between:

```text
personal endurance  ←────────→  community mesh coverage
```

---

## 36. Receive-power tradeoff

There is an unavoidable physical tradeoff:

```text
instant receive
    ↓
radio must listen more often
    ↓
higher idle power
```

versus:

```text
maximum endurance
    ↓
radio sleeps more
    ↓
messages can arrive late
```

Potential SURVIVAL policy:

```text
sleep
↓
wake for RX window
↓
listen briefly
↓
sleep again
```

Exact timings should be measured experimentally on the final XIAO firmware and battery source.

---

# Part X — Recommended Final Product Behavior

## 37. Ideal LieppOS experience

The phone should show something like:

```text
Radio: XIAO nRF52840 + SX1262
USB: Connected
Meshtastic: Ready
Reticulum: Ready

Profile:
[ SURVIVAL ]
[ LISTEN   ]
[ ACTIVE   ]
[ EMERGENCY ]

Mesh role:
[ PERSONAL ]
[ HELP MESH ]
[ BASE     ]

TX Power: 7 dBm
Relay: OFF
Position beacon: OFF
Telemetry: OFF
MQTT: OFF
Wi-Fi: OFF
```

The phone should be the authority for:

- profile selection,
- relay policy,
- TX power,
- receive behavior,
- Meshtastic settings,
- Reticulum tunnel enable/disable,
- emergency settings,
- automatic battery thresholds,
- timed Help-Mesh operation.

---

## 38. Recommended default

For normal portable use:

```text
Profile: LISTEN or ACTIVE
Mesh role: PERSONAL
USB host: ON
Wi-Fi: OFF
MQTT: OFF
BLE: OFF
Position: OFF
Telemetry: OFF
Relay: OFF
```

This preserves immediate personal communications without spending power on infrastructure work.

---

# Part XI — Current Validation Matrix

| Capability | State |
|---|---|
| XIAO nRF52840 firmware build | ✅ |
| Seeed DFU flashing | ✅ |
| Exact board application start `0x27000` | ✅ |
| SX1262 detected | ✅ |
| `Radio.cpp` preInit fix | ✅ |
| EEPROM provisioning | ✅ |
| Device signature validation | ✅ |
| Firmware target hash | ✅ |
| Firmware actual hash | ✅ |
| Target == actual after reboot | ✅ |
| RNode USB host connection | ✅ |
| Reticulum RNodeInterface | ✅ |
| RF configuration | ✅ |
| Noise-floor reporting | ✅ |
| LoRa TX airtime | ✅ |
| Public Reticulum TCP transport | ✅ |
| Independent Reticulum instances | ✅ |
| LXMF path discovery | ✅ |
| LXMF encrypted link | ✅ |
| LXMF transfer | ✅ |
| LXMF delivery confirmation | ✅ |
| LoRa packet RX from second RF transmitter | ⏳ not yet physically tested |
| Meshtastic + Reticulum Port 76 hybrid | 🧪 design/prototype next |
| Strict Personal no-relay Meshtastic policy | 🧪 custom firmware work |
| LieppOS Android USB integration | 🧪 next major integration step |

---

# Part XII — Next Engineering Steps

## 39. Immediate priorities

### Step 1 — Preserve upstreamable RNode patch

Current working RNode patch exists at local commit:

```text
de2424d7
Fix SX1262 preInit on XIAO nRF52840
```

Before upstreaming, consider removing the temporary serial debug print while retaining:

- XIAO BUSY input configuration,
- hardware reset before preInit probe,
- `0x4434 → 0x3444` correction.

Then rebuild/revalidate the hash and hardware one final time.

---

### Step 2 — Prototype Meshtastic hybrid mode

Flash current supported Meshtastic firmware to the XIAO and verify:

- USB PhoneAPI,
- normal personal messaging,
- Port 76 send/receive API access,
- simultaneous normal Meshtastic + Reticulum-tunnel traffic.

Implement a host prototype:

```text
MeshtasticRNSInterface
```

with:

- fragmentation,
- reassembly,
- packet IDs,
- duplicate suppression,
- timeout handling,
- integrity checking.

---

### Step 3 — Implement strict PERSONAL policy

Patch Meshtastic if required so that:

```text
PERSONAL = never rebroadcast third-party traffic
```

while retaining:

- personal Meshtastic send/receive,
- Port 76 Reticulum tunneling,
- control from PhoneAPI/USB.

---

### Step 4 — Implement LieppOS profile manager

LieppOS should expose:

```text
SURVIVAL
LISTEN
ACTIVE
EMERGENCY

PERSONAL
HELP MESH
BASE / ROUTER
```

The service should apply complete configurations, handle XIAO reboot/re-enumeration, and verify actual active state.

---

### Step 5 — Android / Ulefone USB integration

Target:

```text
Ulefone Armor 29 / LieppOS
          │
       USB-C OTG
          │
      XIAO radio
```

First determine whether Android exposes the board as:

```text
/dev/ttyACM*
```

through kernel CDC-ACM support.

If not, use Android's USB Host API directly.

Long-term preference for a polished LieppOS service is likely Android USB Host access because it provides:

- hotplug handling,
- USB permission flow,
- VID/PID detection,
- stable app ownership,
- no dependency on global `/dev/ttyACM*` permissions.

Known application USB identity:

```text
VID 0x2886
PID 0x8044
Serial C698397CF7DDBB03
```

---

# Part XIII — Design Decision Summary

## 40. Current recommendation

### For native Reticulum

Keep the proven RNode firmware path available.

It is now physically validated and should remain an optional native-Reticulum mode.

### For one-radio simultaneous Meshtastic + Reticulum

Prototype:

```text
Meshtastic firmware
+
RETICULUM_TUNNEL_APP Port 76
```

This is the preferred one-radio hybrid because both logical protocols can operate at the same time without trying to make two independent MAC/radio stacks fight over one SX1262.

### For normal portable/off-grid use

Default to:

```text
PERSONAL
+
LISTEN or ACTIVE
```

### For battery emergency

Use:

```text
PERSONAL
+
SURVIVAL
```

### When deliberately helping others

Temporarily enable:

```text
HELP MESH
```

### When deployed as infrastructure

Use:

```text
BASE / ROUTER
```

---

# Sources / References

Primary project and upstream references discussed during this research:

- Seeed XIAO nRF52840:
  - https://wiki.seeedstudio.com/XIAO_BLE/
- Exact Seeed Meshtastic kit:
  - https://www.seeedstudio.com/XIAO-nRF52840-Wio-SX1262-Kit-for-Meshtastic-p-6400.html
- RNode Firmware CE PR for XIAO/Wio:
  - https://github.com/liberatedsystems/RNode_Firmware_CE/pull/115
- Working research branch:
  - https://github.com/SP5MI/RNode_Firmware_CE
- RNode firmware:
  - https://github.com/markqvist/RNode_Firmware
- Reticulum:
  - https://github.com/markqvist/Reticulum
  - https://reticulum.network/
- LXMF:
  - https://github.com/markqvist/LXMF
- Meshtastic firmware:
  - https://github.com/meshtastic/firmware
- Meshtastic protocol SDK docs:
  - https://github.com/meshtastic/meshtastic-sdk/blob/main/docs/protocol.md
- Meshtastic protobuf PortNums:
  - https://github.com/meshtastic/protobufs/blob/master/meshtastic/portnums.proto
- Reticulum-over-Meshtastic community discussion:
  - https://github.com/markqvist/Reticulum/discussions/973
- RMAP public Reticulum transport:
  - https://rmap.world/info.html

---

# Final Current State

The hardware is no longer speculative.

The XIAO nRF52840 + Wio-SX1262 has been physically proven as a working USB RNode with real LoRa TX, and Reticulum/LXMF has been proven from host application through public Reticulum transport to an independent receiver.

The next major research phase is not basic bring-up. It is productization:

1. **Meshtastic + Reticulum hybrid over Port 76**
2. **strict personal/no-relay behavior**
3. **phone-controlled power/mesh profiles**
4. **Ulefone/LieppOS USB integration**
5. **eventual second-radio or public-RF test for physical LoRa RX validation**
