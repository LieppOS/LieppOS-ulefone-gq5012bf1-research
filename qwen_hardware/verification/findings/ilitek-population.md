# U13 - is Ilitek `0-0041` physically populated?

**Current claim:** "driver binding, no consumer classification".

**Previous confidence:** UNKNOWN.

**New evidence**
1. **The three I2C touch clients on bus 0 are mutually exclusive alternates for the *main* panel, not for the rear one.**
   | Node | Compatible | IRQ GPIO | Reset GPIO | Resolution hint |
   |---|---|---|---|---|
   | `focaltech@39` (on **spi3**) | `focaltech,fts` | 7 | 6 | `display-coords = <0 0 1080 2400>`, 10 touch |
   | `ilitek@41` (i2c-0) | `tchip,ilitek` | **7** | **6** | - |
   | `chipone_tddi@48` (i2c-0) | `chipone-tddi` | **7** | **6** | `x-res = 1080`, `y-res = 2460` |
   | `hynitron@15` (i2c-0) | `hynitron,hyn_ts` | 11 | 32 | `display-coords = <340 340>`, **1** touch |
   Ilitek and ChipOne share **exactly the same interrupt and reset lines** as the FocalTech main-panel controller and describe a 1080-wide main panel. They are alternate-vendor options for the same panel position; they are not the rear digitizer (that is Hynitron, at 340x340 single-touch).
2. **Only FocalTech and Hynitron actually bound.** From `buses.txt`, `0-0015` resolves to `/sys/bus/i2c/drivers/hyn_ts` with `/sys/module/hynitron`, and `spi3.0` resolves to `/sys/bus/spi/drivers/fts_ts` with `/sys/module/focaltech_touch_spi_ft3680`. For `0-0041` and `0-0048` the `driver` symlink is **unresolved** - no driver claimed them.
3. **No Ilitek or ChipOne driver is shipped at all.** `vendor_dlkm/lib/modules/` contains `focaltech_touch_spi_ft3680.ko`, `hynitron.ko`, `spi_tiny_co5300_lcd.ko` and 212 other modules, but **no `ilitek.ko` and no `chipone*.ko`**. A part that has no driver in the image cannot be the shipped configuration.
4. `/sys/hynitron_debug/` exists on the live device with `hyntpfwver`, `hynfwupdate`, `hyntpfactorytest`, `hyn_gesture_mode` - the Hynitron path is fully alive.

**Contradicting evidence**
An unbound I2C client alone is weak evidence of absence: `5-0018` (RT5133) is also unbound in the same dump yet is certainly present, because it is served through a different (MFD/regulator) registration path. The decisive additions here are the **shared IRQ/reset pins** and the **absence of any shipped driver**.

**Internet sources:** none required.

**Local evidence:** VL13, VL14, VL15.

**Read-only live evidence:** bus/driver binding table and module inventory from the frozen capture.

**Final conclusion**
**Ilitek `0-0041` and ChipOne-TDDI `0-0048` are unpopulated alternate-vendor device-tree entries for the main touch panel.** The fitted main-panel controller is the **FocalTech FT3680 on SPI3** (10-point, 1080x2400), and the fitted secondary digitizer is the **Hynitron controller at i2c `0-0015`** driving the 340x340 rear sub-display. Because Ilitek/ChipOne would contend for the same interrupt and reset lines that FT3680 owns, they cannot be simultaneously populated in a working design.

**Final confidence:** **STRONGLY_SUPPORTED** that neither is populated; **PROVEN** that neither is usable (no driver shipped, no binding, shared pins already owned).

**Remaining uncertainty:** absolute proof of an empty footprint requires board photography. This does not affect any functional conclusion.

**Impact on final inventory:** YES - touch row rewritten: one main controller (FT3680) plus one rear controller (Hynitron); the two extra bindings are reclassified as ODM alternates rather than mysterious extra hardware.

**Answers:** (1) alternates on the main panel's pins, unbound, no driver; (2) a photograph of the footprint; (3) yes; (4) yes; (5) no; (6) only for absolute certainty; (7) not populated - FT3680 is the fitted main controller; (8) STRONGLY_SUPPORTED; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08) - method correction, verdict unchanged

`buses.txt` was generated with `readlink -f <dev>/driver`, and `readlink -f` **prints the canonical path even
when the final component does not exist**. So a block whose line still ends in `/driver` means *no driver
symlink -> not bound*, while a block resolving to `/sys/bus/<bus>/drivers/<name>` means *bound*. Re-parsing
all 53 blocks under that rule yields exactly **28 bound**, **5 unbound** (`0-0041` ilitek, `0-0048`
chipone-tddi, `5-0018` rt5133, `5-0075` + `6-0075` rt6160) and **5 `dummy` placeholder clients** (`5-001a`,
`5-003f`, `5-004a`, `5-004e`, `5-0064`) - full table in `../evidence/live-runtime-secondpass.md` (L21).
The intermediate worry that "Ilitek/ChipOne driver names appear bound" is **disproven as a parsing
artefact**; pass 1's verdict stands.

Runtime corroboration for the fitted pair: `dmesg.txt` carries `[FTS_TS/I]fts_check_fw_normal:TP Ready,
Read ID=0x56`, and `displays.txt` registers **both** `fts_ts` (`/sys/.../11013000.spi3/spi_master/spi3/
spi3.0`, classes `TOUCH|TOUCH_MT`) and `hyn_ts` (`/sys/.../11c20000.i2c/i2c-0/0-0015`, raw axes 0..340
scaled 3.1672 x 7.0381 into the 1080x2400 viewport) as live input devices (VL28).
