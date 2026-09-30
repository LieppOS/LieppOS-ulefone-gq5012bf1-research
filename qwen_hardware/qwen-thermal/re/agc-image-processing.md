# AGC and image-processing pipeline

The stock ISP JSON and `AdvStreamSourceMode` independently expose this pipeline:

```text
IR/raw -> KBC -> TNR -> HBC/DPC -> VBC -> SNR -> DDE -> AGC -> gamma -> TPD -> mirror/flip -> picture
```

The bundled `isp_switch.json` enables KBC, DPC, RMVC, HBC, VBC, TNR, GPU SNR3, AGC, DDE, BC, TEMP_DEAL, KTBT, NUCT and second correction/calibration. Zoom/transform/crop and ISP pseudo-color are disabled in that profile, not absent from the SDK.

Key ISP controls and exact symbols include TNR, DDE, edge enhancement, gamma, brightness/contrast, spatial-noise reduction, horizontal/vertical band correction, DPC, RMVC-over-temperature, source-stage taps, mirror/flip, zoom, cursor, ISO-line, image detail and AGC source/output modes. `FrameOutputFormat` allows YUYV, NV12, NV12+temperature and YUYV+temperature.

`isp_H.json`/`isp_L.json` provide separate high/low gain profiles. Verified parameters include 32-frame K calibration; B calibration waiting 8 shutter frames and averaging 8; DPC delta threshold 2000 with median/mean filtering; KTBT compensation factor 0.216; RMVC filtering; HBC/VBC thresholds; and TNR min/max deltas and gains. These constants describe the bundled generic profile, not guaranteed per-unit values.

AGC maps corrected high-bit-depth thermal intensity into display luminance. Palette rendering is downstream unless ISP `PSEUDO` is enabled. LieppOS should consume the corrected uint16 plane for measurement and derive a separate display plane, never measure palette RGB values.
