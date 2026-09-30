# LieppOS GQ5012BF1 — Scientific Live Battery Health Estimator

**Device:** Ulefone Armor 29 Pro Thermal (`GQ5012BF1`)  
**Battery:** nominal 10600 mAh at 7.74 V (21200 mAh cell-voltage-equivalent), about 82.0 Wh nominal  
**Goal:** Estimate battery health as continuously as physics allows, while exposing uncertainty instead of inventing false precision.

---

## 1. Core principle

Battery health is not directly observable from one instantaneous sensor reading.

Treat it as a hidden state inferred from:

- current;
- terminal voltage;
- temperature;
- SOC;
- charge throughput;
- voltage relaxation;
- natural current transients;
- charge-curve shape;
- long-term capacity observations;
- primary/secondary gauge outputs.

The estimator should update continuously, but distinguish:

```text
ESTIMATE UPDATED
```

from:

```text
NEW INFORMATION ACTUALLY IMPROVED CONFIDENCE
```

A second-by-second number can be displayed, but the confidence may remain unchanged for hours until a useful charging, resting, or load-transient event occurs.

---

## 2. Do not define "health" as only one thing

Maintain a health vector.

### Capacity health

Primary headline:

```text
SOH_capacity = Qmax_est / Q_reference × 100%
```

where `Q_reference` is the calibrated new-pack usable capacity at a defined temperature/rate window.

### Resistance / power health

Track resistance growth at normalized SOC and temperature:

```text
R_growth = R0_current_ref / R0_new_ref
```

Do not automatically convert this to the same percentage as capacity health unless a validated power-capability model exists.

### Charge-acceptance health

Track how charging current/taper behavior evolves under comparable:

- SOC;
- temperature;
- charger mode;
- voltage;
- current limit.

### Energy health

Track calibrated usable Wh over controlled/reference-like windows.

### Stress exposure

Track separately:

- high-SOC time;
- high-temperature time;
- charge C-rate;
- fast-charge/PPS exposure;
- equivalent full cycles.

Stress exposure predicts aging risk; it is **not** itself a direct measurement of current health.

---

## 3. Recommended user-facing representation

Example:

```text
Battery Health
─────────────────────────────────
Capacity retention      94.2 %
95% confidence          ±1.3 %

Resistance growth       +17.8 %
Power capability        Normal

Gauge-reported SOH      94 %
Secondary-gauge SOH     93 %

Evidence quality        HIGH
Last strong calibration 2 days ago
Samples used            38 charge/rest windows
```

Avoid displaying:

```text
94.273819 %
```

False precision is scientifically misleading.

---

## 4. Multi-rate estimator

Use four estimator layers.

### Layer A — fast / live

Update while the AP is awake using battery measurements.

Typical cadence:

```text
1 Hz normal live telemetry
```

Use short faster bursts only when a useful natural current transient occurs and when the hardware/gauge can supply meaningful samples without creating major I2C/CPU overhead.

Fast layer estimates:

- instantaneous V/I/P/T;
- equivalent-circuit states;
- short-term ohmic resistance;
- polarization;
- predicted terminal voltage;
- residual/error against model.

### Layer B — event estimator

Triggered by informative events:

- screen/GPU load step;
- charger attach/detach;
- large CPU workload step;
- display on/off;
- charging-current change;
- current interruption/rest;
- entry/exit from direct charging.

Use these natural events instead of deliberately stressing the battery with test pulses.

### Layer C — session estimator

Runs after:

- partial charge segments;
- long discharge windows;
- charging sessions;
- sufficiently long relaxation;
- broad SOC traversal.

Updates:

- capacity;
- ICA/DVA health features;
- CV-tail features;
- energy efficiency;
- model parameters.

### Layer D — slow aging estimator

Runs across days/weeks.

Updates:

- capacity trend;
- normalized resistance trend;
- equivalent full cycles;
- temperature/SOC exposure;
- remaining-useful-life trend if enough data exists.

---

## 5. Equivalent-circuit model

Start with a practical first- or second-order Thevenin equivalent-circuit model.

Example second-order state:

```text
terminal_voltage =
    OCV(SOC, T)
    - I * R0
    - Vrc1
    - Vrc2
```

with RC polarization branches.

Candidate hidden-state vector:

```text
x = [
    SOC,
    Qmax,
    R0,
    R1,
    C1,
    R2,
    C2,
    current_sensor_bias,
    voltage_sensor_bias
]
```

Not every parameter must be enabled initially.

Use a dual/augmented estimator rather than re-fitting everything every sample.

Recommended starting approaches:

- UKF or adaptive UKF for nonlinear SOC/state estimation;
- RLS or a slower companion filter for model parameters;
- eventually dual UKF / Bayesian fusion if measurements justify the complexity.

Keep the estimator outside the kernel.

---

