# Stock versus hidden feature matrix

Legend: Y=yes, B=bundled SDK, U=unknown/module capture needed, N=not standard Android Camera API.

| Feature | SDK | Module | Ulefone app | Android standard | LieppOS opportunity | Confidence |
|---|---:|---:|---:|---:|---|---|
| preview | Y | Y | Y | N | system preview | proven |
| radiometry | Y | Y | Y | N | corrected plane API | proven |
| spot temperature | Y | Y | Y | N | expose | high |
| min/max/global | Y | Y | Y | N | expose markers | high |
| ROI line/rect/circle | Y | likely | B/Y | N | expose full shapes | high SDK |
| alarms | Y | likely | U | N | safe host alarm | high SDK |
| emissivity | Y | likely | Y/U exact UI | N | typed setting | high SDK |
| distance/humidity | Y | likely | U | N | expert controls | high SDK |
| reflected/ambient correction | Y | likely | U | N | expert controls | high SDK |
| palettes | Y | Y | Y | N | 11 LUTs/custom LUT | proven |
| FFC | Y | Y | automatic | N | status + guarded manual | proven |
| AGC | Y | Y | Y | N | range lock/host AGC | proven |
| gain/range modes | Y | likely | automatic | N | status + safe auto | high |
| raw/radiometric frame | Y | Y | internal | N | developer export | proven SDK |
| radiometric still/JPEG metadata | Y | likely | Y | N | open metadata export | high |
| radiometric video | Y | likely | recording code | N | sidecar/raw stream | medium |
| visible fusion/dual | Y | U on phone | calibration app | N | only if hardware proven | bundled only |
| rotation/mirror | Y | Y | likely | N | expose | high SDK |
| recording/album/PDF | B | host feature | Y/B | partial media only | retain | high |
| module diagnostics/version | Y | Y | FactoryMode | N | read-only page | proven |
| calibration status | Y | Y | FactoryMode | N | read-only integrity | proven |
| firmware update | Y | likely | SOP/factory | N | omit from normal UI | proven SDK |
| flash/raw calibration writes | Y | likely | factory only | N | prohibit | proven SDK |
