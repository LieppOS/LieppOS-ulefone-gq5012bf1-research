# Stock application behavior

## M170infisens
User thermal application built around the InfiRay `com.energy.ac020library`, UVC camera, common processing, radiometry, dual module and image/JPEG metadata libraries. Platform identity defaults to `TC2C`. The SDK bundle is multi-product: TC2C, WN2256/2384/2640, X2Pro, X3, P2L and GL1280, plus USB/SPI/MIPI/dual/omni drivers.

## M170infDlp
Factory/SOP calibration application (`com.energy.tc2c.sop` code). It contains high/low K, high/low temperature, lid/RMVC and dual-correction step handlers, firmware update manager, UVC dual/native-camera manager and MNN libraries. Exact constants: IR width 256, stream height 386, metadata line height 2, 25 fps, 13 K-calibration captures, 16 autofocus control passes and shutter wait bounds 8..40 frames. Test frames are 256x192x16-bit. This demonstrates manufacturing/calibration tooling, not necessarily the user-app shipping resolution.

## FactoryMode
- `InfiraySmtTest` reads `/sys/devices/platform/yft_tiny2c_usb/sensor_id`; expected ID is exactly `0x4c59`.
- `InfirayEcoTest` writes 1 to platform power and extcon route nodes, registers USBMonitor, opens 256x384 @25 fps `YUYV_AND_TEMP_OUTPUT`, initializes process/parse/temp libs, then reads `secd_cali_data/manufacturer_temporary_data.bin`. At least 192 bytes and byte 0==1 are required for calibrated status.
- Preview launches `com.energy.tc2c/com.energy.usbCamera.ui.splash.SplashActivity` when the M190-style resource flag is true, otherwise `com.infisense.eco/...SplashActivity`.
- Cleanup unregisters USB and writes 0 to both nodes.

## Exposed versus bundled
The user app exposes preview, palettes, measurements, media capture/album and temperature settings. Native SDK additionally carries file/flash, firmware, raw stage taps, detailed calibration, DPC/RMVC, manual gain/FFC, environment tables, diagnostics, dual fusion and factory procedures. Shipping a library is not proof the module supports every call.