## 6. Why estimator logic should NOT live in the kernel

Kernel responsibilities:

- expose raw calibrated measurements;
- expose stable timestamps;
- expose charger/gauge state;
- provide tracepoints for state changes;
- avoid destroying measurement fidelity with aggressive rounding.

Userspace privileged battery-estimator daemon responsibilities:

- floating-point model;
- filtering;
- persistent history;
- Bayesian uncertainty;
- health fusion;
- model migration/versioning;
- database;
- Android Binder interface.

Suggested architecture:

```text
kernel drivers
   ↓
power_supply / tracepoints / charger interfaces
   ↓
lieppos-batteryd
   ↓
Health/Battery policy service
   ↓
Battery Lab / Settings / QS
```

---

## 7. Capacity estimation

### 7.1 Coulomb counting

Over an informative SOC interval:

```text
ΔQ = integral(I dt)
```

A simple capacity observation is approximately:

```text
Qmax_obs ≈ ΔQ / ΔSOC
```

but this must not be used naïvely because:

- SOC itself may depend on the current Qmax estimate;
- temperature changes usable capacity;
- current sensor bias integrates into large error;
- top/bottom nonlinear SOC regions are difficult;
- load-dependent cutoff changes usable capacity.

Instead, feed throughput observations into the joint state estimator.

### 7.2 Prefer broad SOC windows

A 2% SOC traversal is weak evidence.

A stable 20–80%, 30–90%, or similarly broad interval is much stronger.

Give observations weights based on:

```text
SOC span
temperature stability
current sensor quality
rest-anchor availability
charging/discharging stability
model residual
```

### 7.3 Full-cycle calibration

A near-full usable cycle can provide a strong calibration, but users should never be required to deep-cycle the battery for health measurement.

Natural partial-cycle information should accumulate continuously.

---

## 8. OCV and voltage relaxation

When current falls close to zero:

```text
terminal voltage -> relaxed voltage -> OCV
```

Relaxation contains information about:

- SOC;
- polarization dynamics;
- resistance/aging.

Use natural rest events:

- screen-off idle;
- after unplugging;
- after charging pauses;
- after a major load stops.

Store:

```text
V(t=0)
V(5s)
V(10s)
V(30s)
V(60s)
...
temperature
prior current
prior SOC
```

A device-specific relaxation model can use even short rest periods as health evidence.

Do not wake the AP solely to obtain an OCV point. Capture pre-suspend and post-resume data where possible.

---

## 9. Natural-transient internal resistance

A practical online estimate:

```text
R ≈ -ΔV / ΔI
```

over a short current step.

Examples of natural excitation:

- display brightness jump;
- CPU/GPU load start/stop;
- camera start;
- charger-current change.

Requirements:

- synchronized voltage/current timestamps;
- sufficiently large ΔI;
- short enough time window that OCV does not materially change;
- temperature and SOC recorded;
- reject noisy/multi-step events.

Do not compare raw resistance measured at 5 °C and 80% SOC with resistance at 35 °C and 20% SOC.

Normalize resistance using learned functions/tables:

```text
R_ref = normalize(R_measured, SOC, T)
```

Track long-term `R_ref` growth.

---

## 10. Incremental Capacity Analysis (ICA)

During sufficiently stable constant-current or quasi-constant-current charging:

```text
IC = dQ / dV
```

Battery aging changes:

- peak position;
- peak amplitude;
- peak area;
- curve shape.

Partial charging data can still contain useful SOH features.

Pipeline:

```text
raw V/I/Q/T
   ↓
quality gate
   ↓
temperature/rate normalization
   ↓
careful smoothing
   ↓
dQ/dV
   ↓
feature extraction
   ↓
device-specific health model
```

Important for this phone:

120 W PPS/direct charging may contain changing current limits and charger-state transitions, making some regions poor ICA data.

Prefer:

- verified stable CC segments;
- lower-power/stable charging windows;
- charge sections whose rate and temperature are within a trained domain.

Never blindly compute ICA across charger transitions.

---

## 11. Differential Voltage Analysis (DVA)

Also evaluate:

```text
dV / dQ
```

DVA can complement ICA and may make some degradation features easier to track.

Store both raw and normalized curve features for later offline research.

---

## 12. Constant-voltage taper features

Near the upper charge region, a CC-CV charging algorithm produces a current taper.

Track under comparable conditions:

- CV entry SOC;
- CV entry temperature;
- current decay/time constant;
- time from CV entry to termination;
- charge accepted during CV;
- termination current.

These can provide useful health information.

Treat them as secondary health indicators because they are confounded by:

- charger policy;
- thermal throttling;
- requested charge ceiling;
- PPS behavior;
- temperature;
- starting SOC.

The one-session “Charge to 100%” feature can produce particularly useful top-of-charge data, but must not exist merely to gather battery-health data.

---

