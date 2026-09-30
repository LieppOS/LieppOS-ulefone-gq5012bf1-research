# LieppOS Native Thermal Camera App — Research and Implementation Plan

**Target device:** Ulefone Armor 29 Pro Thermal (GQ5012BF1)  
**Platform:** MediaTek MT6878 / MT6878T  
**Thermal hardware:** ThermoVue T2 integrated thermal imaging system  
**Proposed repo location:** `apps/thermal-camera-app.md`  
**Status:** research / design / reverse-engineering plan  
**Last updated:** 2026-09-08

---

## 1. Goal

Build a completely native, open LieppOS thermal-camera stack that does not depend on the stock ThermoVue Pro application for normal operation.

The final stack should provide:

- live thermal video;
- calibrated per-pixel temperature data where the hardware exposes it;
- still-image and video capture;
- min/max/center temperature measurement;
- arbitrary point, line and rectangular-region measurement;
- emissivity and environmental correction where supported by the real hardware model;
- user-selectable palettes;
- manual and automatic display range;
- NUC / FFC / shutter control if the hardware supports software control;
- radiometric image storage;
- optional AI/image enhancement that never alters the underlying temperature matrix;
- thermal + visible-camera fusion;
- a clean LieppOS system API so third-party apps can use the thermal camera without reverse-engineering vendor internals.

The long-term objective is not merely to clone ThermoVue Pro. It is to expose the thermal hardware as a first-class LieppOS subsystem.

---

## 2. Verified public hardware facts

Ulefone's official product material states that the Armor 29 Pro Thermal provides:

| Property | Official specification |
|---|---|
| Thermal system | Integrated ThermoVue T2 |
| Advertised thermal output | 640 × 512 |
| Frame rate | 25 Hz |
| Field of view | 56° × 42° |
| Pixel pitch | 12 μm |
| Thermal sensitivity | < 40 mK |
| Measurement range | -20 °C to 550 °C |
| Claimed accuracy | ±2 °C |
| Stock application | ThermoVue Pro |

Ulefone also advertises:

- a dedicated / independent infrared ISP;
- color optimization and contrast correction in that IR processing path;
- SharpenAI image enhancement;
- AI automatic dual-spectrum fusion marketed as FusionAI;
- MediaTek NPU 655 on the SoC for AI workloads.

### Important interpretation

These claims do **not** yet prove where each processing stage executes.

In particular, it is not yet proven whether SharpenAI runs:

1. inside the ThermoVue T2 system;
2. inside the dedicated IR ISP;
3. in a vendor native library on the application processor;
4. on the MediaTek NPU;
5. or across more than one stage.

Likewise, the advertised 640 × 512 output does not by itself prove the detector's native array resolution.

---

## 3. Current GQ5012BF1 kernel evidence

Current LieppOS kernel research identifies:

- `yft_tiny2c_usb.ko` as a Ulefone-specific thermal-camera power/mode-related module;
- compatible: `mediatek,yft_tiny2c_usb`;
- vendor_dlkm load position near the end of the stock module sequence;
- one intermodule dependency from `mt6375_charger`;
- zero exports;
- no public matching source currently known;
- stock-transition-blob status for the present 6.1 source-kernel programme.

### What is **not** proven yet

Do **not** assume that `yft_tiny2c_usb` transports video frames.

At present it is only safe to treat it as part of the thermal-camera power/mode/control path. The actual image transport may instead be:

- standard USB/UVC;
- vendor USB bulk/isoc endpoints;
- V4L2 through a vendor bridge;
- MediaTek camera HAL input;
- a misc/chardev interface;
- another kernel module;
- or a userspace/native-library interface to an ISP.

Finding the actual frame path is the first major reverse-engineering milestone.

---

## 4. Working architecture hypothesis

The current working model is:

```text
Thermal detector
      │
      ▼
ThermoVue T2 thermal subsystem
      │
      ▼
Dedicated infrared ISP
      │
      ├── calibration / correction ?
      ├── contrast processing       ?
      ├── image enhancement         ?
      └── SharpenAI                  ?
      │
      ▼
Thermal transport into MT6878
      │
      ├── USB/UVC ?
      ├── USB vendor protocol ?
      ├── V4L2 ?
      └── vendor interface ?
      │
      ▼
Android / native vendor stack
      │
      ├── radiometry ?
      ├── additional enhancement ?
      ├── FusionAI ?
      └── recording / UI
      │
      ▼
ThermoVue Pro
```

