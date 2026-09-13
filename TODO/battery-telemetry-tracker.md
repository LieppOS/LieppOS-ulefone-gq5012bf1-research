# LieppOS GQ5012BF1 — Battery Telemetry & Health Tracker

**Goal:** Build a very deep, low-overhead battery and power telemetry system for
LieppOS that can explain **where the energy went**, how the battery is aging,
how charging behaves, and what prevented the phone from sleeping.

Surfaces:

1. developer-grade Power Observatory;
2. optional user-facing **Battery Lab**.

---

## 1. Questions the tracker should answer

At any moment:

- battery voltage/current/power;
- charging or discharging state;
- battery temperature;
- SOC;
- estimated full-charge capacity;
- estimated SOH;
- energy used since unplug;
- energy added during current charge;
- USB-C input power;
- estimated charging efficiency;
- deep-sleep state;
- last wake source;
- active hardware subsystem;
- top UID CPU/network/wakelock contributors;
- runtime-PM blockers;
- high-temperature exposure;
- high-SOC exposure;
- equivalent full cycles;
- capacity degradation trend;
- estimated time-to-empty / time-to-full.

---

## 2. Phone-specific data sources

### Primary battery path

Use the primary MediaTek/MT6375 gauge as the authoritative Android battery source where possible.

Probe/document the final source-built `power_supply` surface rather than assuming properties exist.

Potential data:

- voltage;
- current;
- SOC;
- temperature;
- charge counter;
- full-charge capacity;
- design capacity;
- cycle count;
- status;
- health.

### Secondary SH366003 gauge

Store secondary-gauge values independently.

Potential fields already observed in stock research:

- RSOC;
- voltage;
- current;
- temperature;
- SOH;
- cycle count;
- FCC.

Use it for:

- cross-checking;
- long-term trends;
- diagnostics.

Do not silently average primary and secondary gauges.

### SC8571 direct-charge pair

After reconstruction, capture every stock-proven ADC quantity available from master/slave.

Potential examples, only where proven:

- VBUS;
- IBUS;
- VBAT;
- IBAT;
- die temperature.

### USB-C / PD / PPS

Record where exposed:

- attach state;
- source/sink role;
- PD state;
- PPS state;
- requested voltage/current;
- accepted voltage/current;
- adapter capabilities;
- active charging mode.

---

## 3. Live dashboard

| Metric | Unit / representation |
|---|---|
| SOC | % |
| Battery voltage | V |
| Battery current | A |
| Battery power | W |
| Battery temperature | °C |
| Battery state | charge/discharge/full |
| Estimated FCC | mAh + Wh |
| Estimated SOH | % |
| Charge counter | mAh |
| Charge/discharge rate | C |
| Time to empty | h:m |
| Time to full | h:m |
| USB input voltage | V |
| USB input current | A |
| USB input power | W |
| Battery charging power | W |
| Estimated conversion/system overhead | W |
| Charging mode | normal/direct/PPS/etc |
| Display refresh | Hz |
| Display brightness | normalized + nits if calibrated |
| CPU activity | cluster freq + idle residency |
| GPU activity | freq/utilization |
| Deep sleep | active/suspended |
| Current top wake source | name + hold time |
| Rear display | on/off |
| Thermal camera | active/off |
| uSmart VBUS | on/off |
| Camera rails | on/off summary |

Use one signed-current convention throughout the stack and document it.

---

## 4. Core calculations

### Instantaneous battery power

```text
P_batt = V_batt × I_batt
```

### Energy integration

```text
E_Wh += P_W × delta_seconds / 3600
```

Keep separate charge and discharge energy ledgers.

### Charge throughput

```text
Q_Ah += I_A × delta_seconds / 3600
```

Keep separate charge/discharge throughput.

### C-rate

```text
C_rate = abs(I_batt) / FCC_Ah
```

### Screen-off drain

Always report:

```text
%/h
mAh/h
Wh/h
```

`Wh/h` stays meaningful as the battery ages.

---

## 5. Charging-session analytics

Create a charging session on physical attach.

Store:

