# INTERNAL-THERMAL-USB vs uSmart accessory path

| signal / object | uSmart accessory (rear accessory connector) | internal thermal camera |
|---|---|---|
| presence | GPIO 28 `id-gpios` (both-edge IRQ `extcon-usb`, LOW = inserted) → `mtk_usb_extcon_detect_cable` / boot `id_pin_init` | boot I2C ID 8-003c (`sensor_id`); at runtime the app relies on USB attach |
| power | GPIO 152 `uvc_vbus_gpio` (accessory VBUS) | GPIO 149 / 191 / 192 (`tiny2c_usb_mode`) |
| D+/D− route | GPIO 55 `uvc_switch_gpio` | no GPIO (board routing) |
| status node | `uvc_insert_status` (1 while inserted) | none (`tiny2c_mode` reads 0) |
| role trigger | extcon detect work → HOST / NONE (gated by `yft_usb_flag`, except the boot-time check) | `tiny2c_mode` store → HOST / NONE (not gated) |
| driver | extcon-mtk-usb only | yft_tiny2c_usb (power, ID) + extcon-mtk-usb (`tiny2c_mode`) |
| userspace | YftSystemUI (reads `uvc_insert_status`), uSmart camera apps | M170infisens / M170infDlp / FactoryMode, services.jar cleanup |

Proof that GPIO 55/152 are not thermal controls: they are written only in
`detect_cable`/`id_pin_init` (GPIO 28 path) and in probe (output 0); `uvc_insert_status`
is set together with them; in the captured thermal session `uvc_insert_status=0` (so both
GPIOs were 0) while `3474:4321` streamed. Shared resources: the same MTU3/xHCI/PHY and
role switch, and `yft_usb_flag` (an inserted uSmart accessory is ignored while the
thermal flag is 1). uSmart itself is not reverse-engineered here
(`kernel/usmart-full-contract.md`).