Every `?` above is an explicit RE question, not a fact.

---

## 5. Architectural rule: radiometry and image enhancement must stay separate

LieppOS should distinguish at least three representations:

```text
RAW / SENSOR-DERIVED DATA
        │
        ▼
CALIBRATED TEMPERATURE MATRIX
        │
        ├───────────────► measurement / alarms / analysis
        │
        ▼
DISPLAY IMAGE
        │
        ├── palette
        ├── contrast
        ├── denoise
        ├── sharpening
        ├── super-resolution
        └── AI enhancement
```

An AI-enhanced display frame must **never** be treated as higher-resolution temperature truth unless the hardware supplies corresponding radiometric measurements.

For example, if AI synthesizes a visually sharper edge between two objects, that synthetic edge must not create fabricated temperature samples.

This is a core LieppOS design principle.

---

## 6. Reverse-engineering mission

### Phase A — freeze the stock software oracle

Collect and hash all thermal-related stock components:

- ThermoVue Pro APK;
- split APKs, if any;
- native `.so` libraries used by the APK;
- vendor thermal / IR / UVC libraries;
- camera HAL libraries;
- vendor services;
- init `.rc` files;
- SELinux rules and labels;
- permissions XML;
- USB device filters;
- VINTF declarations;
- thermal calibration/configuration files;
- firmware/model/data files;
- relevant kernel modules;
- relevant DT/DTBO nodes.

Record package name, version, signatures, APK assets and JNI dependencies.

### Phase B — reverse ThermoVue Pro

Search Java/Kotlin, JNI and native code for:

```text
ThermoVue
ThermoVue Pro
T2
thermal
infrared
IRCamera
ir_camera
uvc
USB
VID
PID
bulk
isochronous
radiometry
temperature
emissivity
NUC
FFC
shutter
palette
fusion
FusionAI
SharpenAI
sharp
denoise
super_resolution
NPU
APU
NeuroPilot
NNAPI
tflite
model
weights
homography
registration
calibration
```

Recover:

- device discovery;
- USB VID/PID or other hardware identity checks;
- endpoint layout;
- device nodes;
- ioctls;
- sysfs accesses;
- JNI entry points;
- frame callbacks;
- frame formats;
- metadata formats;
- temperature conversion routines;
- calibration data locations;
- control commands;
- error handling;
- AI model loading;
- visible-camera selection for fusion.

### Phase C — identify the exact frame interface

Required final classification:

```text
STANDARD_UVC
UVC_PLUS_VENDOR_RADIOMETRY
CUSTOM_USB_PROTOCOL
V4L2_VENDOR_DEVICE
CAMERA_HAL_PRIVATE_PATH
MISC_CHARDEV_PROTOCOL
OTHER_PROVEN_INTERFACE
BLOCKED_BY_MISSING_EVIDENCE
```

Recover:

- native frame dimensions;
- delivered frame dimensions;
- frame rate;
- pixel format;
- bit depth;
- stride;
- endianness;
- packet framing;
- metadata location;
- timestamp source;
- dropped-frame behavior;
- whether a separate radiometric frame exists.

### Phase D — determine where the AI processing occurs

For SharpenAI and FusionAI, determine independently:

| Question | Required result |
|---|---|
| Runs in IR ISP? | proven yes / proven no / unknown |
| Runs in APK native library? | proven yes / proven no / unknown |
| Uses MediaTek NPU/APU? | proven yes / proven no / unknown |
| Uses NNAPI? | proven yes / proven no / unknown |
| Loads model/weights from filesystem? | exact path if proven |
| Can enhancement be disabled? | yes/no/unknown |
| Can pre-enhancement frames be obtained? | yes/no/unknown |

Do not infer the implementation from marketing terminology.

---

## 7. Radiometry reconstruction

The most important technical objective after live video is recovering the true temperature model.

Determine whether Android receives:

1. already-calibrated temperature values;
2. raw detector counts plus calibration coefficients;
3. a radiometric metadata block per frame;
4. only rendered thermal video with limited point-temperature queries;
5. multiple simultaneous streams.

### Recover all known correction variables

If present, identify:

- emissivity;
- reflected apparent temperature;
- ambient temperature;
- object distance;
- humidity;
- atmospheric correction;
- window/transmission correction;
- high/low measurement range selection;
- sensor temperature compensation;
- calibration offsets;
- per-pixel correction tables.

### Required proof

For every user-visible temperature value, trace:

```text
hardware/raw value
       ↓
conversion function
       ↓
correction inputs
       ↓
final °C value
```

The target is enough evidence to independently calculate the same temperature as stock for the same frame.

---

## 8. NUC / FFC / shutter behavior

Determine whether the T2 contains a mechanical shutter and how non-uniformity correction is triggered.

Recover:

- automatic NUC trigger conditions;
- manual NUC command;
- command bytes/ioctl/control request;
- whether video pauses;
- correction duration;
- calibration state reporting;
- any temperature/time thresholds;
- failure handling.

If the device automatically performs NUC internally and exposes no host command, document that instead of inventing a software implementation.

---

## 9. Proposed LieppOS system architecture

Do not make the final application depend directly on undocumented sysfs nodes or arbitrary vendor ioctls.

Preferred architecture:

```text
                ThermoVue T2 / IR ISP
                         │
                         ▼
                Linux hardware driver
                         │
                         ▼
             LieppOS Thermal Service
                  (AIDL / native)
                         │
         ┌───────────────┼────────────────┐
         │               │                │
         ▼               ▼                ▼
 LieppOS Thermal     automation /      third-party
      App             diagnostics         apps
```

The service should isolate hardware-specific details from applications.

### Candidate API

```text
open()
close()
startStream()
stopStream()

getCapabilities()
getFrameInfo()
getThermalFrame()
getTemperatureFrame()

getTemperature(x, y)
getCenterTemperature()
getMinTemperature()
getMaxTemperature()

triggerNUC()
getNUCState()

setEmissivity(value)
setReflectedTemperature(value)
setObjectDistance(value)
setHumidity(value)
setMeasurementRange(range)

getCalibrationInfo()
```

Only expose controls actually supported by the recovered hardware contract.

---

## 10. Native LieppOS Thermal app feature plan

### MVP

- live thermal preview;
- smooth 25 Hz rendering;
- rotation handling;
- center crosshair;
- min/max markers if temperature matrix is available;
- screenshot;
- video recording;
- a small initial palette set;
- device status and calibration status;
- manual NUC if supported.

### Professional measurement tools

- multiple movable spot meters;
- rectangle region min/max/average;
- line profile;
- histogram;
- hottest/coldest tracking;
- configurable high/low alarms;
- temperature lock/range control;
- isotherm highlighting;
- emissivity presets by material;
- environmental correction controls;
- Celsius/Fahrenheit/Kelvin display.

### Display palettes

Potential palettes:

- White Hot;
- Black Hot;
- Iron;
- Rainbow;
- Arctic;
- Lava;
- high-contrast industrial;
- user-defined LUT.

Palettes must operate on the display representation, not destructively modify stored radiometry.

---

## 11. Radiometric file format

Do not save only a colored JPEG.

A LieppOS thermal still should preserve:

- original frame;
- calibrated temperature matrix or raw radiometry;
- camera calibration metadata;
- environmental correction inputs;
- measurement range;
- timestamp;
- device information;
- optional visible-camera image;
- display palette and range as non-destructive presentation metadata.

Possible package model:

```text
capture.lthermal/
    preview.webp
    thermal.bin
    radiometry.bin
    visible.webp
    metadata.json
```

A future single-file container can be designed after the hardware data model is known.

The user should be able to reopen a capture later and change palette, range, emissivity or measurement points without losing the original thermal data.

---

## 12. AI / enhanced-video plan

### Principle

AI enhancement is optional visualization, not measurement truth.

### Desired modes

```text
THERMAL RAW/BASE
    closest available processed sensor representation

THERMAL CLEAN
    deterministic denoise / contrast correction

THERMAL ENHANCED
    optional AI sharpening / super-resolution

FUSION
    thermal + visible-camera registration
```

### AI enhancement research

First determine what stock SharpenAI actually does.

Then choose one of:

1. reproduce it if the implementation is legally and technically reusable;
2. build a clean independent equivalent;
3. use only the IR ISP's already-enhanced output;
4. expose both stock-equivalent and LieppOS enhancement paths if technically appropriate.

### LieppOS enhancement goals

Potential future processing:

