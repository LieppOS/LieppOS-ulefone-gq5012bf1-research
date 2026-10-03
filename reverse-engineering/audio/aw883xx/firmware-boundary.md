# AW88394 firmware/tuning boundary

Kernel driver behaviour is closed independently from these data:

| item | role | status |
|---|---|---|
| `aw883xx_acf.bin` | register/profile/DSP configuration; Music and Receiver profile inventory | stock data available, acoustic source proprietary |
| `awinic_params.bin` | Awinic speaker algorithm parameters | stock 13,640-byte blob available |
| `awinic_sinwave_params.bin` | calibration/sine-wave parameters | stock 13,640-byte blob available |
| `awinic.audio.effect.so` | SKTune calibration/protection algorithm | proprietary ELF |
| `libawinicsmartpaparse.so` | ACF/parameter parser | proprietary ELF |
| `libaudiosmartpamtk.so` | MTK SmartPA/NVRAM manager | proprietary ELF |
| SmartPA NVRAM | per-unit calibrated resistance/data | inaccessible without device; must never be fabricated |

A ROM port should preserve these stock files/interfaces. Their proprietary
status is not a blocker for `AW883XX-KERNEL = DONE`.
