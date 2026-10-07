# INTERNAL-THERMAL-USB — internal Tiny2-C USB integration (GQ5012BF1)

**DONE (static).** GPIO 149 → 191 → 192 power the Tiny2-C module (`tiny2c_usb_mode`=1, then
`yft_usb_flag`=1); at boot the same rails are pulsed for a one-time 400 ms + I2C ID read at
8-003c (0x4c59) and switched off again; at runtime `tiny2c_mode`=1 queues USB role HOST in
`extcon-mtk-usb` → MTU3 registers xHCI 11200000 → after ~0.73 s `3474:4321` enumerates at
480 Mbit/s directly on root port `1-1` → built-in `uvcvideo` binds, then the app's bundled
libusb detaches it and claims both interfaces over usbfs; stream on iso EP 0x81, control on
EP0 vendor requests (AC020-UVC). Stop = stream off, rails off (device disconnect, flag 0),
role NONE. GPIO 55/152 are the uSmart accessory path; the module gets no Type-C VBUS.

| file | content |
|---|---|
| `hardware-path.md` | module → PHY → MTU3 → xHCI → 1-1; no thermal mux GPIO; VBUS |
| `power-sequence.md` | BOOT detection vs RUNTIME start/stop, exact order, delays, owners, crash cleanup |
| `role-switch.md` | `tiny2c_mode` → extcon → role switch; `yft_usb_flag` gates |
| `enumeration.md` | timing, uvcvideo bind, app discovery/wait/timeouts, usbfs claim |
| `userspace-path.md` | ownership chain (references AC020-UVC for protocol) |
| `userspace-control-interface.tsv` | every thermal-related sysfs node: path, modes, semantics, callers |
| `external-usb-interaction.md` | Type-C contention / arbitration |
| `usmart-boundary.md` | separation from the uSmart accessory path |
| `failure-semantics.md` | static failure behaviour |
| `firmware-calibration-boundary.md` | references AC020-UVC / FM78100 |
| `source-boundary.md` | which (already closed) source owns each part |
| `stale-claims.md` | 13 corrections |

Related: `../ac020/` (AC020-UVC, DONE), `../fm78100/` (FM78100-COMPANION, DONE),
`../../usb/` (USB kernel stack, EXTCON-MTK-USB, DONE), `usb-research/USB-INTERNAL-THERMAL-CAMERA.md`
(original runtime capture note).