## 13. Use both GQ5012BF1 gauges

The phone exposes a primary MediaTek/MT6375 battery path and a secondary SH366003 `3rd-gauge`.

Do not merge them silently.

Store:

```text
primary:
    V1 I1 T1 SOC1 Q1 FCC1 SOH1 ...

secondary:
    V2 I2 T2 SOC2 FCC2 SOH2 ...
```

Then calculate disagreement:

```text
ΔV
ΔI
ΔT
ΔSOC
ΔFCC
ΔSOH
```

Use disagreement as a data-quality signal.

Example:

```text
primary capacity estimate = 9.95 Ah
secondary FCC             = 9.87 Ah
model estimate            = 9.92 Ah

=> strong agreement
```

If the gauges disagree substantially, confidence should decrease rather than averaging them into a deceptively stable number.

---

## 14. Sensor-bias estimation

Coulomb counting is extremely sensitive to current-sensor offset.

Example:

A constant small current error integrated for many hours creates fake charge throughput.

Therefore estimate/validate:

```text
current_sensor_bias
voltage_sensor_bias
```

using:

- known-rest intervals;
- cross-gauge comparison;
- charger/battery consistency;
- model residuals.

Never claim sub-percent capacity accuracy until sensor bias is characterized.

---

## 15. Temperature normalization

Battery capacity and resistance are temperature dependent.

Every health observation must carry temperature.

Prefer reference health at a defined temperature, for example:

```text
T_ref = 25 °C
```

Actual user-facing health can be normalized to the reference model while live performance separately reports current-temperature capability.

Do not interpret a cold-battery resistance rise as permanent aging.

---

## 16. SOC normalization

Resistance and voltage dynamics vary by SOC.

Build/reference maps:

```text
R0(SOC, T, age)
OCV(SOC, T, age)
RC_parameters(SOC, T, age)
```

Do not compare health indicators from arbitrary SOC windows without normalization.

---

## 17. 2S pack / nominal-energy handling

Ulefone specifies the phone as:

```text
10600 mAh at 7.74 V
```

which is marketed as:

```text
21200 mAh equivalent
```

at the lower cell-voltage convention.

For engineering:

- use the pack-level 7.74 V / 10.6 Ah representation;
- use Wh for energy health;
- do not use 21.2 Ah as the pack charge capacity in formulas.

Nominal energy:

```text
10.6 Ah × 7.74 V ≈ 82.0 Wh
```

Actual calibrated usable energy depends on:

- voltage limits;
- load;
- temperature;
- age;
- conversion losses.

---

## 18. Bayesian evidence fusion

Every observation should be stored as:

```text
measurement
uncertainty
conditions
timestamp
model_version
```

Example health observation:

```text
capacity_obs = 9.94 Ah
sigma = 0.12 Ah
SOC window = 24–84%
Tmean = 27.1 °C
method = coulomb+OCV anchored
```

Fuse many observations instead of replacing the health number with the latest estimate.

Conceptually:

```text
posterior_health =
    prior_health
    × likelihood(new_evidence)
```

This prevents the UI from jumping from 94% to 88% because of one strange charging session.

---

## 19. Confidence grades

Example:

### HIGH

- multiple broad-SOC capacity observations;
- good rest anchors;
- primary/secondary gauge agreement;
- recent data;
- low model residual.

### MEDIUM

- useful partial-charge/relaxation data;
- few strong capacity windows.

### LOW

- new battery/model;
- temperature extremes;
- gauge disagreement;
- only narrow SOC windows;
- recent firmware/model migration.

UI:

```text
Health 94%
Confidence HIGH
95% interval 92.8–95.3%
```

---

## 20. Separate "measured health" from "aging stress"

Never lower displayed health merely because a user charged to 100% yesterday.

Maintain independent stress counters:

```text
time_SOC_ge_80
time_SOC_ge_90
time_SOC_ge_95
time_SOC_ge_99

time_T_ge_35
time_T_ge_40
time_T_ge_45

charge_Ah_throughput
discharge_Ah_throughput
equivalent_full_cycles

PPS_minutes
high_C_rate_minutes
```

These support aging prediction and user education, but are not direct proof of current capacity loss.

---

## 21. Remaining useful life

Do not enable a confident RUL estimate immediately.

RUL requires enough observed degradation history.

Only begin displaying a trend after:

- sufficient calendar time;
- several strong capacity estimates;
- stable model version;
- enough temperature/SOC exposure data.

Display ranges:

```text
Projected time to 80% capacity:
18–30 months
confidence: LOW
```

not:

```text
Battery dies in 713 days
```

---

## 22. Machine learning policy

Do not start with a black-box neural network.

Phase 1:

```text
physics/model-based estimator
+ gauge measurements
+ uncertainty
```

Phase 2:

```text
ICA/DVA/relaxation feature models
```

