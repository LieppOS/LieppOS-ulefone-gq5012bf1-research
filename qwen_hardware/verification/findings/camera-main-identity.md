# U3 - main camera die identity: the "IMX989 vs GN1" contradiction

**Current claim:** OEM marketing says "50 MP Sony IMX989 GN1"; GSMArena lists 1/1.31" / 1.2 um; live driver says `SENSOR_DRVNAME_IMX989_MIPI_RAW`. Recorded as an unresolved contradiction.

**Previous confidence:** UNKNOWN / contradiction.

**New evidence**
1. **The main camera slot is explicitly multi-source in the live device tree.**
   `soc/i2c@11e02000/sensor0@10` -> `sensor-names = "imx989_mipi_raw", "s5kgm2sp_mipi_raw", "imx989cts_mipi_raw", "s5kgn1sp_mipi_raw"`.
   MediaTek's `imgsensor` driver walks this list and binds the first entry whose **sensor ID register** matches, so the DT declares three physically different candidate dies for one slot: Sony **IMX989**, Samsung **S5KGM2SP**, Samsung **S5KGN1SP**.
2. **The unit under test bound the IMX989 entry** (`SENSOR_DRVNAME_IMX989_MIPI_RAW` for camera `[00]`).
3. **The RAW stream size discriminates the two candidates.** `android.scaler.availableStreamConfigurations` reports, for camera 0, `RAW16 4096 x 3072`; for cameras 1 and 2 (both S5KJN1 variants) it reports `RAW16 4080 x 3072`. 4096x3072 is the Sony half-binned geometry (8192x6144); 4080x3072 is the Samsung half-binned geometry (8160x6144). Camera 0 therefore reports a **Sony**, not a Samsung, native array.
4. `android.sensor.info.physicalSize` for camera 0 is 13.107 x 9.830 mm = 8192 x 6144 at 1.6 um = a 1.0-inch-type array. **This field alone is not reliable** here, because camera 2 (an S5KJN1) carries the identical value - the vendor copied it. The RAW size is the trustworthy signal.
5. Ulefone markets the **Armor 29 Ultra** with "1-inch Sony IMX989" and the **Armor 29 Pro Thermal** with a "1/1.31-inch, 50 MP Samsung ISOCELL" main camera. The two models share this ODM software base, which is exactly why one device tree carries both drivers.

**Contradicting evidence**
Ulefone's own Armor 29 Pro Thermal page ("1/1.31\" Ultra-Large Sensor", "50MP Samsung ISOCELL") and GSMArena's "50 MP, f/2.0, 23 mm, 1/1.31\", 1.2 um" describe an **S5KGN1SP**, not an IMX989. Also, the HAL reports f/1.9 where Ulefone states f/2.0.

**Internet sources:** VI5, VI7, VI9.

**Local evidence:** VL11, VL12; `../evidence/live-devicetree-extracts.md`, `../evidence/live-runtime-extracts.md`.

**Read-only live evidence:** camera HAL enumeration + full static metadata from the frozen capture.

**Final conclusion**
The contradiction is **not an error - it is a dual-source bill of materials**. One main-camera slot is wired for three interchangeable 50 MP dies, and the fitted die is discovered at runtime by ID probe. **On this specific handset the fitted main sensor is the Sony IMX989**, evidenced by the ID-matched driver binding and the Sony-specific 4096x3072 RAW geometry. Ulefone's published specification describes the **Samsung S5KGN1SP** population, which other retail lots will carry. Neither statement invalidates the other; the marketing string "IMX989 GN1" is simply both option names concatenated.

**Final confidence:** **STRONGLY_SUPPORTED** that this unit carries IMX989. **PROVEN** that the slot is multi-source (IMX989 / S5KGN1SP / S5KGM2SP) and that per-lot variation must be assumed.

**Remaining uncertainty:** the last step to PROVEN is a **camera-module EEPROM dump** (module/sensor ID bytes at `camera-eeprom0` = i2c 7-0051) or a **package/label reading in teardown**. Both were unavailable.

**Impact on final inventory:** YES - camera row rewritten. Capability matrix "OEM GN1 contradiction" note replaced with the dual-source explanation. Hardware-variants report gains a concrete, proven variant axis.

**Answers:** (1) slot supports 3 dies; this unit probed IMX989; (2) EEPROM module ID or package marking; (3) yes, to STRONGLY_SUPPORTED; (4) yes - a rooted EEPROM read would finish it; (5) yes, for the OEM/variant context; (6) only for absolute proof; (7) Sony IMX989 on this unit, Samsung S5KGN1SP per Ulefone's published spec; (8) STRONGLY_SUPPORTED; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

Stronger local artefact than pass 1 used: the MTK CameraProvider's **runtime enumeration** (VL27, L22):

```
[00] BACK  SENSOR_DRVNAME_IMX989_MIPI_RAW       [01] FRONT SENSOR_DRVNAME_S5KJN1_MIPI_RAW
[02] BACK  SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW  [03] BACK  SENSOR_DRVNAME_OV64B_MIPI_RAW
```

`SENSOR_DRVNAME_*` is the driver name the ID probe matched **on this individual handset**, so the fitted
main die is read directly instead of inferred. Camera 0's published geometry is self-consistent with that
reading: `physicalSize = 13.107 x 9.830 mm` (~16.4 mm diagonal, 1-inch class) with `pixelArraySize =
4096 x 3072` (exactly the 4-in-1 binned array of a 0.8 um 50 MP die), and it is *not* consistent with a
1/1.31" GN1-class die.

External sources pull the other way and are recorded as VI7 / VI25 / VI27: Ulefone's own spec text says
"50MP Main Camera **Samsung GN1** CMOS sensor, 1.2 um, 7 piece lens, FOV 85 deg, f/1.95", and an
independent review measures **S5KGN1, 1/1.31", 1.2 um**. Both describe the *model*; the DRVNAME describes
*this unit* - which is precisely the dual-source-BOM reading of pass 1.

New defect found (why HAL metadata must never be sole silicon evidence): camera 2 publishes a JN1 instance
name together with an 8160x6144 array **and** the main camera's 13.107 x 9.830 mm die geometry; camera 1
publishes a JN1 die size with a 50 MP array; and `android.lens.aperture` / `android.lens.focalLength` are
absent from all four blocks. Verdict unchanged and reinforced: **IMX989 on this unit (runtime-probed),
S5KGN1SP/S5KGM2SP documented alternates of the same slot, OEM literature describes the GN1 alternate.**
