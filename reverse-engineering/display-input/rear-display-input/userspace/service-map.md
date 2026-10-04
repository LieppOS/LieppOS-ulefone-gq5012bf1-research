# Rear screen userspace path (stock, static)

```text
YftMiniScreen.apk (com.yft.miniscreen)           FactoryMode.apk (TinyLCDTestActivity, aging test)
   clock / camera preview / music / notifications      │ ITinylcd$Proxy (direct HIDL client)
   compass / race text / AOD selection                 │
        │ (app UI rendered on a VirtualDisplay)         │
        ▼                                               │
system_server (services.jar)                           │
   MiniScreenDisplay · VirtualDisplayAdapter ·          │
   ImageReader · writeFrameToHal · startGestureWake ·   │
   setBacklightCtrl · MiniScreenWakeLock                │
   gate: ro.yft_support_tinylcd=1                       │
        └───────────── hwbinder ───────────────────────┘
                        ▼
vendor.yft.hardware.tinylcd@1.0::ITinylcd/default
   service tinylcd_hal  /vendor/bin/hw/vendor.yft.hardware.tinylcd@1.0-service
   class late_start · user system · group system input
   proxy/stub lib: vendor/lib64/vendor.yft.hardware.tinylcd@1.0.so
                        ▼  hw_get_module("tinylcd")
vendor/lib{,64}/hw/tinylcd.default.so   ("tinylcd-hal")
   lcd_set_power · set_bl / set_backlight · wirte_frame · wirte_frame_size ·
   start_gesture · frame_status · open("dev/tiny_lcd_miscdev")
                        ▼  ioctl 0x6b37..0x6b41 (init.tinylcd.rc: chmod 0666)
/dev/tiny_lcd_miscdev → spi_tiny_co5300_lcd → (exports) → hynitron
```

## Kernel capability vs userspace feature enablement

| capability (kernel, proven) | userspace enablement (static evidence only) |
|---|---|
| full 340×340 or centred 320×320 RGB565 frame push, TE-paced or immediate | framework `writeFrameToHal`, `VirtualDisplay` + `ImageReader` path; `didFrameSizeChange` |
| controller brightness (0x51), lazily applied | `setBacklightCtrl screenBrightness`; HAL `set_backlight arg_long` |
| AOD mode (touch off, immediate frames) | HAL `TINY_LCM_IOC_POWER_AOD`; app `AodDisplaySelectActivity` |
| touch wake-gesture arm/disarm | `startGestureWake`, HAL `start_gesture` |
| frame status polling | HAL `frame_status` |

The app classes and resources show the rear-screen UI features: `ClockView`,
`SubscreenClockProvider`, camera `PreviewTextureView`/`TAKE_PHOTO`,
`MiniScreenMusic`, `CompassSelectActivity`, `RaceTextSettingsActivity`, and
notification/status help videos. These are user-facing intents and assets; no
claim is made here about their runtime behavior. The camera "preview" reaches
the panel the same way as everything else: rendered into the virtual display,
then pushed as RGB565 frames. There is no kernel camera→panel path.

The 32-bit HAL's pointer-sized ioctl encodings are not translated by the
kernel's `compat_ioctl` (see `../co5300/update-path.md`). In the 64-bit service
this is moot.
