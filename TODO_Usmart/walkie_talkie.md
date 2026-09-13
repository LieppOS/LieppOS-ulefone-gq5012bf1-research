# uSmart Walkie-Talkie / Field Radio Ideas

Target device: **Ulefone Armor 29 Pro Thermal (GQ5012BF1 / MT6878T)**

Goal: build a real RF walkie-talkie / field-radio accessory for the Ulefone uSmart connector, powered by the phone and controlled over USB through LieppOS.

---

## Core concept

This is not an internet PTT accessory. The target is a real RF radio module with the phone acting as the UI, microphone/speaker endpoint, controller, logger, and optional navigation/mesh terminal.

```text
Armor 29 Pro Thermal
        │
        │ uSmart
        │
        ├── 5V VBUS
        ├── GND
        ├── USB D+
        ├── USB D-
        ├── ID / DETECT ?
        └── CONTROL ?
                │
                ▼
┌────────────────────────────┐
│ uSmart Field Radio Module  │
│                            │
│ MCU                        │
│ ├── USB CDC control        │
│ ├── USB Audio              │
│ ├── PTT control            │
│ └── radio configuration    │
│                            │
│ Audio codec / baseband     │
│          │                 │
│ RF transceiver + PA/LNA    │
│          │                 │
│       Antenna              │
└────────────────────────────┘
```

Current uSmart research indicates the accessory-power/data path is associated with:

```text
MT6375 OTG
    ↓
extcon-mtk-usb
    ↓
shared USB0 / MTU3 / USB2 fabric + UVC routing
    ↓
uSmart
```

SC851x has been excluded from the uSmart VBUS/control path.

---

## USB interface model

The cleanest design is a USB composite device.

| Interface | Purpose |
|---|---|
| USB Audio input | Radio RX audio → phone |
| USB Audio output | Phone microphone → radio TX |
| USB CDC serial | Channel/frequency/settings/status |
| CDC or HID control | PTT and fast controls |
| Optional telemetry interface | RSSI, temperature, SWR/fault status, supply voltage |

The phone does not need to implement radio baseband processing if the accessory handles it.

---

## Audio path

Preferred first design:

```text
Phone microphone
     ↓
USB Audio
     ↓
radio module
     ↓
RF TX

RF RX
 ↓
radio module
 ↓
USB Audio
 ↓
Phone speaker
```

Benefits:

- no separate speaker required
- no separate microphone required
- no duplicate user controls
- smaller accessory
- LieppOS controls audio routing, gain, mute, recording, Bluetooth-headset routing, etc.

Optional later variant:

- local accessory speaker
- local accessory microphone
- accessory headset connector
- simultaneous phone + accessory audio

---

## Physical PTT integration

The Armor 29 Pro Thermal already has custom F1/F2 buttons through the YFT GPIO-key path.

Potential mapping:

```text
F1 held
   ↓
LieppOS PTT service
   ↓
USB command: PTT_ON
   ↓
radio transmits

F1 released
   ↓
USB command: PTT_OFF
   ↓
radio returns to receive
```

Possible F2 mappings:

- short press: channel +
- long press: channel -
- double press: scan
- emergency shortcut
- radio/mesh mode switch
- monitor/squelch-open
- repeater/direct toggle

LieppOS should own the button policy rather than hard-code it into accessory firmware.

---

## LieppOS radio UI ideas

Potential radio screen:

```text
CH 03         446.xxx MHz
RX            ███████░░ RSSI
CTCSS         88.5 Hz
POWER         LOW
SCAN          OFF
MODE          FM

[ PTT ]
```

Potential controls:

- channel presets
- frequency where legally permitted
- RX/TX mode
- squelch
- volume
- CTCSS/DCS
- scan
- monitor
- repeater offset
- TX power
- timeout timer
- RSSI meter
- radio temperature
- PA fault status
- antenna/SWR warning if hardware supports it
- recording
- GPS-tagged recordings
- emergency channel
- channel naming
- per-channel profiles

---

## Radio-control protocol

A simple accessory command protocol could expose operations such as:

