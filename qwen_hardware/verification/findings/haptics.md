# U12 - haptic motor and haptic driver

**Current claim:** "one generic vibrator, no dedicated I2C IC" - motor and driver unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
* The live device tree contains exactly one haptic node:
  ```
  /regulator-vibrator {
      compatible = "regulator-vibrator";
      label      = "vibrator";
      min-volt   = <2200000>;   /* 2.2 V */
      max-volt   = <3500000>;   /* 3.5 V */
      vib-supply = <&mt6369_vibr>;
  };
  ```
* The supply resolves to `soc/spmi@1cc04000/second_pmic@5/regulators/vibr` = **`mt6369_vibr`**, a dedicated VIBR LDO inside the **MT6369 sub-PMIC**, range 1.2 - 3.5 V with `regulator-enable-ramp-delay = 680 us`. The board narrows the usable window to 2.2 - 3.5 V.
* **No dedicated haptic driver IC exists on any bus.** The full I2C/SPI enumeration contains no DRV2604/2605, no Awinic AW8624/AW86927, no Texas Instruments or Cirrus haptic part.
* `init.yft.rc` references `/sys/class/leds/aw_vibrator/{activate,brightness,cali,duration,state}` - an Awinic **closed-loop LRA** driver used on *other* ODM projects. Those nodes do not exist on this device, and no `aw_vibrator` module is shipped in `vendor_dlkm`.
* Consistent with this, the vibrator HAL exposes only `vibratorIds=[1]` with effect support and **no primitives, no frequency control and no amplitude/acceleration characteristics**.

**Contradicting evidence:** none.

**Internet sources:** none needed - the mechanism is fully determined locally. The Linux `regulator-vibrator` binding drives a motor by switching and setting a DC supply voltage.

**Local evidence:** VL22, VL17; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** `lights-vibrator.txt` capability dump from the frozen capture.

**Final conclusion**
The haptic actuator is driven **directly from the MT6369 PMIC's VIBR LDO through the generic `regulator-vibrator` driver**, with a 2.2 - 3.5 V board window and ~680 us enable ramp. There is **no haptic driver IC and no closed-loop resonance tracking**. Because `regulator-vibrator` can only apply a DC level - it cannot generate the AC drive an LRA needs at its resonant frequency - the actuator is an **ERM (eccentric rotating mass) motor**, not an LRA. This fully explains the effect-only, primitive-less vibrator HAL: rich haptics are impossible on this hardware, and no software change can add them.

**Final confidence:** drive topology (MT6369 VIBR LDO, no driver IC) = **PROVEN**. Motor type ERM = **STRONGLY_SUPPORTED** (inferred rigorously from the DC-only drive method). Motor manufacturer, model, size and rated voltage = **TEARDOWN_REQUIRED**.

**Remaining uncertainty:** the physical motor part number needs a teardown; its actual drive profile could be observed with a current probe on the VIBR rail.

**Impact on final inventory:** YES - the haptics row changes from "motor/driver IC UNKNOWN" to a proven drive topology plus a well-founded ERM classification, and the capability matrix stops implying that richer haptics might be unlockable.

**Answers:** (1) MT6369 VIBR LDO + generic regulator-vibrator, 2.2-3.5 V; (2) the motor's part number; (3) yes for the drive path; (4) yes (sysfs is already exposed); (5) no; (6) yes for the motor; (7) ERM motor on `mt6369_vibr`, no haptic IC; (8) PROVEN drive / STRONGLY_SUPPORTED ERM / TEARDOWN_REQUIRED part; (9) yes; (10) yes; (11) yes - "rich haptics" is removed as a possibility.
