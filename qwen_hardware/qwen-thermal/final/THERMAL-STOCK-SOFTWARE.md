# Stock thermal software

`M170infisens` is the user application; `M170infDlp` is TC2C factory/SOP calibration and firmware tooling; `FactoryMode` supplies SMT ID, power, USB, preview and calibration checks. Native stack divides into AC020 JNI/DFU, ircmd/vdcmd, UVC drivers, image process/parse, radiometry, palette, dual calibration/fusion, file/package and package-signature security layers.

FactoryMode follows the authoritative lifecycle: both sysfs nodes on -> USBMonitor permission/open -> 25 fps combined stream/init -> calibration read -> USB release -> both nodes off. See `../re/stock-app-behaviour.md`, `../re/libs/native-stack.md` and `../re/security-integrity.md`.
