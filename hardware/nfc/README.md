# NFC research — STMicro ST21NFC

This directory tracks reverse engineering of the NFC subsystem on the Ulefone Armor 29 Pro Thermal (`GQ5012BF1`).

The current target is the STMicroelectronics `st21nfc` NFC controller stack and its Android/NCI/Secure-Element integration.

## Files

- [`st21nfc-current-findings.md`](st21nfc-current-findings.md) — evidence-backed hardware/software findings from live ADB and vendor configuration.
- [`phase1-st21nfc-reconstruction.md`](phase1-st21nfc-reconstruction.md) — current reconstruction frontier and next research tasks.
- [`capture-commands.md`](capture-commands.md) — repeatable ADB commands for future evidence capture.

## Evidence policy

Use the following meanings throughout this directory:

- **PROVEN** — directly observed on the device or in the shipped vendor configuration.
- **SUPPORTED/CONFIGURED** — the vendor stack contains explicit support/configuration, but the complete runtime path has not yet been demonstrated.
- **INFERRED** — consistent with the evidence but still requires a direct test.
- **UNKNOWN** — not established yet.

Do not treat generic ST21 driver capability, comments in configuration files, or Android feature declarations as proof that a specific secure element, low-level emulation mode, or card protocol is physically usable on this handset.