```text
GET_INFO
GET_STATUS
GET_RSSI
GET_TEMP
SET_CHANNEL
SET_FREQUENCY
SET_POWER
SET_SQUELCH
SET_CTCSS
SET_DCS
SET_MODE
SCAN_START
SCAN_STOP
PTT_ON
PTT_OFF
RX_ONLY
GET_FAULTS
```

Do not invent a complicated protocol if USB CDC + a compact binary or line protocol is enough.

The protocol should remain versioned and documented in the LieppOS research repo.

---

## Analog FM option

A straightforward analog voice-radio accessory is likely the lowest-complexity path.

Accessory responsibilities:

- RF transceiver
- modulation/demodulation
- PA/LNA
- filtering
- squelch/RSSI
- optional CTCSS/DCS
- radio channel state
- USB audio bridge
- USB control

Phone responsibilities:

- microphone
- speaker
- PTT UI/buttons
- channel UI
- logs
- settings
- recording
- GPS/context
- firmware update/control

---

## Digital voice option

Possible later path:

```text
Phone / LieppOS
      ↓
USB
      ↓
MCU / baseband
      ↓
digital voice codec / modem
      ↓
RF
```

Potential uses:

- Codec2-style digital voice
- custom data/voice mode
- packet radio
- APRS-like telemetry
- encrypted transport only where legal and appropriate
- store-and-forward data
- emergency telemetry

Digital voice should be treated as a separate design track from basic analog FM.

---

## Meshtastic + walkie-talkie combined module

A combined field-communications module would be especially interesting:

```text
                    ┌── LoRa → Meshtastic
uSmart → MCU / USB ─┤
                    └── VHF/UHF voice radio
```

Potential final architecture:

```text
        ULEFONE ARMOR 29 PRO THERMAL
                    │
                 uSmart
                    │
          ┌─────────┴──────────┐
          │ FIELD RADIO MODULE │
          │                    │
          │ LoRa / Meshtastic  │
          │ VHF/UHF voice      │
          │ GNSS optional      │
          │ USB audio          │
          │ USB serial         │
          └─────────┬──────────┘
                    │
                 antenna

F1 = PTT
F2 = mesh/radio function
```

Potential software behavior:

- voice radio active independently of mesh
- Meshtastic available at same time
- common GPS/time source
- common accessory-health telemetry
- unified LieppOS status screen
- one USB cableless uSmart connection
- optional shared antenna only if RF design safely supports it; otherwise separate antennas

---

## Accessory telemetry

Useful radio telemetry to expose to LieppOS:

- RSSI
- squelch state
- TX active
- RX active
- PA temperature
- MCU temperature
- supply voltage
- supply current if measured
- TX power
- fault flags
- PLL lock
- selected channel
- selected mode
- optional reflected-power/SWR estimate
- firmware version
- hardware revision

---

## Power questions to solve before hardware design

We still need exact uSmart power-budget evidence.

Required:

- VBUS voltage
- maximum sustained current
- peak current limit
- inrush limit
- MT6375 current-limit configuration
- whether the current limit is accessory-dependent
- suspend/screen-off behavior
- thermal/current throttling
- whether USB-C charging can remain active while uSmart sources VBUS
- whether the phone can safely power a transmitter during RF TX current peaks

Potential radio TX power may need to be limited by the uSmart power budget.

A radio accessory may require:

```text
uSmart 5V
   ↓
input protection
   ↓
soft-start / current limit
   ↓
buck / buck-boost
   ↓
RF PA + MCU
```

Do not select PA output power before the connector power budget is proven.

---

## RF hardware TODO

Need to choose:

- band / intended radio service
- legal transmit power
- modulation
- transceiver IC/module
- PA level
- LNA
- RF filtering
- antenna type
- antenna connector
- antenna placement relative to phone
- shielding
- phone desense mitigation
- thermal path
- enclosure RF transparency

The hardest part of the walkie-talkie project is expected to be **RF hardware/antenna/compliance**, not Android or uSmart control.

---

## Mechanical concept

Potential rugged back-mounted accessory:

