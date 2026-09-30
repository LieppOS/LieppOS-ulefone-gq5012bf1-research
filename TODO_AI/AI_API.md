# LieppOS AI API / Intelligence Framework Plan

Target project:

- **LieppOS**
- **Device:** Ulefone Armor 29 Pro Thermal
- **Codename:** GQ5012BF1
- **SoC:** MediaTek MT6878T / Dimensity 7400

Goal:

> Build a local-AI framework where models can reason about and operate the phone through a narrow, typed, auditable capability API — without ever giving the model unrestricted root, shell, sysfs, Binder, or device-node access.

The core rule is:

```text
AI decides what it wants to do.
LieppOS decides whether and how it is allowed to happen.
```

---

# 1. High-Level Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                     USER / UI / VOICE                      │
└─────────────────────────────┬──────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                 LieppOS AI Orchestrator                    │
│                                                            │
│  conversation state    model router      tool planner      │
│  memory/RAG            permissions       confirmations     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌────────────────────────┐       ┌────────────────────────────┐
│     MODEL RUNTIME      │       │       TOOL REGISTRY        │
│                        │       │                            │
│  tiny router model     │       │ LieppOS native tools      │
│  reasoning model       │       │ Android AppFunctions      │
│  vision/audio model    │       │ third-party app tools     │
│                        │       │ user-installed plugins    │
│ CPU/Vulkan/NPU backend │       │ future uSmart tools       │
└────────────────────────┘       └─────────────┬──────────────┘
                                               │
                                               ▼
                               ┌───────────────────────────────┐
                               │   LieppOS Capability Broker   │
                               │                               │
                               │ typed AIDL/Binder APIs        │
                               │ policy + SELinux              │
                               │ validation + audit            │
                               └───────────────┬───────────────┘
                                               │
               ┌───────────────────────────────┼────────────────────┐
               ▼                               ▼                    ▼
         Android services                HAL/services          Kernel/drivers
         Settings                        thermal cam           power
         notifications                   uSmart                battery
         apps                            camera                display
         media                           sensors               USB
```

---

# 2. Non-Negotiable Security Rule

The LLM must **never** receive unrestricted:

```text
root
su
shell
/sys writes
/proc writes
/dev/mem
raw block devices
arbitrary ioctl access
arbitrary Binder access
arbitrary device nodes
arbitrary kernel control
```

Bad architecture:

```text
LLM
 ↓
su
 ↓
echo 1 > /sys/whatever
```

Desired architecture:

```text
LLM
 ↓
typed tool request
 ↓
LieppOS AI Orchestrator
 ↓
Capability Broker
 ↓
policy / permission / validation
 ↓
AIDL / HAL / framework service
 ↓
