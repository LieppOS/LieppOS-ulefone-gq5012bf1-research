# FFC / NUC / shutter

## Recovered controls
The exact `libircmd020.so` / Java surface contains manual FFC, automatic FFC enable, automatic temperature threshold, minimum and maximum automatic intervals, all-FFC availability/cancel status, shutter-status readout and shutter-behavior selection.

Enums from `CommonParams`:
- `AutoFFCStatus`: disabled=0, enable=1.
- `AutoFFCParam`: temperature threshold=0, min interval=1, max interval=2.
- `ManualFFCSwitchStatus`: close=0, open=1.
- `ShutterStatus`: close=0, open=1, unknown=2.
- `AllFFCStatus`: available=0, unavailable=1, cancel=2.
- `FFCShutterBehaviorMode`: update B only=0, update OOC only=1, update both B and OOC=2.

## Processing role
FFC closes the internal shutter so the detector sees a spatially uniform reference. The selected behavior updates the additive B offset field, the OOC correction field, or both. NUC then applies stored per-pixel/nonuniformity terms and temperature-dependent NUC-T correction. Exact native symbols include `calculate_nuc_with_nuc_factor`, `calculate_new_KE_and_BE_with_nuc_t`, `generate_high_gain_nuc_t`, `generate_low_gain_nuc_t` and `get_NUC_value`.

## Calibration families
Separate high/low gain KT, BT and NUC-T files exist under both `default_data/` and `secd_cali_data/`. The module also stores DPC and RMVC data. These data are gain-specific and must remain paired with the detector/module.

## Safety
Do not force shutter cycles, alter FFC cadence, clear DPC/RMVC, or write calibration blobs on a production module without backups and explicit authorization. The current work performed no active USB commands.
