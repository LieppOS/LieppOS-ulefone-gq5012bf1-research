# LieppOS GQ5012BF1 — Kernel Enhancement Roadmap

**Device:** Ulefone Armor 29 Pro Thermal (`GQ5012BF1`)  
**SoC:** MediaTek MT6878 / MT6878T  
**Project:** LieppOS  
**Status:** Design roadmap. Implement after the source-built 6.1 baseline is stable and measurable.

## 1. Philosophy

LieppOS should not become a pile of unmeasured "custom-kernel tweaks".

Every kernel modification should satisfy three rules:

1. **Measurable** — record before/after power, latency, thermal, wakeup, and stability data.
2. **Hardware-aware** — prefer proper runtime PM, event-driven drivers, scheduler energy models, and real device power gating.
3. **Safe** — never weaken battery, charger, thermal, voltage, current, or security protections merely to improve benchmark numbers.

The production goal is:

> Fewer wakeups, deeper idle, less unnecessary hardware activity, efficient burst performance, and coherent whole-device power policy.

---

## 2. Priority roadmap

| Priority | Project | Primary goal | Expected value | Risk |
|---:|---|---|---:|---:|
| 1 | LieppOS Power Observatory | Measurement | Very high | Low |
| 2 | Wakeup/polling elimination | Standby | Very high | Medium |
| 3 | Peripheral Runtime PM | Standby | Very high | Medium |
| 4 | Dynamic 60/90/120 Hz display policy | Screen-on power | Very high | Low |
| 5 | MT6878 Energy Model / EAS / uclamp tuning | Efficiency | Very high | Medium |
| 6 | GPU + DRAM/interconnect power tuning | Efficiency | High | Medium |
| 7 | Battery-health charging policy | Longevity | Very high | Medium |
| 8 | Rear-display / thermal / uSmart power gating | Standby | High | Medium |
| 9 | SC8571 runtime-PM and polling cleanup | Charging + standby | High | Medium |
| 10 | Fuel-gauge polling optimization | Standby | Medium | Medium |
| 11 | Storage/network autosuspend | Standby | Medium | Medium |
| 12 | Thermal-aware sustained-performance policy | Efficiency | High | Medium |
| 13 | New hardware features / accessory APIs | Functionality | Variable | Variable |

---

## 3. LieppOS Power Observatory

Implement this before aggressive tuning.

Collect:

- battery voltage, current, power, temperature, SOC and charge counters;
- primary and secondary gauge data when available;
- charger input/output ADC values;
- USB-C / PD / PPS state;
- CPU frequency and idle residency;
- scheduler/uclamp state;
- GPU devfreq and activity;
- DRAM/interconnect frequency and bandwidth votes;
- runtime-PM state for major peripherals;
- wakeup-source counts and hold time;
- IRQ counts;
- suspend attempts, abort reasons, and deep-sleep residency;
- thermal-zone history and throttling state;
- Wi-Fi / Bluetooth / GNSS activity;
- UFS runtime-PM state;
- display refresh rate and brightness;
- rear-display, thermal-camera and uSmart power state;
- camera LDO state;
- charge-pump state.

The observatory must be low-overhead. Prefer event/tracepoint aggregation and adaptive sampling rather than waking the AP every second while the screen is off.

See `power/battery-telemetry-tracker.md`.

---

## 4. Eliminate unnecessary periodic wakeups

Audit every:

- `delayed_work`;
- timer;
- polling thread;
- recurring I2C/SPI transaction;
- heartbeat/debug worker.

Classify each:

- `REQUIRED_PERIODIC`
- `CAN_RUN_SLOWER`
- `CAN_USE_IRQ`
- `ACTIVE_ONLY`
- `REMOVABLE`

Example desired behavior:

```text
screen on / charging:
    normal polling

screen off / stable:
    slower periodic check or interrupt-driven update

fault / significant event:
    immediate IRQ-driven update
```

Do not weaken battery-state estimation or safety monitoring.

---

## 5. Peripheral Runtime PM

Major device drivers should implement meaningful runtime suspend/resume behavior where hardware supports it.

Priority devices:

- rear LCD;
- rear touch controller;
- thermal-camera path;
- uSmart USB/accessory path;
- camera sensors;
- WL2868 camera PMU;
- AW883xx amplifiers;
- ST21 NFC;
- SC8510;
- SC8571 master/slave;
- GNSS;
- Wi-Fi;
- Bluetooth;
- fingerprint glue;
- LED controllers.

Desired inactive state should include, when safe:

- regulators off;
- clocks off;
- PHYs suspended;
- IRQ wake disabled unless needed;
- GPIOs in low-leakage state;
- bus controllers autosuspended;
- workqueues stopped.

