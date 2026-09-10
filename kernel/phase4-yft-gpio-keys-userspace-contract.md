# yft_gpio_keys userspace contract

## Keylayout

No device-specific `.kl` exists for input name `yft-gpio-keys`; Android falls back to stock `system/usr/keylayout/Generic.kl`:

```text
key 59    F1
key 60    F2
```

Thus Linux `KEY_F1`/`KEY_F2` become Android `KEYCODE_F1` (131) and `KEYCODE_F2` (132). No IDC override for this device was found.

## Framework policy consumer

Stock `services.jar`, decompiled class `com.android.server.policy.YftPhoneWindowManager`, installs both keycodes in its before-queueing and before-dispatching function maps:

- 131 -> `QUEUEING_FUN_KEYCODE_F1` and `DISPATCHING_FUN_KEYCODE_F1`;
- 132 -> `QUEUEING_FUN_KEYCODE_F2` and `DISPATCHING_FUN_KEYCODE_F2`.

GQ5012BF1 stock resources/properties establish:

- `ro.yft_smart_key=1`;
- `ro.yft_support_tinylcd=1`;
- `yft_config_smartkey_mini=true`;
- `yft_config_f1_as_wakeup_key=false`;
- `yft_config_f1_wakeup_screen_for_sos=true`;
- `yft_config_f2_long_press_opensos=false`;
- `yft_config_support_f2_camera=false`;
- `ro.yft_control_camping` absent/default 0.

The F1 queue handler may wake the mini display when `smart_key_one_value=9`, and under the enabled SOS-wakeup configuration acquires the `KeyF1` wake lock on key down and consumes according to policy. Its dispatch handler contains settings/product-dependent smart-key paths including PTT broadcasts and scanner/customer branches. The F2 queue handler conditionally takes `KeySmartF2` for the SOS/smart-key configuration; its dispatch handler contains optional SOS, camera, projector and smart-key branches.

These high-level actions depend on Settings.Global/user selection and product properties. The static stock corpus does not justify claiming one immutable marketing action (camera/PTT/flashlight/SOS) for either key. What is exact is the handoff: F1/F2 Android keycodes enter YFT policy, where long/multi-press/action selection is implemented. None of that logic exists in `yft_gpio_keys.ko`.

Factory policy also recognizes keycodes 131 and 132 during its explicit factory key-test mode. Searches of stock keylayouts, IDC, overlays, Settings/SystemUI/vendor files and framework policy found no remapping before Generic.kl.
