# Evidence

Primary artifacts. Every claim in `../reports/` and `../docs/` should be
traceable to something here or to the (gitignored) `../workspace/`.

```text
boot-hang-2026-08-29/   the boot-stall investigation: PID-1 capture harness
                        sources, on-device diagnostic records, the SELinux
                        policy hash mismatch, pstore results, AVB contract
bootloader/             fastboot getvar dump (slots, partition sizes, unlock
                        state, bootloader version)
stock-images/           unpack_bootimg reconstruction arguments for the stock
                        boot / init_boot / vendor_boot images
trustkernel/            TrustKernel service inventory in Android vs recovery,
                        with the diff that drove the recovery TEE bring-up
hw-tests/               on-device recovery test captures
  build13-usb-teardown/   the ~3 s USB gadget teardown: every capture failed,
                          the 32-byte files are the error messages themselves
  build14-touch-usb/      first successful capture pass (dmesg, logcat,
                          modules, input bindings, slot state, SHA256SUMS)
  live-recovery-working/  a known-good recovery boot for comparison
```

## Not kept here

| Artifact | Where | Why |
|---|---|---|
| Stock TrustKernel trusted applications (`t6/*.ta`) and the encrypted keybox blobs under `t6/data/` | local only | proprietary vendor code and **per-device attestation key material** — must not be published |
| OrangeFox build outputs (~4 GB) | OrangeFox repository releases | build products |
| Stock partition images, live snapshots, extracted firmware (7.2 GB) | `../workspace/` | large, gitignored, contains vendor binaries |
| Raw pstore / expdb / metadata partition dumps (336 MB) | `../../evidence/device-dumps-20260829/` | device-state snapshots, too large to publish |

## Provenance note

The live snapshots were captured on a KernelSU-patched device with a property
spoofing module active. `../tools/snapshot_trust.py` classifies what each
snapshot may still be trusted for; identity, version and attestation
properties from them are **not** authoritative. Hardware topology is.
