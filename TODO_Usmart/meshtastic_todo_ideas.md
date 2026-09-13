# Meshtastic over uSmart — TODOs and Ideas

Target device: **Ulefone Armor 29 Pro Thermal (GQ5012BF1 / MT6878T)**

Goal: build a custom Meshtastic accessory that mounts to the phone, is powered by the phone through the **uSmart Expansion Connector**, and communicates with Android/LieppOS through that same connector using USB data.

---

## Core idea

This is a much better fit for uSmart than attempting to charge the phone through the connector.

Desired architecture:

```text
Armor 29 Pro Thermal
       │
       │ uSmart
       │
       ├── VBUS ────────────────> Meshtastic 5V/VBUS
       ├── GND  ────────────────> Meshtastic GND
       ├── USB D+ ──────────────> Meshtastic USB D+
       ├── USB D- ──────────────> Meshtastic USB D-
       ├── ID / DETECT ──┐
       └── CONTROL ? ────┘
                         │
                    accessory detection
```

Current phone research points to uSmart power coming from:

```text
PHONE BATTERY
    ↓
 MT6375
    ↓
 5V OTG
    ↓
 uSmart
    ↓
 Meshtastic
```

The important correction from the SC851x reverse engineering is that **SC851x is not the uSmart VBUS controller**. The uSmart power/data path resolves to **MT6375 `usb-otg-vbus` → extcon-mtk-usb → shared USB0 / MTU3 / USB2 fabric with UVC/accessory GPIO routing**. There is no live second USB controller.

---

## Feasibility

| Requirement | Feasibility | What we need |
|---|---:|---|
| Power Meshtastic from phone | **9/10** | Exact uSmart VBUS/GND pins + current capability |
| USB data between phone and Meshtastic | **9/10** | Exact D+/D− pins |
| Auto-detect accessory when attached | **8/10** | Recover uSmart ID/detect mechanism |
| Use normal Meshtastic serial protocol | **10/10** | USB CDC/serial-capable Meshtastic board |
| Integrate directly into LieppOS | **10/10** | Small USB service/app |
| No Bluetooth required | **Yes** | USB becomes the transport |
| Work while USB-C is used for charging | **Likely** | One of the major reasons to use uSmart |

Meshtastic already supports serial-based communication, so the phone-to-radio protocol does not need to be invented from scratch.

---

## Preferred accessory architecture

Best case: use a Meshtastic board/MCU with native USB device support.

```text
uSmart D+/D-
     ↓
MCU native USB
     ↓
Meshtastic serial protocol
```

If the selected board does not expose native USB serial:

```text
uSmart USB
    ↓
USB ↔ UART bridge
    ↓
Meshtastic UART
```

Native USB is preferred because it reduces hardware, cabling, power consumption, and software complexity.

---

## LieppOS integration concept

Because we control LieppOS, we do **not** need to fool Ulefone's stock uSmart Camera APK into recognizing the Meshtastic device.

A clean integration could look like:

```text
                    ┌── Meshtastic app
                    │
uSmart              │
Meshtastic ─USB─> LieppOS meshtastic-usmart service
                    │
                    ├── serial API
                    ├── local TCP API
                    └── notifications / emergency integration
```

Possible attach flow:

```text
1. uSmart accessory detected
2. LieppOS enables MT6375 OTG VBUS
3. Meshtastic powers up
4. the shared USB0 / xHCI host path enumerates the device
5. LieppOS recognizes its VID/PID/interface
6. Meshtastic serial connection opens automatically
7. Mesh is available to Android
```

Possible detach flow:

```text
1. uSmart disconnect detected
2. LieppOS closes Meshtastic serial connection
3. service state is cleared
4. MT6375 uSmart OTG VBUS is disabled if no longer required
```

---

## Optional local TCP bridge

LieppOS could bridge uSmart USB serial to localhost:

```text
uSmart USB serial
        ↓
  LieppOS daemon
        ↓
 localhost TCP
        ↓
Meshtastic clients
```

That would make the uSmart radio behave more like a permanently integrated Meshtastic modem.

Applications would not necessarily need to know anything about the special uSmart hardware.

Potential benefits:

- one daemon owns the physical USB device
- several apps/services can consume the mesh connection
- easier reconnect handling
- centralized power management
- centralized notifications
- easier debugging/logging
- future API compatibility layer

---

## Physical accessory concept

Potential final product:

