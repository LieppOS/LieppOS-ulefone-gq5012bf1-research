# LieppOS thermal integration

Preferred near-term strategy is hybrid: preserve/reuse the signed stock SDK for calibration/radiometry while placing power, USB lifecycle and access policy behind a narrow privileged Binder service. UI receives separate image and radiometric planes. Host-side palettes and measurement tools are safe replacements; firmware, raw flash and calibration writes remain disabled.

Backup first: runtime `/mnt/vendor/nvcfg/infiray` if present, read-only module files, module identity/serial/config, all stock APKs/libs, hashes, permissions and SELinux labels. Validate against stock and controlled references before replacing native correction. See `../re/lieppos-integration-design.md`.