---

## 6. Main-display refresh policy

The VTDR6115 contract exposes 60/90/120 Hz modes.

Recommended policy:

```text
interaction / animation -> 120 Hz
short idle             -> 90 Hz
static content         -> 60 Hz
```

Max Battery:

```text
60 Hz ceiling
```

Policy inputs should eventually include:

- SurfaceFlinger requested mode;
- touch activity;
- actual frame cadence;
- GPU load;
- thermal state;
- battery profile.

---

## 7. MT6878 scheduler and CPU energy tuning

Measure before changing.

Investigate:

- Energy Aware Scheduling;
- Energy Model accuracy;
- `schedutil`;
- uclamp policy;
- task placement;
- migration thresholds;
- CPU idle residency;
- cluster wake cost;
- top-OPP efficiency.

Desired behavior:

```text
background -> efficient CPUs
foreground -> sufficient cluster
short heavy burst -> big core allowed
work complete -> big core returns idle quickly
```

Do not blindly disable cores.

---

## 8. GPU power policy

Investigate:

- devfreq governor;
- minimum and maximum OPP;
- boost duration;
- autosuspend delay;
- GPU power-domain shutdown;
- stale memory/interconnect votes.

Max Battery may combine:

```text
60 Hz display
+ lower GPU ceiling
+ shorter boost
+ faster idle/downclock
```

---

## 9. DRAM / interconnect / QoS audit

Instrument MediaTek:

- SMI;
- MMDVFS;
- interconnect;
- QoS;
- DRAM/devfreq votes.

Detect leaked votes after camera, GPU, display, codec, or ISP activity ends.

Development builds should answer:

```text
current memory frequency
current bandwidth vote
requesting subsystem
age of the vote
```

---

## 10. Ulefone-specific peripheral gating

### Rear display + rear touch

When unused:

- panel rail off;
- touch rail off if safe;
- SPI/I2C runtime suspended;
- unused IRQ wake disabled;
- clocks off.

### Thermal camera

When no thermal application/session exists:

- USB/accessory path idle;
- associated camera power off;
- no recurring worker.

### uSmart

Current research places uSmart VBUS/control on MT6375 `usb-otg-vbus` plus
`extcon-mtk-usb` over the shared USB0 / MTU3 / USB2 fabric, not SC851x and not a
separate USB controller.

Desired state machine:

```text
NO ACCESSORY
    VBUS off
    shared USB2 PHY suspended
    mux idle
    detect only

ACCESSORY PRESENT
    route the shared USB0 / MTU3 fabric to the accessory
    enable required OTG/accessory power
    enumerate

REMOVED
    suspend USB
    VBUS off
    mux idle
```

### Camera LDO

Track WL2868 consumers and assert in debug builds that all camera rails return off after the final camera consumer closes.

---

## 11. SC8571 charging runtime power

After reconstruction, determine whether both SC8571 devices can safely reduce activity outside direct charging.

Potential inactive state:

- charge pump disabled;
- ADC disabled;
- unnecessary watchdog/worker stopped;
- event/fault IRQ retained as required;
- runtime suspended if supported.

During PD/PPS direct charging:

- resume;
- configure;
- enable required ADC/monitoring;
- preserve all hardware safety thresholds.

Never disable OVP/OCP/thermal protections for power savings.

---

## 12. Battery-health charging policy

Implement through proper Android Health/Power/charging integration rather than raw shell scripts.

Candidate features:

- selectable charge ceiling: 70/75/80/85/90/100%;
- adaptive overnight charging;
- Battery Health reduced-power charging profile;
- temperature-aware reduction of requested charging power;
- optional fast-charge toggle;
- charging-session history and health estimates.

Safety rule:

> Software may request less charging power. It must never raise proven hardware safety limits.

---

## 13. Power profiles

Recommended profiles:

### Performance
- full CPU/GPU ceilings;
- high refresh allowed;
- normal background policy.

### Balanced
- dynamic 60/90/120 Hz;
- energy-aware CPU placement;
- normal radios/peripherals.

### Battery
- stronger background uclamp;
- faster GPU downclock;
- aggressive peripheral autosuspend;
- reduced scan/poll rates.

### Max Battery
- 60 Hz ceiling;
- efficient CPU/GPU ceilings;
- rear display disabled unless explicitly opened;
- thermal/uSmart power demand-only;
- aggressive radios/autosuspend;
- minimal background activity.

### Sleep
Internal screen-off state emphasizing maximum deep-suspend residency while preserving required wake sources.