```text
┌─────────────────────────────┐
│ Armor 29 Pro Thermal        │
│                             │
│                      LoRa   │
│                        │    │
│       uSmart ●●●●●●════╪════│ custom Meshtastic module
│                        │    │
└─────────────────────────────┘
```

Goals:

- no USB-C cable
- no Bluetooth dependency
- possibly no separate accessory battery
- power provided directly by phone
- USB data over uSmart
- tight mechanical integration with the phone
- potentially weather-resistant / rugged mounting
- removable accessory

---

# Current expected six-pin functional model

We do **not** yet know the physical pin order.

Current likely functional set:

```text
VBUS / +5 V
GND
USB D+
USB D-
ID / accessory detect
CONTROL / second ID / mux enable
```

This is a working hypothesis, not a confirmed physical pinout.

Do **not** assign connector contact numbers until evidence proves them.

---

# What must be solved first

## 1. Exact six-pin mapping

Need to establish:

```text
uSmart contact 1 = ?
uSmart contact 2 = ?
uSmart contact 3 = ?
uSmart contact 4 = ?
uSmart contact 5 = ?
uSmart contact 6 = ?
```

Priority signals:

- VBUS
- GND
- USB D+
- USB D-
- accessory detect / ID
- second control / ID / routing signal

### Static RE targets

Recover from:

- DT / DTBO
- extcon-mtk-usb
- shared USB0 / MTU3 / USB2 routing
- UVC-related GPIOs
- MT6375 OTG regulator
- vendor init scripts
- vendor HALs/libraries
- ueventd rules
- SELinux policy
- stock uSmart apps
- existing dmesg/sysfs snapshots

### Hardware oracle idea

A genuine **uSmart-to-Type-C cable** may be extremely useful.

If it directly adapts the uSmart connector to USB Type-C, passive continuity testing could reveal:

- GND
- VBUS
- D+
- D−
- possibly ID/control behavior

This should be done without injecting unknown power into the phone.

---

## 2. uSmart power budget

Before powering a LoRa board continuously, determine:

- uSmart VBUS voltage
- maximum current
- current-limit source
- MT6375 regulator configuration
- overcurrent protection
- whether current limit changes by accessory type
- whether the port is enabled continuously or only after accessory detect
- suspend/screen-off behavior
- thermal/current throttling behavior
- simultaneous USB-C charging behavior

Need to compare against the selected Meshtastic board's:

- idle current
- receive current
- transmit current
- peak transmit current
- startup/inrush current
- optional GPS current
- display current
- sensor current

---

## 3. Accessory detect / ID mechanism

Recover exactly how the phone knows a uSmart accessory is attached.

Questions:

- dedicated GPIO?
- resistor ID?
- USB attach only?
- mux-detect GPIO?
- multiple accessory IDs?
- accessory-present interrupt?
- userspace property/event?
- extcon event?
- UVC-specific routing state?

Need to identify whether a custom Meshtastic accessory must emulate a stock accessory ID or whether generic USB enumeration is enough under LieppOS.

---

## 4. Shared USB0 / MTU3 / USB2 routing

Recover exact path:

```text
MT6375 OTG
    ↓
extcon-mtk-usb
    ↓
shared USB0 / MTU3 / USB2 fabric + mux / GPIO routing
    ↓
uSmart
```

Need:

- controller instance
- mux GPIOs
- pinctrl states
- host-mode trigger
- VBUS enable ordering
- data switch ordering
- disconnect sequence

---

# Meshtastic board selection TODO

Prefer a board with:

- native USB device
- stable USB CDC/serial
- low idle current
- manageable TX peaks
- no mandatory battery
- 5 V/VBUS input or suitable onboard regulator
- compact PCB
- external antenna connector if possible
- LoRa frequency suitable for intended region
- good Meshtastic support

Potential MCU families to evaluate:

- ESP32-S3
- nRF52-based boards
- RP2040/RP2350-based designs if supported for chosen use
- other supported Meshtastic boards with native USB

Do not select final board until uSmart power budget is known.

---

# Software TODOs

## LieppOS kernel/device side

- [ ] Recover exact uSmart VBUS enable path.
- [ ] Recover accessory detect signal.
- [ ] Recover shared-USB-fabric routing GPIOs/pinctrl.
- [ ] Recover uSmart attach/detach events.
- [ ] Determine whether stock kernel exposes an extcon/uevent that can be reused.
- [ ] Determine if a generic USB device can enumerate without stock uSmart app involvement.
- [ ] Determine suspend/resume behavior of uSmart host power.
- [ ] Determine whether USB-C charging can remain active while uSmart host mode is enabled.