Phase 3, only with enough GQ5012BF1 data:

```text
hybrid physics + data-driven residual model
```

Any ML model must be trained/validated on data representative of:

- this battery chemistry;
- this pack configuration;
- this voltage window;
- realistic temperatures;
- fast/slow charging modes.

Do not apply a model trained on unrelated EV cells and present the output as ground truth.

---

## 23. Calibration plan for a new phone / replacement battery

When a new pack is first seen:

1. record battery/gauge identifiers where available;
2. start with nominal pack parameters;
3. collect normal user data;
4. establish OCV/relaxation points;
5. collect several broad-SOC charge/discharge windows;
6. establish reference resistance map;
7. establish baseline ICA/DVA features;
8. establish baseline FCC from independent methods;
9. increase health-confidence gradually.

Initial UI:

```text
Battery health: Establishing baseline
Confidence: LOW
```

This is better than inventing 100%.

---

## 24. Sampling strategy

### Normal awake

```text
battery electrical telemetry: about 1 Hz
```

### Charging/debug

Use sufficient rate for charger transitions and curve reconstruction, subject to actual gauge/ADC capabilities.

### Natural load transient

Temporarily capture faster data if useful and low-overhead.

### Screen off

No periodic AP wake solely for health tracking.

Use:

- hardware/gauge counters;
- suspend/resume snapshots;
- event-driven collection.

---

## 25. Data-quality gates

Reject or heavily down-weight an observation when:

- battery temperature changes too quickly;
- current/voltage timestamps are unsynchronized;
- charger mode changes in the middle of a curve segment;
- SOC window is too narrow;
- current sensor saturates;
- sample interval is irregular beyond tolerance;
- a gauge resets;
- the phone reboots mid-session without recoverable continuity;
- current sign convention is ambiguous;
- pack topology/units are uncertain.

Bad data should reduce confidence, not corrupt the health history.

---

## 26. Battery Lab — proposed Health page

```text
HEALTH
────────────────────────────────────

Capacity health             94.2 %
95% interval                92.9–95.5
Confidence                  HIGH

Estimated full capacity     9.99 Ah
Estimated full energy       77.4 Wh
Nominal reference           10.60 Ah / ~82 Wh

Resistance growth           +16 %
Resistance confidence       MEDIUM

Equivalent full cycles      128.4
Gauge cycle count           126

Primary gauge SOH           94 %
Secondary gauge SOH         93 %

Time ≥90% SOC               284 h
Time ≥40 °C                  11 h
Fast/PPS charging            38 h

Last strong capacity obs    2026-09-06
Last resistance obs         18 min ago
Last relaxation obs         3 h ago
```

Values shown above are illustrative only.

---

## 27. Research/validation metrics

Before claiming the estimator is accurate, validate it against controlled reference tests.

Possible lab/reference validation:

- calibrated external coulomb/energy meter during charge/discharge;
- controlled temperature;
- known current profile;
- reference capacity cycle at safe manufacturer limits;
- compare primary gauge, secondary gauge, and LieppOS estimate.

Measure:

```text
capacity MAE
capacity bias
resistance repeatability
SOC error
confidence interval calibration
temperature sensitivity
drift over time
```

---

## 28. Safety

The health estimator is observational.

It must never:

- force deep discharge;
- force full charge;
- inject battery test pulses solely for estimation;
- bypass charge limits;
- bypass thermal protections;
- change OVP/OCP thresholds;
- wake the device repeatedly during sleep solely for measurement.

Use normal user operation as the excitation source whenever possible.

---

## 29. Implementation TODO

- [ ] Freeze primary-gauge raw units and update cadence.
- [ ] Freeze SH366003 measurement units and semantics.
- [ ] Freeze SC8571 ADC units/scaling.
- [ ] Establish pack-level signed-current convention.
- [ ] Determine usable voltage/SOC limits from stock.
- [ ] Implement timestamped V/I/T/SOC acquisition.
- [ ] Add cross-gauge disagreement detector.
- [ ] Characterize current-sensor zero-offset.
- [ ] Implement first/second-order ECM.
- [ ] Implement UKF/AUKF SOC state estimation.
- [ ] Implement slow Qmax estimator.
- [ ] Implement natural-transient R0 estimator.
- [ ] Build R0(SOC,T) normalization map.
- [ ] Collect relaxation-voltage features.
- [ ] Implement partial-charge ICA/DVA extraction.
- [ ] Add CV-taper feature extraction.
- [ ] Implement Bayesian observation fusion.
- [ ] Track estimator uncertainty/confidence.
- [ ] Store model version with every result.
- [ ] Track EFC, high-SOC, thermal, and fast-charge exposure.
- [ ] Add Battery Lab Health page.
- [ ] Validate against an external calibrated energy/coulomb meter.
- [ ] Add estimator regression tests across kernel/ROM updates.
