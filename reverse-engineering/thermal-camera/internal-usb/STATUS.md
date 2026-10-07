# INTERNAL-THERMAL-USB — STATUS (2026-10-07)

**DONE (static integration closure).** No new kernel module is owned here: every kernel
part is already byte-level closed (yft_tiny2c_usb in FM78100-COMPANION, extcon-mtk-usb,
mt6375-charger, MTU3/xHCI/PHY in the USB stack) and the userspace protocol is closed in
AC020-UVC. This component closes the *integration*: order, ownership, gates, interaction.

| DONE criterion | result |
|---|---|
| power sequencing | BOOT: rails 149→[5v absent]→191→192 on, 400 ms, ID read, rails off; RUNTIME: same rails on then `yft_usb_flag`=1; off then flag 0; no kernel delays — PROVEN |
| I2C detection | boot-only, reg 0x0000/0x0001, 0x4c59; result feeds only `sensor_id`; USB does not depend on it — PROVEN |
| host-role path | `tiny2c_mode` 1/other → HOST/NONE via extcon `update_role` + `usb_role_switch_set_role`; not flag-gated; no VBUS/GPIO side effects — PROVEN |
| enumeration | ~0.73 s after rails; 1-1, HS, 3474:4321; uvcvideo bind → usbfs `DISCONNECT_CLAIM` — PROVEN (capture + code) |
| userspace ownership | M170infisens/M170infDlp/FactoryMode via USBMonitor fd → libAC020sdk/libusbuvccamera020 — PROVEN |
| external Type-C | single fabric, last-writer role; flag suppresses external role events during the session; external role not restored after — PROVEN |
| uSmart separation | GPIO 28/55/152 + `uvc_insert_status` = uSmart only; 0 during thermal session — PROVEN |
| stream / control | EP 0x81 iso / EP0 vendor (AC020-UVC); no sysfs/ioctl/I2C/V4L2 command path — PROVEN |
| stop / disconnect / crash | stream off → rails off (disconnect) → role NONE; AMS cleanup for tc2c/sop (not FactoryMode) — PROVEN |
| firmware / calibration | none in the integration; module flash over USB (AC020-UVC) — PROVEN |

Residual, non-blocking: physical D+/D− selection element for the module (board-only,
not software-visible); stock quirks recorded (no external-role restore, FactoryMode not in
crash cleanup, `tiny2c_mode` reads 0, rails dropped before role change).
