# PL/LK reset-signature comparison

Historical Phase-5 PL/LK captures were compared across:

- deferred MTK evidence
- post-lk_b attempt
- post-live-LK attempt
- final post-firmware attempt that reached USB PID 0x201C

## Common non-discriminating state

The captures repeatedly contain:

- `aee exception info exp_type: 0x0`
- initial `aee exception info wdt_status: 0x800`
- `kedump: last is full pmic reset!`
- `kedump: normal flow`
- `kpoc_check, charger_boot_switch = 0`
- LK boot mode 0
- `/watchdog` DT lookup warnings

These signatures therefore do not distinguish the Slot-B failure from other
boot/recovery sequences and are not currently useful as root-cause evidence.

## Unique post-live-LK retained record

The post-live-LK capture uniquely found retained expdb data and restored:

`wdt_status = 0x2`

with:

`rc_wdt_status = 2`
`rc_exp_type = 0`

The later final post-firmware attempt that reached PID 0x201C does not contain
this expdb restore sequence or restored status 0x2.

Therefore the status-2 record is treated as historical/persisted evidence from
an earlier event, not proof that the final post-firmware reset was caused by a
watchdog.

## Boot-reason records

Historical fallback captures contain only generic recovery-path values such as:

- `reboot`
- `bootloader`
- boot-device strings

They do not identify the original Android-side cause of the Slot-B reset.

## Next boundary

The investigation should move to second-stage Android reset/reboot authority:
init fatal handling, `sys.powerctl`, explicit reboot/shutdown triggers, critical
service crash policy, SELinux transition failures, apexd/vold failures, and
MediaTek userspace watchdog/reset services.
