# Thermal data path

```
Tiny2-C module (LWIR 256×192, shutter, flash)  — powered by GPIO 149/191/192
  └─ USB2 HS device 3474:4321 on xHCI 11200000 root port 1-1 (host role via extcon tiny2c_mode)
       ├─ kernel: GKI built-in uvcvideo binds at enumeration (Found UVC 1.10 …)
       └─ Android UsbHostManager → USBMonitor (app, permission) → fd
            └─ libusbuvccamera020.so (bundled libusb/libuvc, android_usbfs)
                 detach uvcvideo, claim if0 (VC) + if1 (VS), set alt 1,
                 iso IN 0x81 → YUY2 256×386 @25 Hz (image + Y16 temperature + 2 meta lines)
                 control EP0: UVC probe/commit + vendor vdcmd (vendor-control.md)
            └─ libircmd020.so (vdcmd command layer), libAC020sdk.so (JNI, DFU)
            └─ libadvirparse / libadvirprocess / libadvirtempac020 / libcommonsdk (frame parse, radiometry)
            └─ libmnnmodel.so MNN_SR_TINY2C (super-resolution), libcolormapping, fusion libs
  └─ apps: M170infisens (com.energy.tc2c), M170infDlp (com.energy.tc2c.sop), FactoryMode
```

V4L2 is not on the stock path. `libjni_deviceAsWebcam.so` (`/dev/video*`) is the Android
webcam-gadget feature, unrelated.