Prefer Android Power HAL/system service integration over many raw sysfs knobs.

---

## 14. Wakeup and suspend regression testing

Track at minimum:

- screen-off drain `%/h`;
- screen-off drain `mAh/h`;
- screen-off drain `Wh/h`;
- deep-sleep percentage;
- wakeups/hour;
- suspend aborts/hour;
- top wake sources;
- average AP awake duration per wake;
- CPU idle-state residency.

Every optimization must be compared against a known-good baseline.

---

## 15. Production vs debug kernel

### Production
- minimal logs;
- tracing disabled by default;
- security features enabled;
- no expensive debug checks.

### Debug
Use when needed:

- ftrace / tracepoints;
- Perfetto-compatible tracing;
- PM debug;
- scheduler and DVFS events;
- runtime-PM events;
- interconnect/QoS events;
- charger/gauge tracing;
- wakeup-source diagnostics.

Candidate custom tracepoints:

```text
lieppos_panel_refresh
lieppos_usmart_power
lieppos_rear_display_power
lieppos_camera_ldo
lieppos_sc8571_state
lieppos_battery_sample
```

---

## 16. One-session “Charge to 100%” Quick Settings tile

### Goal

Users may normally configure, for example:

```text
daily charge limit = 80%
```

The Quick Settings tile temporarily allows:

```text
CHARGE TO 100% — THIS SESSION ONLY
```

without changing the saved daily charge limit.

### Required behavior

When tapped:

```text
persistent_user_limit = 80
temporary_session_override = 100
effective_limit = 100
```

The override MUST clear automatically when:

1. charger is physically disconnected;
2. 100% / charge-complete is reached;
3. the user cancels the override;
4. the charging session becomes invalid/ambiguous;
5. a charging safety stop occurs.

After clearing:

```text
effective_limit = persistent_user_limit
```

Example:

```text
daily limit = 80%

plug in
    ↓
tap "Charge to 100%"
    ↓
charge to 100%
    ↓
override clears
    ↓
next physical charging session stops at 80%
```

### Required state separation

Never overwrite the persistent setting.

Maintain:

```text
persistent_user_limit
temporary_session_override
charging_session_id
```

Conceptually:

```text
if override belongs to current charging_session_id:
    effective_limit = 100
else:
    effective_limit = persistent_user_limit
```

### UI

Suggested tile states:

- `Charge limit 80%`
- `Charging to 100% once`
- active tile tap again = cancel

Optional notification:

> Charging to 100% for this session. Your normal charge limit will return automatically afterward.

### Architecture

Do not implement this as a shell script writing a raw sysfs node.

Preferred path:

```text
QS Tile
  ↓
SystemUI / privileged LieppOS service
  ↓
Battery policy service
  ↓
Health / charger HAL
  ↓
kernel charging policy
```

### Safety

The tile changes only the SOC target/ceiling. It must not:

- raise battery voltage limits;
- raise OVP/OCP limits;
- raise current beyond stock-safe limits;
- bypass thermal protections;
- fake SOC;
- force charging through a reported fault.

### Telemetry

Log:

- activation timestamp;
- cancel timestamp;
- starting SOC;
- persistent limit;
- effective limit;
- charging-session ID;
- energy added under override;
- peak temperature;
- time above 80/90/95/99%;
- clear reason.

---

## 17. Changes to avoid

Do not ship:

- random CPU governors;
- blind undervolting;
- universal core parking;
- thermal-limit removal;
- charger protection increases;
- fsync disabling;
- SELinux disabling;
- random scheduler patchsets without measurements;
- huge undocumented sysfs interfaces;
- permanent verbose vendor logs;
- fake "RAM optimizer" modifications.

---

## 18. Acceptance criteria

A power optimization is accepted only when it has:

1. source-level rationale;
2. before/after telemetry;
3. battery/energy impact;
4. performance impact;
5. thermal impact;
6. suspend/wakeup impact;
7. stability test;
8. hardware safety review;
9. rollback path.

---

## 19. Suggested implementation order

```text
1. Stable source-built 6.1 hardware baseline
2. Power Observatory
3. Wakeup-source baseline
4. Peripheral runtime-PM audit
5. Dynamic refresh policy
6. CPU Energy Model / EAS / uclamp tuning
7. GPU + memory/interconnect tuning
8. SC8571 and gauge polling cleanup
9. Android power-profile integration
10. Battery-health charging controls
11. One-session 100% QS tile
12. Long-duration regression testing
13. Carry validated policy to newer kernel generations
```

The 6.1 branch remains the hardware/reference baseline. Newer GKI ports should carry forward only improvements already proven against this baseline.
