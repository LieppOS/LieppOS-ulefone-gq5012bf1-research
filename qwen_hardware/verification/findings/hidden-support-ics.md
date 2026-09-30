# U24 - board-level support ICs not previously catalogued

**Current claim:** "not software-visible" - incomplete BOM.

**Previous confidence:** UNKNOWN.

**New evidence - parts discovered in this pass that the original inventory did not list**

| Part / node | Where | Function | Confidence |
|---|---|---|---|
| **MT6363** | SPMI `pmic@4` | main system PMIC (regulators, auxadc, efuse, pinctrl, power keys, dynamic-load throttling) | PROVEN |
| **MT6369** | SPMI `second_pmic@5` | sub-PMIC + **audio codec** (`mt6369codec`) + **headset accdet** + `VIBR` haptic LDO + `vio28` supply for IR TX | PROVEN |
| **MT6319** | SPMI `mt6319@6` | external buck regulator (`extbuck-debug`, `mt6319-6-regulator`) | PROVEN |
| **MT6685** | SPMI `mt6685_mfd` | clock buffer + RTC + consys support, and the **TIA-NTC thermistor front end** feeding `thermal-ntc1/2/3/6` | PROVEN |
| **SC8510** | i2c `6-0069` | bidirectional switched-capacitor converter (reverse/OTG power path) - previously mis-recorded as "SC851x-class companion" | PROVEN |
| **Chipone CO5300** | spi0.0 | rear 1.04-inch AMOLED display driver IC | PROVEN |
| **Natlinear LN2403 (likely)** | `/yft_camplight` | PWM/PFM buck constant-current LED driver for the auxiliary camping/work light: `ln2403-en-gpio`, `ln2403-power-gpio`, `ln2403_pwmon` / `pwmoff_*`, alongside red/blue/power GPIOs | node/wiring PROVEN; exact part **LIKELY** from matching LN2403 2 A LED-driver datasheet (VI29) |
| **IR transmitter path** | `/irtx-pwm` | `mediatek,irtx-pwm`, PWM-driven, supplied from `mt6369_vio28` | node PROVEN, emitter population UNVERIFIED |
| **FM receiver** | `/fm`, `/fmradio` | MediaTek connsys FM (`family-id 0x6983`, `host-id 0x6878`, `conn-id 0x205`), `status = "okay"`, discrete `fm_lna_gpio` (pin 72); FM firmware `fm_cust.cfg` + `soc_fm_v1_patch/coeff.bin`; stock app `YftFmRadio.apk`; antenna switched from the headset jack via `gpio-accdet-fm-switch` (pin 195) | PROVEN |
| **3.5 mm headset jack** | `second_pmic@5/accdet` | `mediatek,mt6369-accdet`, `status = "okay"`, 3-key and 4-key threshold tables, efuse-calibrated | PROVEN |
| Four board NTC thermistors | `thermal-ntc1/2/3/6` | discrete temperature sensing with per-channel lookup tables | PROVEN |
| `/yft_device` | platform | `urxdo_gpio_select` (pin 186) and `yft_fm_switch` class node | PROVEN |
| Second main-panel option | `dsi0/panel2@1` | `jdi,nt36672e,vdo,60hz` - unused JDI/Novatek LCD alternative | PROVEN (as an option) |
| Unused actuator drivers | `vendor_dlkm` | `main3_vcm.ko`, `sub_vcm.ko` shipped with no device-tree client | PROVEN |

**ODM option catalogue that must NOT be read as fitted hardware.** `vendor/etc/init/hw/init.yft.rc` is shared across many YFT/Ulefone projects and references sysfs paths for parts this device does not have: `mt5786group` wireless charging, `aw_vibrator` (Awinic LRA), `radio_rtc6226` (discrete FM tuner), `dlp3430` projector motor, `as1509-sensor` angle sensor, `yft_distance_meas` laser rangefinder, `fs16xx` speaker amp, `aw22xxx_led` LED matrix, `mt6360_pmu_rgbled`, dual `fg_main_*`/`fg_sub_*` gauges on i2c-1/i2c-10, and `spi4.0` touch. **None of those buses, devices or classes exists on GQ5012BF1** - the file simply enumerates the ODM's build options. Related: `vendor/etc/camera/eis/morphoEISCalibration_DOOGEE_M24PS.bin` shows the same software base is shared with a Doogee model.