- attach timestamp;
- detach timestamp;
- starting/ending SOC;
- starting/ending charge counter;
- charger/adapter identity where available;
- USB input voltage/current/power history;
- PPS usage;
- SC8571 master/slave activity;
- battery voltage/current/power;
- battery temperature;
- peak and average temperature;
- requested charge ceiling;
- effective charge ceiling;
- total estimated input energy;
- battery energy gained;
- estimated conversion/system overhead;
- time to 50/80/90/95/100%;
- time spent above 80/90/95/99%;
- thermal-throttling events;
- charger faults;
- termination reason.

Derived estimate:

```text
battery_charge_efficiency =
    battery_energy_gained / estimated_input_energy
```

Only present this as an estimate unless both sides are validated/calibrated.

---

## 6. One-session “Charge to 100%” tracking

Integrate with the planned Quick Settings tile:

```text
Charge to 100% — this session only
```

Log:

- tile activation/cancel timestamp;
- persistent daily charge ceiling;
- temporary effective ceiling;
- charging-session ID;
- SOC at activation;
- energy added after activation;
- peak battery temperature;
- time above 80%;
- time above 90%;
- time above 95%;
- time above 99%;
- clear reason:
  - `REACHED_100`
  - `UNPLUGGED`
  - `USER_CANCELLED`
  - `SESSION_INVALIDATED`
  - `SAFETY_STOP`

Useful user summary:

```text
"Charge to 100%" used 7 times this month
Average time above 90%: 2h 14m/session
Average peak temperature: 34.8 °C
```

Do not present such statistics as guaranteed battery degradation; present them as battery-stress context.

---

## 7. Battery health model

Do not pretend one noisy gauge field is absolute truth.

### Capacity

Track:

- design capacity;
- gauge FCC;
- observed usable throughput between calibrated SOC regions;
- long-term FCC trend.

### Internal-resistance estimate

Where sample quality permits:

```text
R_internal_est ≈ ΔV / ΔI
```

Only compute using stable, time-aligned load transitions.

### Equivalent full cycles

Track:

- hardware/gauge cycle count;
- throughput-derived EFC.

Example:

```text
EFC += discharged_Ah / reference_capacity_Ah
```

### High-SOC exposure

Cumulative time:

- >=80%;
- >=90%;
- >=95%;
- >=99%.

### Temperature exposure

Suggested bins:

```text
<0 °C
0–15 °C
15–30 °C
30–35 °C
35–40 °C
40–45 °C
>45 °C
```

### Charging stress context

Track distributions of:

- charge C-rate;
- charging temperature;
- PPS/direct-charge duration;
- time near maximum SOC.

### Confidence

Every health estimate should record:

```text
value
confidence
sample_count
measurement_window
source
```

Avoid false precision.

---

## 8. History views

### Since unplug

Show:

- elapsed time;
- screen-on/off time;
- energy consumed;
- average power;
- deep-sleep percentage;
- top wake sources;
- top UID CPU/network/wakelock consumers;
- display activity;
- radio activity;
- estimated remaining runtime.

### 24 h / 7 d / 30 d

Graph:

- SOC;
- voltage;
- current;
- power;
- temperature;
- FCC estimate;
- charge/discharge energy;
- deep-sleep residency;
- wakeups/hour;
- brightness/refresh;
- charging sessions.

### Lifetime

Store downsampled aggregates:

- cycle count;
- EFC;
- FCC trend;
- SOH trend;
- internal-resistance trend;
- high-SOC exposure;
- temperature exposure;
- fast-charge usage;
- number of 100% overrides;
- average daily energy throughput.

---

## 9. “Where did my battery go?” attribution

Candidate categories:

- display;
- CPU;
- GPU;
- cellular/modem;
- Wi-Fi;
- Bluetooth;
- GNSS;
- camera;
- thermal camera;
- rear display;
- audio;
- storage;
- uSmart/USB accessory;
- kernel-awake overhead;
- unattributed.

Do not fabricate precise subsystem wattage without a validated energy model.

Use confidence labels:

```text
MEASURED
MODELLED
PROXY
UNATTRIBUTED
```

---

## 10. Suspend / wakeup analytics

Track:

- suspend attempts;
- successful suspend;
- abort reason;
- resume source;
- wakeup-source count;
- wakeup-source hold time;
- IRQ delta around wake;
- AP awake duration after resume;
- CPU idle-state residency.

Example summary:

```text
Last 8 hours

Deep sleep:  7h 43m
Awake:          17m
Wakeups:        113

Top sources:
modem            63
wlan             21
touch             8
alarmtimer        5
other            16
```

---

## 11. Runtime-PM dashboard

For each device expose:

```text
state
runtime_status
usage_count
last_active
autosuspend_delay
wake_enabled
```

Priority devices:

- rear LCD;
- rear touch;
- thermal path;
- uSmart / shared USB0 fabric;
- NFC;
- AW883xx;
- camera PMU / sensors;
- SC8510;
- SC8571 master/slave;
- Wi-Fi;
- Bluetooth;
- GNSS;
- UFS.

Highlight devices that remain active unexpectedly while screen-off.

---

## 12. Low-overhead sampling

Do not wake the phone every second merely to measure how well it is sleeping.

### Screen on / charging / debug

Example:

```text
1–5 s live sampling
```

### Screen off

Prefer:

- event records;
- suspend/resume snapshots;
- kernel counters;
- batched low-frequency aggregates.

### Deep sleep

No periodic AP wake solely for telemetry.

Use pre-suspend/post-resume snapshots to reconstruct the interval.

---

## 13. Storage tiers

### Raw ring buffer

High resolution, short retention:

```text
minutes to hours
```

### Session store

Per:

- charging session;
- discharge session;
- screen-off session.

### Daily aggregates

Long retention:

- energy;
- throughput;
- wakeups;
- deep sleep;
- temperature exposure;
- SOC exposure;
- FCC/SOH.

Use schema versioning from day one.

---

## 14. Export

Privacy-safe diagnostic bundle:

```text
battery-summary.json
charging-sessions.csv
daily-energy.csv
wakeup-summary.csv
health-history.csv
power-timeline.parquet
metadata.json
```

Developer bundle may optionally include selected kernel trace snippets.

---

## 15. Alerts

Optional useful alerts:

- unusually high screen-off drain;
- failed deep sleep;
- unusually high battery temperature;
- repeated charging thermal throttling;
- significant FCC trend change;
- runtime-PM device active for hours;
- persistent wake-source regression;
- frequent daily-limit overrides.

Avoid alarmist battery-health claims from weak evidence.

---

## 16. Developer regression mode

Compare every kernel/ROM build using:

```text
screen_off_Wh_per_hour
screen_off_mAh_per_hour
deep_sleep_percent
wakeups_per_hour
suspend_aborts_per_hour
CPU_idle_residency
GPU_idle_residency
charging_efficiency_estimate
thermal_peak
```

Store kernel commit/build fingerprint with results.

---

## 17. Battery Lab pages

### Live
Electrical/system state.

### Since unplug
Drain and energy attribution.

### Charging
Current charging session + PPS/direct-charge details.

### Sleep
Deep sleep, wakeups, blockers.

### Hardware
Runtime-PM state.

### Health
FCC, SOH, EFC, resistance estimate, temperature/SOC exposure.

### History
24h / 7d / 30d / lifetime.

### Experiments
Compare profiles and kernel builds.

---

## 18. TODO

- [ ] Freeze exact primary gauge property contract.
- [ ] Reconstruct/freeze SH366003 measurement semantics.
- [ ] Freeze SC8571 ADC scaling and units.
- [ ] Document USB-C/PD/PPS observable properties.
- [ ] Define signed-current convention.
- [ ] Define telemetry database schema.
- [ ] Add kernel tracepoints to reconstructed Ulefone drivers.
- [ ] Implement suspend/wakeup aggregator.
- [ ] Implement adaptive sampling.
- [ ] Implement charging-session detector.
- [ ] Implement discharge-session detector.
- [ ] Implement EFC and high-SOC exposure counters.
- [ ] Implement battery temperature exposure bins.
- [ ] Implement long-term FCC/SOH estimator with confidence.
- [ ] Implement Battery Lab UI.
- [ ] Implement privacy-safe export.
- [ ] Add build/commit regression comparison.
- [ ] **Implement QS tile: `Charge to 100% — this session only`.**
- [ ] Keep persistent charge ceiling separate from temporary session override.
- [ ] Auto-clear 100% override on unplug/completion/cancel/invalid session/safety stop.
- [ ] Log 100% override usage and battery-stress context.
