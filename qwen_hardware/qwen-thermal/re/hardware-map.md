# Thermal hardware map

```text
MT6878 Android userspace
  M170infisens / M170infDlp / FactoryMode
    AC020 Java/JNI + native InfiRay SDK
      /dev/bus/usb/* -> internal USB2 UVC device
MT6375 / extcon USB role-routing glue
  /sys/class/yft_extcon/tiny2c_mode
YFT tiny2c power/presence driver
  /sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode
  /sys/devices/platform/yft_tiny2c_usb/sensor_id
  four GPIO enables: 1.8 V, 3.3 V, 5 V, 3.3 V I/O
  I2C8 @ 0x3c presence/chip-ID read; expected stock-test ID 0x4c59
InfiRay/InfiSense module
  AC020-class processing/command/USB bridge
  uncooled LWIR detector + shutter + lens + module flash/calibration
  UVC video/radiometric stream + vendor control transfers
```

The DT child is named `fm78100@0x3c` but binds `mediatek,tiny2c_usb` / `tiny2c_usb-sensor`; it is power/presence glue, not the thermal image sensor data path. FactoryMode requires `sensor_id` to equal `0x4c59` before enabling Pass. SCL/SDA are GPIO IDs 141/142. Rail phandle values recovered: 1v8=192, 3v3=191, io3v3=149; 5v exists but its numeric phandle was not recovered in current snapshot.

Marketing/prior-research identity is InfiRay Mini640-class, 640x512, 12 um, radiometric 25 Hz, AC020, branded ThermoVue T2. Static software also contains 256x192/384-line Eco/factory paths and many donor families. Therefore 640x512 is STRONGLY_SUPPORTED by product evidence, not proven by a live descriptor or frame from this unit.


## Correction (2026-10-06, `reverse-engineering/thermal-camera/`)

- The module is a Raytron/InfiRay **Tiny2-C (TC2-C), native 256×192**: M170infDlp ships
  `RS300_TC2C_…whole_package…zip` whose `whole_package.json` says `"device_name":"TINY2-C"`;
  M170infDlp `IR_SENSOR_WIDTH/HEIGHT = 256/386`; USB identity 3474:4321 equals the public
  Tiny2-C/TC001 descriptor (YUY2 256×194 / 256×386 @25 Hz). **640×512 is the marketing output
  after the app's `MNN_SR_TINY2C` super-resolution; native 640×512 is retracted.**
- `tiny2c_usb_vdd_5v` is not "unrecovered": the property is absent from the GQ5012BF1 DT.
- 8-003c ID value is known: `0x4c59` (reg 0x0001=0x4c, reg 0x0000=0x59).
- GPIO 55/152/28 belong to the uSmart accessory path, not to the thermal camera.
