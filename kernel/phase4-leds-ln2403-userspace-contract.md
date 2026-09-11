# LN2403 userspace contract

## Camping-light app

Stock `YftOutdoorLightUlefone.apk` (`com.yft.lamp`) reads/writes
`/sys/devices/platform/yft_camplight/camplight_mode` and
`camplight_set_brightness`. `LampBrightController` maps app modes SOS→`5`,
SUPER→`4`, ALWAYS→`2`; LIGHTING writes seekbar values to brightness. Shutdown,
timeout and receiver paths write mode 0 and brightness 0. Selectable auto-off
periods are 5, 10, 20 and 30 minutes, with `-1` as no timeout; Handler and exact
elapsed-realtime AlarmManager paths both enforce closure. Default is 5 minutes.

The app—not the kernel—limits repeated >90 seekbar use: it records a high-use
time and requires a 10-minute interval, presenting a warning dialog otherwise.
It also presents a low-power warning. These checks can be bypassed by another
writer and therefore are policy, not driver safety properties.

## Red/blue app

Stock `com.yft.redbluelight` writes
`/sys/devices/platform/yft_camplight/leds_ctl`. Its service maps blue flash→5,
red flash→4, alternating red/blue→6, red→1, blue→2, both→3, off→0. It commonly
queues an explicit 0 before a nonzero transition and shuts down to 0 on its
service/broadcast lifecycle. Sound playback is independent userspace behavior.

## Framework and policy

`YftPowerSavingSwitchService` is gated by `ro.yft_custom_camping=1`. When power
saving is enabled it reads the two camping files and writes 0 to any active
mode/brightness. Stock SELinux maps all three canonical nodes to `sysfs_yft_file`, and
`init.yft.rc` chmods all three 0777; policy grants intended system/YFT clients
access. An additional chmod containing `soc:gftk_camplight` is a legacy path and
is not used by these clients.

No userspace component supplies waveform timings, GPIOs, pinctrl states, PWM
channel or register fields. Those are kernel ABI. Conversely auto-off, high-use
cooldown, low-battery UI, notifications and sound are userspace-only and are not
to be invented in the module.