- edge-aware denoise;
- temporal denoise;
- deblurring;
- contrast enhancement;
- perceptual sharpening;
- optional super-resolution;
- hot-object segmentation;
- anomaly highlighting.

All algorithms must preserve a separate original/radiometric frame.

---

## 13. FusionAI replacement / visible + thermal fusion

Recover which visible camera ThermoVue Pro uses and how alignment is calibrated.

Determine:

- camera ID;
- visible resolution;
- lens/FOV;
- thermal-to-visible transform;
- crop/scaling;
- homography or calibration matrix;
- whether alignment changes with focus/distance;
- whether stock uses AI registration or a fixed geometric transform;
- whether calibration parameters are stored per device.

LieppOS fusion modes could include:

- thermal-only;
- visible-only;
- adjustable alpha overlay;
- thermal edges over visible;
- visible edges over thermal;
- hot-region overlay;
- automatic feature-based registration.

Do not allow AI image fusion to alter the underlying measured temperatures.

---

## 14. Performance targets

The advertised thermal stream is 640 × 512 at 25 Hz:

```text
640 × 512 = 327,680 pixels/frame
327,680 × 25 = 8,192,000 pixels/second
```

This is a modest workload for the MT6878T GPU for palette mapping and normal image processing.

Preferred implementation:

- zero-copy or minimal-copy frame transport where possible;
- GPU shader palette mapping;
- GPU rendering of overlays;
- bounded CPU work per frame;
- optional NPU acceleration only where it measurably helps;
- no mandatory AI path for basic viewing;
- thermal subsystem fully runtime-suspended when the app is closed.

---

## 15. Battery / runtime-PM requirements

Because LieppOS also targets maximum battery life, the thermal stack must have explicit power-state behavior.

When thermal camera is unused:

```text
thermal sensor/bridge     OFF or deepest supported standby
IR ISP                    OFF / runtime suspended
USB/internal transport    suspended
thermal-specific GPIOs    inactive
thermal worker threads    stopped
AI/NPU workload           none
```

When the app starts:

```text
request thermal service
       ↓
power hardware
       ↓
wait required stabilization
       ↓
perform init/NUC if required
       ↓
start stream
```

When the final client closes:

```text
stop stream
       ↓
flush/close hardware
       ↓
runtime suspend
       ↓
power down
```

No periodic polling should remain active after the subsystem is closed unless proven necessary for hardware safety.

---

## 16. Security / permissions

The thermal camera should be treated as a privacy-sensitive sensor.

Recommended LieppOS policy:

- dedicated thermal-camera permission or tightly controlled system API;
- visible privacy indicator while thermal imaging is active;
- no unrestricted third-party access to hardware ioctls;
- SELinux isolates the device node/service;
- third-party apps receive access through the LieppOS thermal service;
- raw calibration/firmware data is read-only to apps;
- only the system service can perform dangerous hardware-control commands.

---

## 17. Development sequence

### Stage 0 — stock oracle

- inventory APK/native libs/vendor services/kernel/DT;
- document exact stock pipeline;
- no replacement code yet.

### Stage 1 — live frames

- identify frame interface;
- receive frames independently of ThermoVue Pro;
- prove resolution/frame rate/pixel format;
- build minimal native viewer.

### Stage 2 — radiometry

- recover temperature matrix;
- center/min/max temperature;
- compare LieppOS values against stock for identical captured conditions.

### Stage 3 — hardware controls

- NUC;
- measurement ranges;
- emissivity/environment settings;
- correct suspend/resume/power lifecycle.

### Stage 4 — clean system API

- implement LieppOS thermal service;
- remove application dependence on vendor internals.

### Stage 5 — production app

- professional measurement UI;
- radiometric storage;
- recording;
- palettes;
- region analysis.

### Stage 6 — AI/image enhancement

- characterize stock SharpenAI;
- implement optional LieppOS enhancement;
- benchmark quality, latency and power.

### Stage 7 — visible/thermal fusion

- recover/calibrate camera alignment;
- implement deterministic fusion;
- optionally add AI auto-registration.

---

## 18. Completion levels

### Level 1 — VIEWER_COMPLETE

- independent live thermal stream;
- correct resolution/frame rate;
- no ThermoVue Pro dependency.

### Level 2 — RADIOMETRY_COMPLETE

- correct per-pixel temperature data;
- center/min/max parity with stock within expected measurement tolerance;
- calibration path documented.

