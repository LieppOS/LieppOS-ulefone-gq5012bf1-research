# U21 - cooling material stack

**Current claim:** "thick/heavy chassis and thermal policy" - internal cooling construction unknown.

**Previous confidence:** UNKNOWN.

**New evidence (all indirect; no software can see a heat spreader)**
* **Thermal instrumentation is extensive**: HAL zones for CPU, GPU, NPU, TPU, SOC, SKIN, BATTERY, USB_PORT and POWER_AMPLIFIER, with throttling thresholds of 85/90/100/117 degC for the silicon zones, 43/45/55/65/75/80 degC for SKIN, 50/55/59/60 degC for BATTERY and 68/90/100/110 degC for the PA.
* **Four board NTC thermistor channels** (`thermal-ntc1/2/3/6`, `mediatek,mt6685-tia-ntc`, 1328-byte lookup tables each) plus PMIC-internal sensors (`mt6363-temp`, `mt6369-temp`) and a `vtskin` virtual skin model.
* **Cooling devices are all electrical, not mechanical**: `backlight-cooler`, `charger-cooler`, `wifi-cooler`, Mali devfreq, flashlight cooler, `cpu-power-throttling`, `gpu-power-throttling`, `md-power-throttling`, `low-battery-throttling`, `bp-thl`. **There is no fan, pump, TEC or any actuated cooling device anywhere in the device tree.**
* Observed steady-state at capture: CPU/GPU/NPU/TPU/SOC all ~46.8 degC with a cached peak of 64.7 degC, skin 39.2 degC, battery 37.0 degC, USB port 43 degC, PA 39.7 degC - all identical across the silicon zones, i.e. a single shared die sensor set.
* **Physical context from the OEM**: the phone weighs about **688 g** and is IP68/IP69K + MIL-STD-810H rated. That mass and the required sealing imply a thick metal mid-frame with a fully passive, gasket-sealed thermal path.

**Contradicting evidence:** none. Ulefone does not claim a vapour chamber for this model in any of the reviewed material, so the earlier "vapour chamber?" question was speculative from the start.

**Internet sources:** VI7, VI8 (IP/MIL ratings, ~688 g). Q10 found **no** teardown or FCC internal photographs for GQ5012BF1.

**Local evidence:** thermal zone/cooling-device inventory in `thermal-power.txt`; DT NTC and throttling nodes.

**Read-only live evidence:** the frozen thermal HAL dump.

**Final conclusion**
Cooling is **entirely passive and software-governed**: nine thermal zones, four board thermistors plus PMIC sensors, and ten purely electrical cooling devices (backlight, charger, Wi-Fi, GPU devfreq, flashlight, CPU/GPU/modem power throttling). **No active cooling hardware of any kind exists.** The physical heat-spreading stack - graphite sheet, copper foil, thermal gel, whether any vapour chamber is present, and how the thermal camera and charge pumps are coupled to the chassis - is **not observable in software and remains undetermined**.

**Final confidence:** "no active cooling; passive + aggressive software throttling" = **PROVEN**. Material stack = **TEARDOWN_REQUIRED**.

**Remaining uncertainty:** requires a teardown with layer photography, or thermal-camera imaging of the running board. Note the amusing corollary that this phone's own InfiRay module could image a second unit's internals.

**Impact on final inventory:** YES - the cooling row now states positively that there is no active cooling, instead of leaving "vapour chamber" as an open possibility.

**Answers:** (1) passive only, richly instrumented; (2) the physical layer stack; (3) no; (4) no; (5) no; (6) yes; (7) passive spreader of unknown composition; (8) TEARDOWN_REQUIRED (material) / PROVEN (no active cooling); (9) yes; (10) yes; (11) yes - "active vapour chamber" is downgraded from open question to disproven-in-software.

## Second-pass update (2026-09-08)

Runtime corroboration: `thermal-power.txt` exposes exactly five cooling devices to the framework -
`devfreq-13000000.mali`, `charger-cooler`, `flashlight_cooler`, `lcd-backlight`, `wifi-cooler` (VL28). A
full-tree scan of the live DT plus `dmesg.txt` finds **no** fan, TEC, BLDC, tachometer or `pwm-fan` object:
the only cooling providers in the tree are `backlight-cooler`, the three LED drivers' `#cooling-cells`, and
`mali@13000000`; the only PWM controllers are `disp-pwm0/1` (panel backlight) and `pwm@11008000`, whose
consumers are `irtx_pwm` and `ln2403_pwm`. "No active cooling hardware of any kind" therefore holds at the
runtime thermal-HAL level as well as at DT level. Material stack remains TEARDOWN_REQUIRED.
