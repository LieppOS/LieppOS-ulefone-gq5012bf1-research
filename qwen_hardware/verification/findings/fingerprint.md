# U15 - fingerprint die and scan geometry

**Current claim:** "SPI1 + Microarray/TEE generic identity" - exact die unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
* **Vendor is confirmed by three independent artefacts**: the SPI client `spi1.0` binds to `/sys/bus/spi/drivers/madev` from module **`microarray_fp_tee`**; the character device is `/dev/madev0` with SELinux label `mafinger_device`; and the HAL library is `/vendor/lib64/hw/microarray.fingerprint.default.so`. The vendor is **Microarray Microelectronics (MaFinger)**.
* **Bus and power**: `soc/spi1@11011000/fingerprint@0`, `compatible = "mediatek,madev_finger"`, `spi-max-frequency = 8000000` (8 MHz), `vfp-supply` from a dedicated regulator, `status = "okay"`.
* **A companion control node exists**: `/yft_finger` with `int-gpio` = pin 3, `reset-gpio` = pin 30, and **16 pinctrl states** including `finger_power_en0/1`, `finger_reset_en0/1` and full SPI-pin-to-GPIO remuxing (`finger_spi0_{mi,mo,clk,cs}_as_gpio`) plus EINT pull configuration. That remuxing capability is typical of a sensor whose SPI lines must be parked during low-power or secure phases.
* **Two vestigial fingerprint nodes are present but inert**: `/fingerprint` (`mediatek,goodix-fp`) and `/ft_fingerprint` (`focaltech,fp`). Neither has a `reg`, a bus parent or a status property, and no Goodix or FocalTech fingerprint module is shipped - they are ODM alternates for other projects.
* An `init.yft.rc` entry exposes `/sys/bus/platform/drivers/yft_finger/tplcd_pattern`, linking the fingerprint flow to an on-screen pattern - consistent with an **optical under-display** sensor that needs the panel to illuminate the finger, rather than a capacitive side-mounted one.
* 8 MHz SPI is a low image-transfer rate; combined with TrustKernel TEE matching, image data is handled inside the secure world.

**Contradicting evidence**
The original inventory called the sensor "capacitive" without evidence. The shared `tplcd_pattern` hook is compatible with optical operation, while an independent review reports side-mounted placement. Neither the device tree nor the HAL states modality/location outright, so both physical interpretations remain open rather than one replacing the other.

**Internet sources:** no public Microarray part-level datasheet was located for this die (recorded as a miss, not filled by inference).

**Local evidence:** VL13, VL17; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** `/dev/madev0` node and driver binding from the frozen capture.

**Final conclusion**
The fingerprint sensor is a **Microarray (MaFinger) module on SPI1 at 8 MHz**, powered through a dedicated `vfp` rail with reset on GPIO 30 and interrupt on GPIO 3, matched inside a **TrustKernel TEE**, and integrated with a display-illumination pattern hook. **The exact die part number is not present anywhere in software** - the driver, HAL and device tree all use the generic `madev` naming.

**Final confidence:** vendor, bus, transport, power/IRQ topology and TEE integration = **PROVEN**. Exact die part number, physical location, modality and scan geometry = **TEARDOWN_REQUIRED**. The `tplcd_pattern` hook makes optical plausible, while an independent review reports side-mounted placement; neither is silicon proof.

**Remaining uncertainty:** the die marking and physical mounting require teardown. Modality/location could be narrowed non-destructively on stock software by observing the enrolment target and whether a bright panel-illumination pattern appears.

**Impact on final inventory:** YES - vendor and transport are firmed up, the unsupported "capacitive" descriptor is withdrawn, and the two vestigial Goodix/FocalTech nodes are documented as ODM alternates.

**Answers:** (1) Microarray module, SPI1 8 MHz, TEE-matched; (2) die marking, modality and physical location; (3) partially; (4) yes for modality/location by observing stock enrolment; (5) no; (6) yes for the part number; (7) Microarray/MaFinger, modality unresolved; (8) PROVEN vendor / TEARDOWN_REQUIRED die and geometry; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

Runtime nodes sharpen the stack but not the die: `/dev/madev0` is labelled `mafinger_device`, and
`/dev/tkcore_fp` is labelled `tkcore_client_device`, confirming the MaDev userspace path and TrustKernel/
TkCore secure-world transport (VL28). The capture's GSI has no registered framework fingerprint service,
so runtime resolution/modality metadata could not be queried. External family-level evidence confirms that
Microarray Technology markets fingerprint devices under **MaDev / MAFP** naming (VI31), but exposes no
phone-module die mapping.

One low-quality independent review calls the scanner **side-mounted** (VI26), in tension with the generic
`tplcd_pattern` display-pattern hook that motivated pass 1's optical hypothesis. The OEM pages and local
software do not settle the location, and the hook may be shared ODM code. Therefore no confidence upgrade
is warranted: vendor/bus/TEE remain PROVEN; **die, physical location and scan modality remain
TEARDOWN_REQUIRED**, with optical only a software-derived possibility rather than a reliable inventory fact.