### Level 3 — HARDWARE_CONTROL_COMPLETE

- all required power, NUC, range and correction controls independently implemented;
- suspend/resume proven.

### Level 4 — STOCK_FEATURE_PARITY

- all important ThermoVue Pro measurement functions replicated;
- photos/video;
- palettes;
- fusion if stock supports it;
- stock app no longer required.

### Level 5 — LIEPPOS_SUPERSET

- clean system API;
- radiometric file format;
- advanced measurement tools;
- optional improved enhancement/fusion;
- documented SDK/API for third-party LieppOS software.

---

## 19. Unknowns / blockers to resolve

| Question | Current status | Priority |
|---|---|---:|
| Exact frame transport | UNKNOWN | P0 |
| Native detector resolution | UNKNOWN | P1 |
| Is 640×512 native or enhanced output? | UNKNOWN | P1 |
| Exact frame pixel format | UNKNOWN | P0 |
| Separate temperature matrix available? | UNKNOWN | P0 |
| Radiometric conversion formula | UNKNOWN | P0 |
| Calibration file/data location | UNKNOWN | P0 |
| NUC/shutter protocol | UNKNOWN | P1 |
| Exact purpose of `yft_tiny2c_usb` | PARTIAL — thermal power/mode relation known | P0 |
| Dedicated IR ISP identity/interface | UNKNOWN | P1 |
| SharpenAI execution location | UNKNOWN | P1 |
| SharpenAI model/algorithm | UNKNOWN | P2 |
| FusionAI implementation | UNKNOWN | P2 |
| Visible camera used for fusion | UNKNOWN | P1 |
| Thermal-visible calibration transform | UNKNOWN | P1 |
| NPU/APU involvement | UNKNOWN | P2 |

---

## 20. Evidence discipline

Every claim in the reconstruction should be tagged as one of:

```text
PROVEN_FROM_STOCK_BINARY
PROVEN_FROM_STOCK_RUNTIME
PROVEN_FROM_STOCK_DT
PROVEN_FROM_STOCK_APK
PROVEN_FROM_VENDOR_LIBRARY
PROVEN_FROM_OFFICIAL_PUBLIC_SPEC
STRONGLY_INFERRED
HYPOTHESIS
UNKNOWN
```

Do not convert Ulefone marketing language into implementation facts without RE evidence.

Particularly:

- "SharpenAI" is a product feature name, not proof of an NPU model;
- "FusionAI" is a product feature name, not proof of a specific neural network;
- "640×512 thermal resolution" is an advertised output specification, not yet proof of physical detector resolution.

---

## 21. Suggested research outputs

Create/update in `LieppOS/ulefone-gq5012bf1-research`:

```text
apps/thermal-camera-app.md
thermal/stock-software-inventory.md
thermal/thermovue-pro-re.md
thermal/thermal-interface-contract.md
thermal/frame-format.md
thermal/radiometry-contract.md
thermal/calibration-contract.md
thermal/nuc-ffc-contract.md
thermal/yft-tiny2c-usb-contract.md
thermal/ir-isp-contract.md
thermal/sharpenai-analysis.md
thermal/fusionai-analysis.md
thermal/visible-camera-registration.md
thermal/power-runtime-pm.md
thermal/lieppos-thermal-service-api.md
thermal/radiometric-file-format.md
```

Raw RE evidence should live under an appropriate `workspace/thermal-camera/` tree rather than being mixed into clean source/device repositories.

---

## 22. Immediate next task

The next focused task should be:

> Reverse ThermoVue Pro, its JNI/native libraries and all thermal-related vendor components to identify the exact frame transport, frame format and radiometry path.

The first milestone is not AI recreation. It is answering this precisely:

> **What exact interface and bytes carry one thermal frame and its corresponding temperature information from the ThermoVue T2 / IR ISP into Android?**

Once that is known, a basic independent LieppOS thermal viewer is likely a normal application/graphics task rather than a major kernel problem.

---

## 23. Public references

Official Ulefone sources used for currently verified product-level facts:

- https://www.ulefone.com/products/armor-29-pro-thermal-version
- https://www.ulefone.com/pages/armor-29-pro-thermal-version-spec
- https://store.ulefone.com/products/armor-29-pro-thermal

These references establish the marketed hardware/output capabilities. Implementation details must still be proven from the device software/hardware evidence.
