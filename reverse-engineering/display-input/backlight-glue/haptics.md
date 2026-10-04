# Haptics — kernel closure

- **Hardware:** an ERM motor (inferred: DC drive only) on the MT6369 `VIBR` LDO
  (`vib-supply = <&mt6369_vibr>`), window 2.2–3.5 V
  (`min-volt 0x2191c0`, `max-volt 0x3567e0`). There is no haptic IC on any bus.
- **Kernel:** `regulator-vibrator.ko` (vendor ramdisk,
  sha256 `13b4903d…`).
  - A vs B: **9/9 functions, 15/15 data, 18/18 imports, 6/6 modinfo;
    section-equal except build-id; B1==B2.**
  - Source: MTK `4d63addd35a4` with code unchanged, plus 27 non-code lines
    (layout delta, KDM ef13d89).
- **Interface:** LED class device `vibrator` with the GKI built-in
  `ledtrig-transient` (`CONFIG_LEDS_TRIGGER_TRANSIENT=y`). `init.rc` writes
  `trigger=transient` and chowns `activate`/`duration`/`state`/`brightness`.
- **HAL:** `android.hardware.vibrator-service.mediatek` (AIDL V2) uses
  `/sys/class/leds/vibrator/{activate,duration,state}` ("Vibrator using LED
  trigger"). Capabilities 0, effects CLICK/DOUBLE_CLICK/TICK/HEAVY_CLICK/
  TEXTURE_TICK (all timed on/off), no primitives or amplitude control.
- **HAPTICS-TUNING/FIRMWARE:** none exists. There is no waveform library, no
  firmware, no calibration (`aw_vibrator` paths in init.yft.rc are dead
  template lines).
- Remaining: motor part number (teardown) and runtime drive profile.
