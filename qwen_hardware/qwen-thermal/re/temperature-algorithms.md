# Temperature algorithms

1. UVC delivers a detector/intensity plane and/or module temperature plane.
2. Gain-specific K/B calibration linearizes pixels; DPC/RMVC, B/OOC and NUC-T remove fixed pattern, defects and temperature drift.
3. KT/BT and NUC factors produce corrected absolute-temperature codes.
4. Emissivity, atmospheric transmission, ambient/reflected temperatures, humidity and distance create environment coefficients and final compensation.
5. The output plane is unsigned LE16 in 1/64 kelvin for the classic 256/384 path.
6. Point/line/rect/circle/global reducers return min/max/average and extrema coordinates; Java converts to Celsius.

Exact display formula: `C = raw/64.0 - 273.15`. Exact physical internals are represented by native functions (`calculate_tau`, `calculate_KE_and_BE`, `temp_correct`, distance/emissivity tables, reverse correction) but their polynomial constants/scales are not asserted without code decompilation or controlled calibration targets.
