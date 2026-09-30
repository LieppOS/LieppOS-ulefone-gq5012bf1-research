# U5 - thermal detector silicon, NETD, shutter, radiometry

**Current claim:** "Dedicated `fm78100` / `mediatek,tiny2c_usb` endpoint; OEM claim 640x512 at 25 Hz; exact detector/NETD/radiometry UNKNOWN."

**Previous confidence:** UNKNOWN.

**New evidence**
* The stock system partition ships two thermal applications that were invisible in the GSI snapshot: `system/app/M170infisens/M170infisens.apk` and `system/app/M170infDlp/M170infDlp.apk`.
* Their `arm64-v8a` native libraries are an **InfiRay/IRay thermal SDK**:
  `libAC020sdk.so`, `libadvirtempac020.so`, `libircmd020.so`, `libomniircamera020.so`, `libdualuvccamera020.so`, `libusbuvccamera020.so`, `libircam.so`, `libirutilssdk.so`, `libadvirparse.so`, `libadvirprocess.so`, `libdualcalibration.so`, `libcolormapping.so`, `libirpack_tool.so`.
* String evidence inside those libraries: **`infiray`**, **`mini640`**, `tiny2c`, `tiny1c`, and in `libircmd020.so` the module family list **`MINI225 MINI238 MINI264 MINI640`**. The repeated `020`/`AC020` suffix is InfiRay's **AC020 image-processing ASIC**.
* `vendor/etc/init/hw/init.yft.rc` creates the calibration directory `/mnt/vendor/nvcfg/infiray` under the comment `# YFT.liuyang InfiRay` (a sibling `/mnt/vendor/nvcfg/FLIR` exists for other ODM projects).
* The dual-camera libraries (`libdualuvccamera020.so`, `libdualcalibration.so`, `libgpudual.so`) show the module is used in **thermal + visible fusion**, and `libusbuvccamera020.so` shows the stream arrives over **USB UVC**, not the Android camera HAL - which is why the device exposes only four Android cameras.

**Contradicting evidence:** none. The DT/driver name is `tiny2c`, while the shipped calibration/target strings are `mini640`; the SDK supports both, and only the 640x512 figures match the product specification.

**Internet sources**
* VI1/VI3 (Ulefone): thermal sensor "**ThermoVue T2**", **640 x 512**, **25 Hz**, **NETD < 40 mK**, **12 um pixel pitch**, FOV 56 deg x 42 deg, range -20 to 550 degC, accuracy +/-2 degC, "Independent Infrared ISP", app "ThermoVue Pro".
* VI18/VI19: InfiRay **Mini640** = 640x512, 12 um pitch, radiometric version 25 Hz, typical NETD <= 40 mK, sold as a MINI module + companion ASIC.
* VI20: the same module family is retailed under the **"InfiRay / InfiSense Mini2 640"** branding - which explains the app name `M170infisens`.

**Local evidence:** VL16, VL17, VL18.

**Read-only live evidence:** i2c `8-003c` bound to `tiny2c_usb-sensor`; `/sys/class/yft_extcon/tiny2c_mode` present.

**Final conclusion**
The thermal core is an **uncooled VOx LWIR microbolometer, 640 x 512 at 12 um pitch, NETD <= 40 mK, radiometric, 25 Hz**, i.e. an **InfiRay (IRay/InfiSense) Mini640-class module with the InfiRay AC020 processing ASIC**, marketed by Ulefone as "ThermoVue T2". Radiometry is real, not interpolated: the SDK contains dedicated temperature libraries (`libadvirtemp.so`, `libadvirtempac020.so`) and the device stores per-unit calibration in `/mnt/vendor/nvcfg/infiray`. The OEM's "1280x1024 at 3 fps" figure is a software super-resolution mode, not a detector resolution.

**Final confidence:** **STRONGLY_SUPPORTED** (vendor SDK + calibration path + module-family strings + exact spec match). The precise orderable Mini640 sub-variant (lens focal length, radiometric SKU code, shutter/FFC hardware) is **TEARDOWN_REQUIRED**.

**Remaining uncertainty:** whether the module has a mechanical shutter for flat-field correction cannot be read from software; it needs a teardown or an FFC observation. The exact lens (Mini640 is offered with 4-75 mm options) follows from the stated 56x42 deg FOV but is not independently confirmed.

**Impact on final inventory:** YES - thermal row rewritten from "UNKNOWN core" to a named module family with quantified detector parameters.

**Answers:** (1) 640x512/12 um/25 Hz radiometric InfiRay module; (2) exact SKU, lens, shutter presence; (3) yes, largely; (4) yes - `sensor_id` sysfs read would add the module ID; (5) yes; (6) yes for the remainder; (7) InfiRay/InfiSense Mini640-class + AC020 ASIC ("ThermoVue T2"); (8) STRONGLY_SUPPORTED; (9) yes; (10) yes; (11) yes.

## Second-pass update (2026-09-08)

Independent module-market research again finds the Mini640 family at **640 x 512 / 12 um / radiometric
25 Hz / typical NETD <= 40 mK** (Q21, VI18, VI19), matching the ThermoVue T2 OEM fields and local
Mini640/AC020 library strings. No public source maps Ulefone's module label to an orderable lens/shutter SKU,
so lens focal length, radiometric sub-SKU and mechanical FFC shutter remain **TEARDOWN_REQUIRED**; overall
STRONGLY_SUPPORTED confidence is unchanged.
