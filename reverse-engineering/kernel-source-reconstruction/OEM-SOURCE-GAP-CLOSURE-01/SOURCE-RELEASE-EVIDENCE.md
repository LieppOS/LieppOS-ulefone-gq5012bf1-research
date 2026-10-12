# Source-release evidence

## Licence facts, read directly from each shipped module's `.modinfo` (read-only)

The full table, for all 37 uncertified identities, is in `evidence/STOCK-MODINFO.tsv` (filename, class, sha256,
license, author, description, version).

| licence (`.modinfo`) | Count | Modules |
|---|---:|---|
| `GPL` / `GPL v2` | 35 | all C and G rows, plus `flashlight` (D) |
| `Proprietary` | 2 | `fpsgo`, `msync2_frd` (D) |

## Also verified

- **Public TrustKernel headers:** the 4.0p0 and 7:2.2 files state "This program is free software; you can
  redistribute it and/or modify it under the terms of the GNU General Public License version 2"
  (`evidence/trustkernel/anvil-4.0p0/`).
- **Stock firmware identity:** `GQ5012BF1_EEA_V15`, fingerprint
  `Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274:user/release-keys`, kernel
  `6.1.115-android14-11-g945dff7bc1bf`.

## Not established, so not claimed

- **Distribution terms:** whether Ulefone published a written offer, and in which channel, was not checked here.
  Before sending, the user should check the device box/manual and Ulefone's website for an existing GPL source
  offer or download.
- **Legal entitlement:** no legal conclusion is drawn. The drafts ask for the source corresponding to the GPL-
  licensed binaries and cite the binaries' own licence strings.
- **Proprietary-licensed modules:** no obligation is inferred for `fpsgo` and `msync2_frd`.
- **Out of scope:** secure-world, firmware and TA components are excluded entirely.

## Public material already checked (insufficient for byte parity)

- **Pinned trees:** MediaTek ALPS `5e415e05`, NothingOSS device_modules `957dac18` and kernel_modules `5f75a3b1`,
  GKI `6b18f0b5` / build 12901745.
- **TrustKernel:** 3.2p3 (ZTE), 3.2p8 (Vivo Y21s/V23 5G), 4.0p0 (anvil-kernel 4.19 `492dbcf3`, new this session),
  7:2.2 (anvil-kernel `8e1a0f39`).
- **SouthChip SC8541:** LKML 2025-10-13.
- **OPLUS SC8571:** LineageOS sm8550-modules.
- **WL286x drivers:** Sony, OnePlus, MiCode, Motorola.
- **Other:** MiCode/Transsion/Motorola searches recorded in the historical packages.