kernel / hardware
```

The model never needs to know which sysfs node or ioctl implements a feature.

---

# 3. Stable LieppOS Tool Namespace

Define a model-independent API namespace.

Initial proposal:

```text
lieppos.battery.*
lieppos.power.*
lieppos.display.*
lieppos.thermal.*
lieppos.camera.*
lieppos.usmart.*
lieppos.sensor.*
lieppos.network.*
lieppos.audio.*
lieppos.apps.*
lieppos.notifications.*
lieppos.files.*
lieppos.system.*
```

Example tools:

| Tool | Purpose |
|---|---|
| `lieppos.battery.status` | Battery %, voltage, current, temperature, charging state |
| `lieppos.battery.estimate_runtime` | Estimate remaining runtime |
| `lieppos.power.get_profile` | Read current power policy |
| `lieppos.power.set_profile` | Balanced / Performance / Max Battery |
| `lieppos.display.get_state` | Display state and refresh mode |
| `lieppos.display.set_refresh_policy` | Auto / 60 / 90 / 120 Hz |
| `lieppos.thermal.status` | Thermal-camera subsystem status |
| `lieppos.thermal.capture` | Capture a thermal frame |
| `lieppos.thermal.hottest_point` | Return calibrated hottest point |
| `lieppos.usmart.status` | Detect attached uSmart accessory |
| `lieppos.usmart.get_capabilities` | List accessory capabilities |
| `lieppos.camera.capture` | Capture from an approved camera |
| `lieppos.network.status` | Read network state |
| `lieppos.audio.set_volume` | Change volume |
| `lieppos.apps.launch` | Launch installed application |
| `lieppos.notifications.search` | Query authorized notifications |
| `lieppos.settings.change` | Change explicitly exposed settings |

---

# 4. Typed Tool Schemas

The model should not receive giant raw system dumps.

Bad:

```text
cat /sys/*
cat /proc/*
feed 300 KB into the LLM
```

Good:

```text
lieppos.battery.status()
```

returns:

```json
{
  "level_percent": 43,
  "temperature_c": 31.7,
  "current_ma": -640,
  "charging": false,
  "charger_type": "NONE"
}
```

Benefits:

- smaller prompts
- lower inference cost
- lower RAM bandwidth
- better battery life
- lower hallucination risk
- cleaner versioned API
- easier compatibility across kernel generations

---

# 5. Binder / AIDL Layer

Native LieppOS capabilities should use **typed Binder/AIDL services**.

Example:

```aidl
interface ILieppPowerService {
    BatteryStatus getBatteryStatus();
    PowerProfile getPowerProfile();
    void setPowerProfile(in PowerProfile profile);
}
```

Example thermal service:

```aidl
interface ILieppThermalService {
    ThermalStatus getStatus();
    ParcelFileDescriptor captureFrame();
    ThermalPoint getHottestPoint();
}
```

Why Binder/AIDL:

- caller UID identity
- explicit Android permissions
- SELinux mediation
- typed IPC
- process isolation
- lifecycle management
- no TCP/socket attack surface
- integrates cleanly with Android system services

---

# 6. Process Isolation

Do **not** put the LLM runtime directly into `system_server`.

Preferred layout:

```text
system_server
     │
     │ Binder
     ▼
LieppOS AI Broker
     │
     ▼
LLM Runtime
```

Dedicated SELinux domains should be used, for example:

```text
u:r:liepp_ai:s0
u:r:liepp_ai_broker:s0
```

The inference process should have:

```text
NO root
NO arbitrary device nodes
NO raw block access
NO arbitrary sysfs write access
NO unrestricted Binder access
NO direct hardware control
```

The model runtime can:

- receive a prompt
- run inference
- return text
- emit a typed tool request

That is all.

---

# 7. Capability Broker

The security boundary is the **LieppOS Capability Broker**.

Possible implementation package/service:

```text
com.lieppos.ai.broker
```

Every action must answer:

```text
WHO requested it?
WHAT capability?
WHAT parameters?
IS the capability enabled?
IS the request valid?
DOES it require confirmation?
IS the caller allowed?
```

Example:

```text
AI:
lieppos.power.set_profile(MAX_BATTERY)

Broker:
✓ capability exists
✓ reversible
✓ valid enum
✓ user policy allows automatic execution
✓ caller authorized

execute
```

Forbidden action:

```text
AI:
factory_reset()

Broker:
✗ no AI capability exists
```

The safest high-risk operation is one that the AI API simply does not expose.

---

# 8. Capability Risk Levels

Suggested levels:

| Level | Category | Example | Default behavior |
|---:|---|---|---|
| **0** | Read-only | battery status, temperature | Automatic |
| **1** | Harmless reversible | flashlight, volume | Usually automatic |
| **2** | System configuration | refresh rate, power profile | Policy-controlled |
| **3** | Sensitive | microphone, camera, notifications | Permission/context dependent |
| **4** | High-impact | delete file, send message, disable network | Explicit confirmation |
| **5** | Forbidden | flash partitions, wipe userdata, raw kernel writes | No tool exists |

Possible UI:

```text
Settings
 → LieppOS AI
 → Permissions
```

Example:

```text
Battery data             [Allow]
Thermal camera            [Allow]
Change power profile      [Allow]
Read notifications        [Ask]
Send messages             [Ask]
Microphone                [While using]
Files                     [Selected folders]
Developer controls        [Deny]
```

---

# 9. Confirmation UI

Confirmations must be rendered by trusted system UI, not by the LLM.

Example user request:

```text
"Send John the thermal image and tell him the bearing is overheating."
```

Tool plan:

```text
contacts.resolve("John")
thermal.capture()
messages.send(...)
```

Trusted confirmation UI:

```text
AI wants to:

Send message to John
Attachment: thermal_2026-09-08.png

"The bearing appears to be overheating."

[Cancel] [Send]
```

The model cannot fake approval because the broker/system UI owns the decision.

---

# 10. Model-Independent Tool Representation

Internally tools should use one canonical schema.

Example:

```text
Tool {
    id: "lieppos.power.set_profile"

    description:
      "Change the system power profile"

    parameters:
      profile: enum [
        BALANCED,
        PERFORMANCE,
        MAX_BATTERY
      ]

    risk: REVERSIBLE_SYSTEM_CHANGE

    confirmation: POLICY_DEFINED
}
```

Adapters convert this schema into the tool-call format expected by each model:

```text
Qwen
Ling
LFM
Gemma
future model
```

The OS API stays stable even when the model changes.

---

# 11. Model Router

A tiny model should sit at the front of the stack.

Example:

```text
User:
"what's my battery?"
       │
       ▼
tiny router model
       │
       ├── no large model needed
       ▼
lieppos.battery.status()
       │
       ▼
answer
```

Heavy request:

```text
"Look at this thermal image,
compare it with yesterday's measurements,
and tell me what component might be failing."
```

Router identifies:

```text
vision required
retrieval required
reasoning required
```

and loads the appropriate larger model.

Proposed stack:

```text
tiny router
   │
   ├── simple reply
   ├── direct tool use
   ├── fast reasoning model
   ├── quality model
   └── vision/audio model
```

Goal:

> Do not wake a 4–8B model for trivial tasks.

---

# 12. Android AppFunctions Adapter

Android 17 AppFunctions should be treated as an **external tool-provider adapter**, not as the core LieppOS API.

Concept:

```text
Tool Registry
│
├── LieppOS native tools
│    ├── battery.*
│    ├── thermal.*
│    ├── power.*
│    └── usmart.*
│
├── Android AppFunctions
│    ├── Notes.createNote
│    ├── Music.play
│    └── Todo.createTask
│
└── optional external integrations
```

Important rule:

```text
LieppOS native AIDL API = stable core
Android AppFunctions   = compatibility adapter
```

Do not make LieppOS hardware control depend on AppFunctions.

---

# 13. Event-Driven AI

The AI must not poll hardware continuously.

Expose structured events:

```text
BatteryLow
ChargerConnected
ChargerDisconnected
ThermalAccessoryAttached
uSmartAccessoryAttached
uSmartAccessoryRemoved
HighTemperature
IncomingNotification
WiFiConnected
AlarmTriggered
```

Desired behavior:

```text
hardware / framework
       ↓
event
       ↓
Capability Broker
       ↓
policy says AI cares?
       ↓
wake tiny model
```

Avoid:

```text
LLM wakes every 5 seconds:
"anything new?"
```

This is important for LieppOS battery goals.

---

# 14. Memory / RAG Architecture

Long-term memory should remain outside the model.

```text
                   ┌── contacts DB
                   ├── conversation memory
                   ├── user documents
LLM ← retrieval ←──┼── device knowledge
                   ├── LieppOS manuals
                   └── selected personal context
```

Preferred approach:

```text
short active context
        +
local retrieval
        +
persistent structured memory
```

instead of keeping huge 32K–128K histories active continuously.

Target active context for normal local assistant use:

```text
4K–8K
```

---

# 15. Thermal Camera Integration

Do not expect the vision model to derive calibrated temperature values from a color palette.

Preferred flow:

```text
Thermal kernel/HAL
       ↓
LieppThermalService
       │
       ├── capture()
       ├── hottestPoint()
       ├── minTemperature()
       ├── maxTemperature()
       ├── averageTemperature()
       ├── regions()
       └── renderedImage()
                ↓
          multimodal model
```

The model receives:

```text
image
+
actual calibrated temperature values
```

Possible tools:

```text
lieppos.thermal.capture
lieppos.thermal.hottest_point
lieppos.thermal.region_stats
lieppos.thermal.compare_frames
```

---

# 16. uSmart Integration

Once the six-pin/protocol work is complete:

```text
uSmart hardware
      ↓
USB / kernel / accessory layer
      ↓
LieppUsmartService
      ↓
AI Tool Registry
```

Possible initial APIs:

```text
lieppos.usmart.status
lieppos.usmart.get_connected_accessory
lieppos.usmart.get_capabilities
lieppos.usmart.camera.capture
lieppos.usmart.sensor.read
```

Do not expose raw USB or GPIO control to the model.

---

# 17. Self-Describing LieppOS Accessories

Long-term goal:

A custom uSmart accessory should be able to announce its capabilities.

Example:

```text
Vendor: LieppOS
Device: Environment Probe
Protocol: 1

Capabilities:
  read_temperature()
  read_humidity()
  read_co2()
  read_voc()
```

Registration flow:

```text
accessory attached
       ↓
LieppOS accessory daemon
       ↓
parse accessory descriptor
       ↓
register capabilities
       ↓
AI Tool Registry
       ↓
new tools become available
```

This produces:

> plug hardware into the phone → new tools appear to the local AI.

Security requirements:

- accessory identity
- capability allowlist
- protocol versioning
- per-accessory permission
- no arbitrary executable code from accessory
- no automatic privileged capability escalation

---

# 18. AI Action Audit Log

Every tool invocation should be auditable.

Record:

```text
timestamp
model
tool ID
arguments
caller
policy decision
confirmation state
result
error
```

Example:

```text
19:42:01 battery.status       READ
19:42:04 thermal.capture      READ_SENSOR
19:42:10 power.set_profile    MAX_BATTERY
19:43:26 apps.launch          org.example.maps
```

Settings UI:

```text
Settings
 → LieppOS AI
 → Activity
```

Avoid storing full private prompts by default if not required.

The important question is:

```text
What did the AI actually do?
```

---

# 19. Power / Battery Integration

AI runtime should integrate with the LieppOS power profile.

Desired lifecycle:

```text
AI idle
   ↓
large models unloaded or inactive
GPU/NPU runtime suspended
normal CPU battery policy

tiny request
   ↓
tiny model wakes
minimal CPU/memory vote

heavy request
   ↓
larger model loaded
CPU/GPU/NPU enabled as needed
memory/interconnect vote raised only as required

generation complete
   ↓
DVFS decays immediately
accelerator runtime suspend
deep idle restored
```

Measure:

- wake cost
- model-load cost
- idle model RAM
- accelerator residency
- tokens/joule
- post-inference return-to-idle latency

---

# 20. API Versioning

Every public LieppOS AI API should be versioned.

Example:

```text
lieppos.ai.api.version = 1
```

Tool contract should support:

```text
tool ID
schema version
minimum OS version
capability flags
deprecation state
```

Example:

```text
lieppos.thermal.capture@1
lieppos.power.set_profile@1
```

Do not break existing models/tools during kernel or Android upgrades.

---

# 21. Kernel Independence

The AI-facing API must remain stable across:

```text
Linux 6.1
Linux 6.18
Android-mainline 7.x
```

Example:

```text
lieppos.power.set_profile(MAX_BATTERY)
```

must stay unchanged even if the implementation behind it moves from:

```text
kernel driver A
```

to:

```text
new power HAL
```

or:

```text
different kernel API
```

This is a major reason to keep model-facing APIs above the kernel boundary.

---

# 22. Initial Phase-1 API

Start small.

Implement only a core set first:

```text
lieppos.battery.status
lieppos.power.get_profile
lieppos.power.set_profile
lieppos.display.get_state
lieppos.display.set_refresh_policy
lieppos.flashlight.set
lieppos.thermal.status
lieppos.thermal.capture
lieppos.usmart.status
lieppos.apps.launch
```

Components:

```text
LieppAiService
│
├── model runtime
├── model router
├── tool registry
├── capability broker
├── policy engine
├── confirmation service
├── audit logger
└── AIDL adapters
```

Phase 1 success criteria:

- model cannot access root directly
- all tool invocations go through broker
- all tools are typed
- invalid parameters rejected
- permissions enforced
- confirmation flow works
- action log works
- system remains functional without AI service
- AI service crash cannot crash `system_server`
- idle power returns to baseline after inference

---

# 23. Phase 2

Add:

```text
notifications
contacts
calendar
messages
audio
camera
files
sensors
```

Requirements:

- per-domain permissions
- explicit privacy boundaries
- selected-folder access for files
- confirmation for communication actions
- no unrestricted database scraping

---

# 24. Phase 3

Add Android AppFunctions discovery.

Goals:

- dynamically discover approved app tools
- convert AppFunctions metadata into internal tool schema
- apply LieppOS policy on top
- preserve per-app permissions
- allow user to disable individual app tool providers

---

# 25. Phase 4

Add dynamic uSmart accessory capabilities.

Goals:

- accessory identification
- capability descriptors
- dynamic tool registration
- protocol versioning
- accessory permission UI
- hardware disconnect cleanup
- no stale tools after device removal

---

# 26. Phase 5

Add:

```text
voice
vision
proactive/event-driven AI
local RAG
personal memory
multi-model routing
NPU acceleration
```

At this stage the local assistant becomes a real LieppOS intelligence layer rather than a chatbot.

---

# 27. Proposed Source Tree

Possible initial layout:

```text
packages/modules/LieppAI/
├── aidl/
│   ├── ILieppAiService.aidl
│   ├── ILieppCapabilityBroker.aidl
│   ├── ILieppPowerService.aidl
│   ├── ILieppThermalService.aidl
│   └── ILieppUsmartService.aidl
├── broker/
├── orchestrator/
├── router/
├── tools/
│   ├── battery/
│   ├── power/
│   ├── display/
│   ├── thermal/
│   ├── usmart/
│   └── apps/
├── policy/
├── confirmations/
├── audit/
├── appfunctions/
├── runtime/
└── tests/
```

Android app/UI:

```text
packages/apps/LieppAI/
```

SELinux policy:

```text
system/sepolicy/private/liepp_ai.te
system/sepolicy/private/liepp_ai_broker.te
```

Exact placement may change once LieppOS Android tree architecture is finalized.

---

# 28. Testing Requirements

Mandatory tests:

## API

- valid request succeeds
- invalid enum rejected
- integer bounds enforced
- missing argument rejected
- unknown tool rejected
- version mismatch handled

## Security

- model process cannot become root
- no unrestricted shell
- no direct sysfs write
- no raw block access
- no arbitrary Binder calls
- SELinux denials confirmed for forbidden paths

## Policy

- read-only tool runs automatically
- sensitive tool asks when required
- forbidden tool absent
- revoked capability fails immediately

## Crash isolation

- kill model runtime
- kill broker
- restart service
- corrupt tool output
- timeout tool execution

The phone must remain stable.

## Power

- verify runtime returns to deep idle
- verify GPU/NPU suspend
- verify model process does not generate periodic wakeups
- measure baseline idle before/after enabling AI framework

---

# 29. Threat Model

Explicitly defend against:

- prompt injection
- malicious webpage/document instructions
- model hallucinated tool names
- malformed tool arguments
- compromised third-party app function
- malicious uSmart accessory
- repeated high-impact action requests
- confirmation spoofing
- unauthorized private-data retrieval
- model trying to escalate privileges
- DoS via expensive model/tool loop

Important principle:

```text
LLM output is untrusted input.
```

Every tool request must be treated like data from an untrusted process.

---

# 30. Final Target

The end-state should be:

```text
                 LieppOS Intelligence Layer

                        Local Models
                             │
                        Orchestrator
                             │
                      Capability Broker
                             │
       ┌──────────┬──────────┼──────────┬───────────┐
       │          │          │          │           │
     Android    hardware    apps      uSmart      sensors
       │          │          │          │           │
       └──────────┴──────────┴──────────┴───────────┘
```

The LLM is the reasoning interface.

Deterministic LieppOS code retains all authority.

That separation is mandatory for security, stability, portability, and long-term maintainability.
