# Hynitron exact-GKI build

Workspace: `/home/armol/kernel-work/gki-12901745-workspace`
Target: `//lieppos/hynitron-recon:hynitron_recon`
Kernel: `//common:kernel_aarch64`, Linux 6.1.115-android14-11, CI 12901745.

Command: `./tools/bazel build //lieppos/hynitron-recon:hynitron_recon`

- BUILD_RC: **0**
- compiler warnings: **0**
- modpost warnings: **0**
- unresolved symbols: **0** (`*.check_no_remaining` passed)
- module: `workspace/phase4-hynitron/rebuild/hynitron.ko`
- SHA256: `26522dc090fc6a57cf45ed841755a8ef267c83f43f511433439f1392e2ba438a`

Kleaf's sign-file emitted expected missing-development-key SSL diagnostics; it
falls back to unsigned external-module output and they are neither compiler nor
modpost warnings. The build uses
`workspace/phase4-hynitron/oracle/stock-yft-devinfo.symvers` as the explicitly
required real stock-provider ABI witness. It does not use reconstructed
yft_devinfo and performs no CRC/ELF patching.
