# uSmart TODO Suggestions and Accessory Ideas

Target device: **Ulefone Armor 29 Pro Thermal (GQ5012BF1 / MT6878T)**

Purpose: maintain a broad backlog of possible LieppOS/uSmart projects beyond the current Meshtastic and walkie-talkie work.

---

## Current working model

Current reverse engineering supports the following high-level model:

```text
MT6375 OTG
    ↓
extcon-mtk-usb
    ↓
shared USB0 / MTU3 / USB2 fabric + UVC routing
    ↓
uSmart connector
```

SC851x has been excluded from the uSmart VBUS/control path.

The exact physical six-pin order is still unresolved.

Current likely functional set:

```text
VBUS
GND
USB D+
USB D-
ID / accessory detect
CONTROL / second ID / mux control
```

Treat this only as a functional hypothesis until the connector pin order is proven.

---

# Highest-priority platform work

## 1. Universal uSmart development adapter

Build this before making many one-off accessories.

Concept:

```text
uSmart
  │
  ├── VBUS
  ├── GND
  ├── D+
  ├── D-
  ├── ID
  └── CTRL
       ↓
┌──────────────────┐
│ uSmart dev board │
│                  │
│ ESD protection   │
│ current monitor  │
│ test pads        │
│ ID breakout      │
│ USB connector    │
└────────┬─────────┘
         ↓
      USB device
```

Goals:

- expose USB2 safely
- expose all six contacts to test pads
- measure VBUS voltage/current
- support passive continuity work
- permit connection of ordinary USB peripherals
- preserve unknown ID/control lines for research
- include ESD/protection
- make future accessory prototyping much easier

This is probably the single most valuable physical development tool.

---

# Accessory idea backlog

| Idea | Use | Interface | Difficulty | Priority |
|---|---|---|---:|---:|
| **Meshtastic module** | LoRa mesh modem | USB serial | Medium | ★★★★★ |
| **Walkie-talkie / field radio** | Real RF voice/PTT | USB Audio + CDC | Medium–High | ★★★★★ |
| **Universal USB adapter** | Connect arbitrary USB2 devices | USB2 | Low–Medium | ★★★★★ |
| **CAN adapter** | Vehicle/machinery diagnostics | USB CAN | Medium | ★★★★★ |
| **RS-485 / Modbus** | Industrial equipment | USB serial | Low | ★★★★★ |
| **RTK GNSS** | High-accuracy positioning | USB serial | Medium | ★★★★★ |
| **SDR receiver** | RF spectrum/scanner | USB | Medium | ★★★★★ |
| **Ethernet adapter** | Wired networking | USB Ethernet | Low | ★★★★☆ |
| **OBD-II module** | Vehicle diagnostics | CAN/USB | Medium | ★★★★☆ |
| **Environmental sensor pod** | Air/weather telemetry | USB serial | Low | ★★★★☆ |
| **APRS/radio modem** | Packet radio | USB serial/audio | Medium | ★★★★☆ |
| **RFID/NFC/barcode module** | Field scanning | HID/serial | Low | ★★★★☆ |
| **External UVC camera** | Endoscope/NV/macro | UVC | Low | ★★★★☆ |
| **Hardware security module** | FIDO2/keys/signing | HID/CCID | Medium | ★★★★☆ |
| **USB storage module** | Rugged removable storage | Mass storage | Low | ★★★☆☆ |
| **Geiger counter** | Radiation logging | USB serial | Low–Medium | ★★★☆☆ |
| **General GPIO lab module** | Portable electronics interface | USB | Medium | ★★★★★ |

---

# Meshtastic

See:

`meshtastic_todo_ideas.md`

Core concept:

```text
uSmart
  ↓
USB serial + 5V
  ↓
Meshtastic MCU/LoRa
```

Potential integration:

- auto-power on attach
- USB serial instead of Bluetooth
- local TCP bridge
- LieppOS status integration
- phone GPS sharing
- emergency/off-grid messaging
- custom rugged back-mounted radio

---

# Walkie-talkie / field radio

See:

`walkie_talkie.md`

Core concept:

```text
uSmart
  ↓
USB Audio + CDC + 5V
  ↓
VHF/UHF radio module
```

Potential mapping:

- F1 = PTT
- F2 = channel/scan/emergency
- phone mic/speaker used for voice
- LieppOS owns UI/channel/telemetry
- possible combined Meshtastic + voice-radio accessory