```text
┌────────────────────────────────┐
│ Armor 29 Pro Thermal           │
│                                │
│                     antenna    │
│                        │       │
│       uSmart ●●●●●●════╪════╗  │
│                             ║  │
│                  radio pod  ║  │
│                             ╚══│
└────────────────────────────────┘
```

Goals:

- secure uSmart mechanical engagement
- no dangling USB-C cable
- replaceable antenna
- rugged enclosure
- minimal obstruction of thermal camera / rear display / cameras
- acceptable RF separation from phone antennas
- manageable heat under TX
- removable module

---

## Firmware update idea

Accessory firmware should support safe USB firmware updates through LieppOS.

Potential flow:

```text
LieppOS Settings
    ↓
Field Radio
    ↓
Firmware Update
    ↓
USB bootloader
    ↓
signed accessory firmware
```

Use recovery/failsafe firmware slots if MCU supports them.

---

## LieppOS integration ideas

- [ ] F1 physical PTT.
- [ ] F2 programmable radio action.
- [ ] Quick Settings radio tile.
- [ ] Status-bar RX/TX indicator.
- [ ] Channel/frequency indicator.
- [ ] Radio service starts automatically on uSmart attach.
- [ ] Audio route automatically switches to USB radio.
- [ ] Bluetooth headset can optionally become radio microphone/speaker.
- [ ] Record received/transmitted audio.
- [ ] GPS-tag recordings.
- [ ] Emergency/SOS workflow.
- [ ] Background scanning.
- [ ] Notification on activity.
- [ ] Configurable TX timeout.
- [ ] Power/thermal management.
- [ ] Firmware update screen.
- [ ] Diagnostics page.
- [ ] Optional Meshtastic integration in same communications UI.

---

## Feasibility

| Feature | Feasibility |
|---|---:|
| uSmart powers radio | **9/10**, pending power-limit confirmation |
| USB radio control | **10/10** |
| USB audio | **9/10** |
| F1 as physical PTT | **10/10 in LieppOS** |
| Analog walkie-talkie | **9/10** |
| RSSI/channel UI in LieppOS | **10/10** |
| Integrated Meshtastic + voice radio | **8/10** |
| Rugged snap-on field-radio module | **9/10** |

---

## Safety / regulatory notes

Before transmitting:

- determine the intended legal band/service
- comply with local transmit-power limits
- use appropriate filtering
- do not transmit outside authorized bands
- do not assume an RF module is legal merely because it can tune a frequency
- validate antenna/PA thermals
- ensure the phone/uSmart power path can handle TX peaks
- avoid RF coupling into phone sensors, GNSS, cellular, Wi-Fi, NFC, or thermal-camera electronics

Development should start with:

1. USB control
2. receive-only operation
3. low-power bench transmission into a proper RF load/test setup
4. controlled radiated tests only after RF design is validated

---

## Immediate TODO

Before choosing final radio hardware:

1. Finish exact uSmart six-pin mapping.
2. Recover uSmart current limit and VBUS behavior.
3. Recover attach/detect mechanism.
4. Confirm generic USB composite enumeration over uSmart.
5. Confirm USB Audio works over the uSmart shared USB0 / MTU3 / USB2 path.
6. Decide target radio service/band.
7. Estimate maximum safe radio TX power from uSmart power budget.
8. Select MCU/transceiver architecture.
9. Prototype USB CDC control first.
10. Prototype USB Audio.
11. Integrate F1 PTT into LieppOS.
12. Only then design the RF/mechanical PCB.

---

## Final concept

The strongest end-state is a **LieppOS-native field-radio ecosystem** where the uSmart accessory provides RF hardware and the phone provides the user experience.

```text
Phone
├── UI
├── Mic
├── Speaker
├── GPS
├── Storage
├── Logs
├── Maps
├── PTT buttons
└── LieppOS radio service
      │
      │ uSmart USB + power
      ▼
Accessory
├── MCU
├── USB Audio
├── USB control
├── RF transceiver
├── PA/LNA/filtering
├── LoRa optional
└── antenna
```

This would turn the Armor 29 Pro Thermal into a genuinely integrated rugged communications terminal rather than a phone with a cable-attached radio.