## LieppOS userspace

Potential `meshtastic-usmart` service:

- [ ] Listen for uSmart attach/detach.
- [ ] Enable accessory VBUS if userspace control is required.
- [ ] Identify Meshtastic USB device.
- [ ] Open USB serial.
- [ ] Automatically reconnect.
- [ ] Expose local API/socket.
- [ ] Optionally expose localhost TCP bridge.
- [ ] Integrate notifications.
- [ ] Expose radio status.
- [ ] Expose mesh node count.
- [ ] Expose last packet / message status.
- [ ] Shut down or suspend radio when desired.
- [ ] Handle Android sleep/doze correctly.

---

# Possible advanced LieppOS integration

Ideas after basic USB transport works:

- native status-bar Meshtastic indicator
- quick settings tile
- mesh radio enable/disable tile
- mesh connectivity icon
- emergency/SOS integration
- notification bridge
- offline location sharing
- map integration
- background telemetry
- battery/power status for accessory
- auto-start mesh service when accessory attached
- configurable power-off after inactivity
- GPS sharing from phone to Meshtastic
- time synchronization from phone
- BLE disabled automatically when wired uSmart connection exists
- firmware update over uSmart USB
- diagnostics page in LieppOS Settings

---

# Accessory firmware ideas

Custom accessory firmware could expose:

- standard Meshtastic USB serial
- USB CDC ACM
- optional custom control interface
- firmware version
- radio temperature
- TX power
- supply voltage
- current/health telemetry if hardware supports it
- optional accessory identity descriptor

LieppOS could use a custom USB VID/PID for the dedicated accessory, while still exposing the standard Meshtastic serial protocol.

---

# Hardware design ideas

Potential custom board:

```text
uSmart connector
   │
   ├── VBUS
   │     ↓
   │  protection / optional load switch
   │     ↓
   │  MCU + LoRa
   │
   ├── D+
   ├── D-
   ├── GND
   ├── ID
   └── CTRL
```

Possible protections/components:

- ESD protection on D+/D−
- TVS on VBUS if appropriate
- input bulk capacitance sized for uSmart power limit
- soft-start/inrush management if required
- USB series resistors if required by MCU reference design
- optional current measurement
- optional ID resistor/network once uSmart detect scheme is known

Do not design or populate an ID network until the stock mechanism is proven.

---

# Main research conclusion so far

This project looks highly feasible.

Current assessment:

| Goal | Feasibility |
|---|---:|
| Phone powers Meshtastic over uSmart | **9/10** |
| USB data over same uSmart connector | **9/10** |
| Automatic attach and enumeration | **8/10** |
| Fully integrated LieppOS Meshtastic modem | **10/10** |
| No Bluetooth dependency | **10/10** |
| Custom rugged back-mounted accessory | **9/10** |

The remaining uncertainty is mostly the **physical connector contract**, not the software architecture.

Once we know:

1. exact six-pin mapping,
2. uSmart VBUS current limit,
3. accessory detect mechanism,
4. shared USB0 / MTU3 routing state machine,

we can design the accessory electrically instead of guessing.

---

# Safety / evidence boundary

Do not:

- inject 5 V into unknown uSmart contacts
- short pins experimentally
- assume physical pin order from the functional model
- enable unknown GPIOs blindly
- force OTG modes without a dedicated test plan
- connect an accessory until VBUS/GND polarity is known
- exceed uSmart power/current capability

Prefer:

- static DT/kernel/userspace reverse engineering
- passive continuity testing on a genuine uSmart-to-Type-C adapter
- USB descriptor/protocol capture
- known-good current-limited bench setups only after pinout is proven
- staged Slot-B testing once the software stack is ready

---

# Immediate next uSmart-specific research task

Perform dedicated reconstruction of:

- exact six physical connector functions
- MT6375 uSmart OTG regulator/current configuration
- shared USB0 / MTU3 routing GPIOs and pinctrl
- accessory detect/ID state machine
- stock uSmart attach/detach events
- genuine accessory USB descriptors if available
- behavior while USB-C is simultaneously charging

Target result:

```text
uSmart pin 1 = ...
uSmart pin 2 = ...
uSmart pin 3 = ...
uSmart pin 4 = ...
uSmart pin 5 = ...
uSmart pin 6 = ...

VBUS voltage = ...
VBUS current limit = ...
detect mechanism = ...
USB controller = ...
USB role = ...
mux state = ...
simultaneous Type-C charging = ...
```

Only after this should the first custom Meshtastic adapter schematic be finalized.
