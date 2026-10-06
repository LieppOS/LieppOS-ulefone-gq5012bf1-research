# U6 - the exact role of "FM78100"

**Current claim:** "node/driver name only"; role unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
* The DT node is `soc/i2c@11e03000/fm78100@0x3c`, but its `compatible` is `mediatek,tiny2c_usb` and the **driver that actually claimed it** is `tiny2c_usb-sensor` from module `yft_tiny2c_usb` (`buses.txt`: `8-003c -> /sys/bus/i2c/drivers/tiny2c_usb-sensor`).
* Disassembled strings of `vendor_dlkm/lib/modules/yft_tiny2c_usb.ko` show its entire function set:
  `gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d`, `%s: power on: %d` / `power off: %d`, `read sensor-id fail`, `dev_attr_sensor_id`, `dev_attr_tiny2c_usb_mode`, plus `i2c_transfer` and `of_get_named_gpio_flags`.
  It registers **both** an I2C client and a platform device (`platform:yft_tiny2c_usb`).
* The matching platform node `/yft_tiny2c_usb` supplies `tiny2c_usb_vdd_1v8`, `tiny2c_usb_vdd_3v3`, `tiny2c_usb_vddio_3v3` GPIOs.
* A **different** driver, `fm78100-sensor`, exists in the ODM software base: `init.yft.rc` chowns `/sys/bus/i2c/drivers/fm78100-sensor/{chip_power, chip_enable, chip_exist, mems_temp, ntc_temp, objs_temp}`. That sysfs surface - `objs_temp` (object temperature), `mems_temp`, `ntc_temp` - is the signature of a **single-point non-contact infrared thermopile thermometer**, not of an imaging core. **That driver is not bound on this device.**
* `/sys/module/mt6375_charger/holders/yft_tiny2c_usb` shows the thermal module's power path is interlocked with the charger driver.

**Contradicting evidence:** the node *name* still says `fm78100`, which invites the wrong conclusion that an FM78100 thermopile is fitted here.

**Internet sources:** none needed; no public FM78100 datasheet was located (this is recorded, not glossed over).

**Local evidence:** VL13, VL17, VL18.

**Read-only live evidence:** bus binding table and `/sys/class/yft_extcon/tiny2c_mode` from the frozen capture.

**Final conclusion**
On GQ5012BF1, **"fm78100" is a legacy node name inherited from a different ODM project variant** (one that fits a real FM78100-class IR thermopile). On this board the node is re-purposed: it is the **power-sequencing and identification endpoint of the InfiRay thermal-imaging module**. The bound driver does exactly three things - sequence the module's 1.8 V / 3.3 V / 5 V / IO-3.3 V rails, read a `sensor_id` over I2C address 0x3c, and expose a `tiny2c_usb_mode` switch. The imaging data itself does **not** flow through this I2C path; it arrives over an internal **USB UVC** link handled in userspace by the InfiRay SDK.

**Final confidence:** **PROVEN** (driver binding + module strings + init.rc are unambiguous).

**Remaining uncertainty:** the numeric `sensor_id` value that the driver reads was not captured, so the module's own ID byte is unknown. Whether a physical part marked "FM78100" exists anywhere on this board is **not** established - the evidence says the software path is not using one.

**Impact on final inventory:** YES - the thermal-interface row is corrected from "exact FM78100 silicon role unknown" to a described, proven power/ID endpoint, and the misleading implication of a fitted FM78100 thermopile is removed.

**Answers:** (1) it is the InfiRay module's power/ID I2C endpoint; (2) the `sensor_id` value and whether an FM78100 part physically exists; (3) yes; (4) yes - `cat .../sensor_id`; (5) no (no public datasheet); (6) only for the package-marking question; (7) not an FM78100 thermopile - it is the `yft_tiny2c_usb` control endpoint for the thermal camera; (8) PROVEN; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

External corroboration for the inherited-node explanation: FM78100 appears in multiple wearable BOMs as an
**infrared body-temperature sensor** (VI30). On this handset, however, the node binds `yft_tiny2c_usb`, whose
shipped module only sequences `tiny2c_usb_vdd_1v8` (GPIO 192), `_3v3` (GPIO 191), `_vddio_3v3` (GPIO 149)
and reads a `sensor_id`; it exposes no thermopile register/temperature interface. Thus FM78100 is a genuine
alternate-project part name, but on GQ5012BF1 the node remains the InfiRay module's power/ID endpoint, **not
an independently populated thermometer**.


## Correction (2026-10-06, `reverse-engineering/thermal-camera/`)

- The module is a Raytron/InfiRay **Tiny2-C (TC2-C), native 256×192**: M170infDlp ships
  `RS300_TC2C_…whole_package…zip` whose `whole_package.json` says `"device_name":"TINY2-C"`;
  M170infDlp `IR_SENSOR_WIDTH/HEIGHT = 256/386`; USB identity 3474:4321 equals the public
  Tiny2-C/TC001 descriptor (YUY2 256×194 / 256×386 @25 Hz). **640×512 is the marketing output
  after the app's `MNN_SR_TINY2C` super-resolution; native 640×512 is retracted.**
- `tiny2c_usb_vdd_5v` is not "unrecovered": the property is absent from the GQ5012BF1 DT.
- 8-003c ID value is known: `0x4c59` (reg 0x0001=0x4c, reg 0x0000=0x59).
- GPIO 55/152/28 belong to the uSmart accessory path, not to the thermal camera.