**Contradicting evidence:** none, provided the ODM catalogue is not misread. Flagging that trap is itself one of the results of this pass.

**Internet sources:** VI12-VI17 for pass-1 parts; VI29 resolves LN2403 at datasheet-family level; VI32 covers AW36515/AW36518.

**Local evidence:** VL13, VL17, VL23, VL24, VL26; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** SPMI/I2C/SPI enumeration from the frozen capture.

**Final conclusion**
Thirteen board-level elements that the original inventory missed are now catalogued, including the **entire SPMI PMIC tier** (MT6363/MT6369/MT6319/MT6685), the **rear-display DDIC**, the **reverse-power charge pump**, an **FM radio receiver with a real antenna switch**, a **3.5 mm headset jack**, an **IR transmitter PWM path**, and the **auxiliary light driver**. Truly invisible passives - ESD arrays, level shifters, crystals, RF filters, connectors - remain outside software's reach.

**Final confidence:** bound listed parts = **PROVEN**; LN2403 node/wiring = **PROVEN** and exact Natlinear part = **LIKELY**; IR PWM path = **PROVEN** but emitter population and usable HAL = **UNVERIFIED**. Passive/discrete remainder = **TEARDOWN_REQUIRED**.

**Remaining uncertainty:** a complete BOM needs board photography. The IR-TX question is nearly free to settle: on stock software, look for a remote-control app or test `/dev/pwm` consumer behaviour.

**Impact on final inventory:** YES - substantial additions to MASTER-HARDWARE-INVENTORY, plus two genuinely new user-facing capabilities (FM radio, 3.5 mm jack) for the hidden-capability report.

**Answers:** (1) support tier catalogued; (2) passives/RF discretes, IR emitter and exact LN2403 confirmation; (3) yes for bound active parts; (4) yes for IR functionality; (5) LN2403 now likely identified; (6) yes for passives and remaining markings; (7) see table; (8) per-row confidence retained; (9) yes; (10) yes; (11) yes.

## Second-pass update (2026-09-08)

Two upgrades and one new distinction.

* **LN2403 upgraded from UNKNOWN to LIKELY identified.** Natlinear LN2403 = CMOS **PWM/PFM buck
  constant-current LED driver, up to 2 A**, 2.5-6.0 V, 40 uA quiescent, 100 % duty capable, SOT23-5, with
  OVP/OCP/OTP (VI29). The DT wiring matches that part exactly: `yft_camplight` drives
  `ln2403-power-gpio = <74>`, `ln2403-en-gpio = <91>` and three pinctrl states named
  `ln2403_pwmon` / `ln2403_pwmoff_high` / `ln2403_pwmoff_low` - a PWM-dimmed buck LED string - alongside
  `leds-power 153`, `leds-red 20`, `leds-blue 21`. Part-level identification is datasheet-grade; the
  physical emitter (white camp light + red/blue warning LEDs) is still only inferable from the GPIO names,
  so it stays **LIKELY**, not PROVEN.
* **The lighting tier is now fully attributed** (L21 + VI32): `aw36515` bound at `6-0063` = Awinic dual
  independent **2 A** flash/torch/IR LED driver with 2 MHz or 4 MHz synchronous boost and IVFM;
  `aw36518_v2` bound at `12-0063` and `aw36518` bound at `8-0063` = Awinic **1.5 A** flash/IR LED drivers;
  `leds-rgb-aw2013` bound at `11-0045` = Awinic AW2013 RGB notification LED controller; plus the LN2403
  path above and the three LED drivers' `#cooling-cells` registrations (flashlight_cooler).
* **IR blaster distinction corrected (2026-09-27).** DT ships enabled `/irtx-pwm`
  (`mediatek,irtx-pwm`, `pwm-ch = <0>`, `dma-mask-bit = <35>`, `pwm-supply = mt6369_vio28`). The AOSP
  `android.hardware.ir-service.example` is the AIDL binder wrapper, while
  `ro.hardware.consumerir=common` selects shipped MediaTek backend `consumerir.common.so`. That backend
  opens `/dev/lirc0`; rc-core routes it to `mtk_irtx_pwm.ko` and `mtk-pwm.ko`. Software ownership and the
  LIRC/PWM ABI are therefore PROVEN; the physical emitter and waveform remain UNVERIFIED. See
  `ir-blaster.md`. The unrelated face service remains an AOSP example and is not upgraded by this finding.