---

# CAN + RS-485 field adapter

Very strong fit for a rugged phone.

Concept:

```text
uSmart
   ↓
USB
   ↓
MCU
 ├── isolated CAN
 ├── isolated RS-485
 ├── UART
 └── GPIO
```

Potential uses:

- vehicles
- solar inverters
- BMS systems
- industrial controllers
- HVAC
- PLCs
- machinery
- agricultural equipment
- power systems
- building automation

Possible LieppOS features:

- CAN logger
- DBC decoding
- Modbus terminal
- serial terminal
- oscilloscope-like live graphs
- GPS-tagged diagnostic sessions
- log export

---

# RTK GNSS

Concept:

```text
uSmart
   ↓
USB serial
   ↓
RTK GNSS
   ↓
external antenna
```

Potential uses:

- GIS
- field mapping
- construction
- surveying support
- trail/route mapping
- antenna/site work
- precision waypointing

Potential LieppOS integration:

- external GNSS provider
- NTRIP client
- RTK fix status
- accuracy indicator
- raw logging
- map overlay
- survey profiles

---

# SDR receiver

Concept:

```text
uSmart
  ↓
USB2
  ↓
SDR receiver
  ↓
antenna
```

Possible uses:

- spectrum analysis
- ADS-B reception
- weather radio
- amateur radio monitoring
- ISM-band debugging
- pager/data decoding where lawful
- RF troubleshooting

Main concerns:

- power consumption
- USB2 bandwidth
- RF interference from phone
- antenna placement
- thermal load

---

# Ethernet

Potential simple accessory:

```text
uSmart
 ↓
USB Ethernet controller
 ↓
RJ45
```

Potential features:

- wired diagnostics
- adb/network debugging
- field router access
- network appliance setup
- isolated/secured network work

Could also combine Ethernet with RS-485/CAN in one service module.

---

# Environmental sensor pod

Potential sensor set:

- temperature
- humidity
- barometric pressure
- VOC
- CO2
- particulate matter
- UV
- light
- gas sensors
- sound level
- optional radiation

Concept:

```text
uSmart
 ↓
USB MCU
 ├── BME-class sensors
 ├── CO2
 ├── PM
 └── other probes
```

Could combine with Meshtastic to broadcast field measurements.

---

# Geiger/radiation accessory

Concept:

```text
Geiger tube / detector
       ↓
counter electronics
       ↓
MCU
       ↓
USB
       ↓
uSmart
```

LieppOS could log:

- CPM
- dose rate
- GPS coordinates
- timestamp
- map heat layer

---

# General-purpose electronics interface

Potential module:

```text
uSmart
 ↓
RP2040 / STM32 / similar
 ├── I2C
 ├── SPI
 ├── UART
 ├── GPIO
 ├── ADC
 └── PWM
```

Potential use:

- portable hardware lab
- sensor development
- UART console
- embedded debugging
- GPIO automation
- test fixtures

This could become the foundation for many future custom accessories.

---

# Security accessory

Potential:

```text
uSmart
 ↓
USB
 ↓
secure MCU / secure element
```

Possible interfaces:

- FIDO2
- CCID
- secure signing
- SSH key storage
- LieppOS-specific unlock/authentication
- hardware-backed recovery keys

---

# Accessory identification strategy

If the two extra uSmart contacts are really ID/control lines, LieppOS could optionally use them.

Possible model:

```text
ID state
  ↓
LieppOS
  ↓
select accessory policy
```

But a cleaner custom ecosystem may simply use USB VID/PID/interface identification:

```text
USB VID/PID
    ↓
LieppOS accessory manager
    ↓
launch appropriate service
```

Potential examples:

```text
Meshtastic VID/PID → meshtastic-usmart
Radio VID/PID      → field-radio-service
CAN VID/PID        → can-service
GNSS VID/PID       → external-gnss-service
Sensor VID/PID     → sensor-hub-service
```

Do not depend on proprietary stock accessory IDs unless necessary.

---

# LieppOS uSmart accessory manager idea

Long-term idea:

```text
uSmart attach
   ↓
Accessory Manager
   ↓
USB descriptor + optional ID line
   ↓
match profile
   ↓
power/routing/service policy
```

Responsibilities:

- detect accessory
- manage VBUS
- manage USB role/routing
- identify VID/PID
- launch service
- manage permissions
- handle suspend/resume
- collect power/thermal telemetry
- expose Settings UI
- log faults
- safely shut down accessory

Potential settings page:

```text
Settings
  └── Connected devices
       └── uSmart
            ├── Accessory: Meshtastic
            ├── Power: 5V / xxx mA
            ├── USB: Connected
            ├── Service: Running
            ├── Firmware
            └── Diagnostics
```

---

# Research TODOs before accessory PCB design

## Connector

- [ ] Determine exact contact numbering.
- [ ] Prove GND.
- [ ] Prove VBUS.
- [ ] Prove USB D+.
- [ ] Prove USB D−.
- [ ] Identify accessory-detect pin.
- [ ] Identify final sixth signal.
- [ ] Determine connector contact current rating if possible.
- [ ] Determine mating connector/mechanical part source.

## Power

- [ ] Recover MT6375 OTG current limit.
- [ ] Recover VBUS nominal voltage.
- [ ] Recover OCP behavior.
- [ ] Recover inrush behavior.
- [ ] Determine continuous current capability.
- [ ] Determine screen-off/suspend behavior.
- [ ] Determine simultaneous USB-C charging behavior.
- [ ] Determine thermal throttling.
- [ ] Determine if accessory categories change power limit.

## USB

- [ ] Confirm shared USB0 / MTU3 / xHCI fabric mapping (no second controller exists).
- [ ] Recover mux GPIOs.
- [ ] Recover pinctrl states.
- [ ] Recover host-role transition.
- [ ] Recover VBUS/data enable order.
- [ ] Test generic USB enumeration later on Slot B.
- [ ] Confirm USB Audio support.
- [ ] Confirm CDC serial support.
- [ ] Confirm composite devices.
- [ ] Confirm Ethernet/CDC-NCM/RNDIS as needed.
- [ ] Confirm USB mass storage.
- [ ] Confirm UVC.

## Detect / ID

- [ ] Determine whether attach detection is GPIO-, resistance-, or USB-based.
- [ ] Recover stock accessory events.
- [ ] Identify extcon/uevent output.
- [ ] Determine whether stock accessory IDs exist.
- [ ] Decide whether LieppOS should preserve or replace stock ID logic.

---

# Hardware development sequence

Recommended:

```text
1. Finish static RE
2. Obtain genuine uSmart-to-Type-C adapter/accessory
3. Passive continuity mapping
4. Build protected breakout/dev board
5. Validate power with dummy/current-limited load
6. Validate USB with simple low-power device
7. Validate generic CDC
8. Validate USB Audio
9. Validate selected accessory prototype
10. Build dedicated mechanical PCB
```

Do not jump directly to a high-current RF transmitter.

---

# Suggested project priority

| Rank | Project | Why |
|---:|---|---|
| **1** | Universal uSmart dev adapter | Unlocks every other project |
| **2** | Meshtastic | High practical value, straightforward USB serial |
| **3** | Walkie-talkie / field radio | Excellent rugged-phone use case |
| **4** | CAN + RS-485 | Strong industrial/field value |
| **5** | RTK GNSS | Excellent field-mapping capability |
| **6** | SDR | Powerful but RF/power-sensitive |
| **7** | Sensor pod | Easy and useful |
| **8** | General GPIO lab tool | Great development platform |

---

# Long-term ecosystem idea

Instead of treating uSmart as a Ulefone-only camera connector, LieppOS can turn it into a general accessory platform.

```text
                  LieppOS
                     │
             uSmart Accessory Manager
                     │
       ┌─────────────┼──────────────┐
       │             │              │
 Meshtastic      Field Radio      RTK GNSS
       │             │              │
       ├──── CAN / RS485 ────────────┤
       │             │              │
      SDR       Sensor Hub       Dev Board
```

The key is to reverse engineer the connector **once** and then standardize our own accessory hardware/software conventions.

---

# Safety boundary

Do not:

- inject voltage into unknown uSmart pins
- short unknown contacts
- assume the six-pin order
- exceed an unproven power limit
- blindly toggle unknown ID/control GPIOs
- connect high-current RF hardware before VBUS behavior is proven

Prefer:

- static reverse engineering
- passive continuity testing
- a protected dev/breakout board
- current-limited validation
- staged Slot-B software testing
- documented USB/accessory protocols

