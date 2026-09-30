# Radiometry

## Proven sample representation
`LibIRTemp(int width,int height)` allocates `width*height*2` bytes and stores the radiometric plane in `tempData`. Its region/point helpers return Java `char` samples (unsigned 16-bit). The stock wrapper uses `scale=64` and converts:

```text
T_C = uint16_le_sample / 64.0 - 273.15
```

This exact formula appears in `getTemperatureOfPoint`, `getTemperatureOfLine`, `getTemperatureOfRect`, `getTemperatureOfCircle` and whole-frame min/max/average. The independently reversed P2 Pro donor uses the same 1/64 K representation, corroborating the family convention.

## Frame organization
FactoryMode constructs a USB handle at 25 fps, width 256, height 384, `YUYV_AND_TEMP_OUTPUT`. This is consistent with a 256x192 YUYV image plane plus a 256x192 little-endian uint16 temperature plane. It is exact for the `InfirayEcoTest` path, but is not proof that the marketed 640x512 module uses this geometry. The SDK also has WN640/384 modes and distinct `get_tempinfo_wn640_v2` processing.

## Environmental correction architecture
`LibIRTemp` and `libadvirtempac020.so` expose exact symbols/classes for:
- `EnvParam_t`: `EMS`, `TAU`, `Ta`, `Tu` (fixed-point integers in Java ABI; native scaling not fully recovered).
- `EnvFactor_t`: `K_E`, `B_E`.
- `NucFactor_t`: `P0`, `P1`, `P2`.
- calibration factors `Kn/Bn`, recalibration `K/B`, calibration points `TH/TL`.
- `calculate_tau`, vapor-pressure/humidity lookup, distance table generation, emissivity tables, `calc_env_factor_with_dist_and_env_temp`, `calculate_KE_and_BE`, `calculate_new_KE_and_BE_with_nuc_t`, `temp_correct`, reverse correction and enhanced distance correction.

The architecture is therefore: corrected detector code -> high/low gain KT/BT and NUC-T table -> environment coefficient from emissivity/transmission/reflected/background temperature, humidity and distance -> corrected absolute-temperature plane. Exact internal polynomial/scaling constants are not claimed without native decompilation or controlled observations.

## Measurement engine
Native exact symbols cover point, line, horizontal/vertical/slope line, rectangle and circle min/max/average, coordinates of extrema, global frame measurement and hot/cold threshold alarms. `setSideLength` accepts 3..15 for neighborhood-based point measurement. Java result type carries min/max/average Celsius plus min/max pixel coordinates.

## Gain behavior
`gain_switch_detect` scans every LE16 sample. Pixel proportions above/below configured thresholds drive debounce counters; after `switch_frame_cnt`, callback requests low/high gain and suppresses further switching for `waiting_frame_cnt`. Overexposure avoidance similarly uses gain-specific thresholds, pixel proportion, switch debounce and delayed close. These are SDK features even if not all are exposed by Ulefone UI.
